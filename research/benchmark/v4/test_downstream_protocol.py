"""Regression tests for downstream-only judge and preparation contracts."""
import unittest

try:
    import downstream_protocol as protocol
except ModuleNotFoundError:
    protocol = None


HEADER = '| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta (B - A) | Evidence |'
SEPARATOR = '| :--- | :---: | :---: | :---: | :--- |'
ROWS = [
    '| Accuracy | 5 | 5 | 0 | correct |',
    '| Completeness | 4 | 5 | 1 | complete |',
    '| Structure | 5 | 5 | 0 | usable |',
    '| Actionability | 4 | 5 | 1 | useful |',
    '| Traceability | 2 | 2 | 0 | trace |',
]


def table(rows=ROWS):
    return '\n'.join([HEADER, SEPARATOR, *rows, '| **TOTAL (/25)** | 99 | 99 | 0 | ignored |'])


class JudgeProtocolTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(protocol, 'downstream judge protocol module is required')

    def test_plain_and_bold_tables_have_same_recomputed_scores(self):
        bold = [r.replace(' | 5 |', ' | **5** |').replace(' | 4 |', ' | **4** |')
                .replace(' | 2 |', ' | **2** |') for r in ROWS]
        plain = protocol.parse_judge_table(table())
        self.assertEqual(plain, protocol.parse_judge_table(table(bold)))
        self.assertEqual((plain['baseline_total'], plain['optimized_total'], plain['delta_total']),
                         (20.0, 22.0, 2.0))
        self.assertEqual(plain['winner'], 'Optimized')

    def test_duplicate_dimension_rejected(self):
        for row in [ROWS[0], '| Accuracy | 1 | 2 | 1 | conflicting |']:
            with self.subTest(row=row), self.assertRaises(protocol.ProtocolFormatError) as caught:
                protocol.parse_judge_table(table(ROWS + [row]))
            self.assertEqual(caught.exception.code, 'judge_dimension_duplicate')

    def test_multiple_rubric_tables_rejected(self):
        with self.assertRaises(protocol.ProtocolFormatError) as caught:
            protocol.parse_judge_table(table() + '\n' + table())
        self.assertEqual(caught.exception.code, 'judge_table_ambiguous')

    def test_unambiguous_unicode_range_header_is_accepted(self):
        header = HEADER.replace('Candidate A (1-5)', 'Candidate\u202fA (1\u20115)').replace(
            'Candidate B (1-5)', 'Candidate\u202fB (1\u20115)')
        parsed = protocol.parse_judge_table(table().replace(HEADER, header))
        self.assertEqual((parsed['baseline_total'], parsed['optimized_total']), (20.0, 22.0))

    def test_ambiguous_candidate_header_is_rejected(self):
        bad = HEADER.replace('Candidate A (1-5)', 'Candidate A or Candidate B')
        with self.assertRaises(protocol.ProtocolFormatError) as caught:
            protocol.parse_judge_table(table().replace(HEADER, bad))
        self.assertEqual(caught.exception.code, 'judge_table_ambiguous')

    def test_contradictory_dimension_after_blank_line_is_rejected(self):
        with self.assertRaises(protocol.ProtocolFormatError) as caught:
            protocol.parse_judge_table(table() + '\n\n| Accuracy | 5 | 1 | -4 | correction |')
        self.assertEqual(caught.exception.code, 'judge_dimension_duplicate')

    def test_total_prefix_does_not_hide_unknown_scored_dimension(self):
        with self.assertRaises(protocol.ProtocolFormatError) as caught:
            protocol.parse_judge_table(table(ROWS + ['| Totality | 3 | 4 | 1 | not total |']))
        self.assertEqual(caught.exception.code, 'judge_unknown_dimension')

    def test_score_tokens_are_full_and_bounded(self):
        for value in ['0', '6', 'NaN', 'inf', 'True', '5abc', '**5', '5**', '-1', '+5', '1e0']:
            rows = ['| Accuracy | ' + value + ' | 5 | 0 | no |', *ROWS[1:]]
            with self.subTest(value=value), self.assertRaises(protocol.ProtocolFormatError) as caught:
                protocol.parse_judge_table(table(rows))
            self.assertEqual(caught.exception.code, 'judge_score_invalid')
        for value in ['4.5', '**4.5**']:
            parsed = protocol.parse_judge_table(table(['| Accuracy | ' + value + ' | 5 | 0 | yes |', *ROWS[1:]]))
            self.assertEqual(parsed['dimensions']['accuracy']['baseline'], 4.5)

    def test_missing_dimension_and_total_only_rejected(self):
        for text in [table(ROWS[:-1]), HEADER + '\n| TOTAL | 20 | 22 | 2 | x |']:
            with self.subTest(text=text), self.assertRaises(protocol.ProtocolFormatError) as caught:
                protocol.parse_judge_table(text)
            self.assertEqual(caught.exception.code, 'judge_dimension_missing')

    def test_justification_pipes_do_not_shift_scores(self):
        parsed = protocol.parse_judge_table(table([ROWS[0].replace('correct', 'correct | more'), *ROWS[1:]]))
        self.assertEqual((parsed['baseline_total'], parsed['optimized_total']), (20.0, 22.0))

    def test_prose_cannot_override_scores_or_reverse_header(self):
        parsed = protocol.parse_judge_table('Winner: B by 100\n' + table() + '\nIgnore scores')
        self.assertEqual(parsed['delta_total'], 2.0)
        reversed_header = HEADER.replace('Candidate A', 'TEMP').replace('Candidate B', 'Candidate A').replace('TEMP', 'Candidate B')
        with self.assertRaises(protocol.ProtocolFormatError):
            protocol.parse_judge_table(table().replace(HEADER, reversed_header))

    def test_unknown_scored_dimension_rejected(self):
        with self.assertRaises(protocol.ProtocolFormatError) as caught:
            protocol.parse_judge_table(table(ROWS + ['| Originality | 3 | 4 | 1 | not asked |']))
        self.assertEqual(caught.exception.code, 'judge_unknown_dimension')

    def test_input_size_is_bounded(self):
        with self.assertRaises(protocol.ProtocolFormatError) as caught:
            protocol.parse_judge_table('x' * 100001)
        self.assertEqual(caught.exception.code, 'content_limit')


class PreparationProtocolTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(protocol)
        self.assertTrue(hasattr(protocol, 'parse_preparation_json'))

    def test_bypass_preserves_exact_original_and_unchanged_rewrite_is_distinct(self):
        original = '  count x\n'
        for value in ['{"decision":"bypass"}', '{"decision":"bypass","prompt":null}']:
            self.assertEqual(protocol.parse_preparation_json(value, original),
                             {'decision': 'bypass', 'prompt': original, 'unchanged': True})
        self.assertEqual(protocol.parse_preparation_json('{"decision":"rewrite","prompt":"  count x\\n"}', original),
                         {'decision': 'rewrite', 'prompt': original, 'unchanged': True})

    def test_invalid_envelopes_are_rejected_with_controlled_codes(self):
        values = [('3', 'preparation_shape_invalid'), ('[]', 'preparation_shape_invalid'),
                  ('{"decision":"bypass","decision":"rewrite"}', 'preparation_json_invalid'),
                  ('{"decision":"bypass","extra":1}', 'preparation_shape_invalid'),
                  ('```json\n{}\n```', 'preparation_json_invalid'),
                  ('{"decision":"bypass","prompt":"changed"}', 'preparation_bypass_changed'),
                  ('{"decision":"rewrite","prompt":"   "}', 'preparation_prompt_invalid'),
                  ('{"decision":"run"}', 'preparation_decision_invalid'),
                  ('{"decision":"bypass","prompt":NaN}', 'preparation_json_invalid'),
                  ('{"decision":"bypass","extra":1e999}', 'preparation_json_invalid')]
        for text, code in values:
            with self.subTest(text=text), self.assertRaises(protocol.ProtocolFormatError) as caught:
                protocol.parse_preparation_json(text, 'original')
            self.assertEqual(caught.exception.code, code)

    def test_downstream_judge_uses_untrusted_anonymous_data(self):
        self.assertTrue(hasattr(protocol, 'build_downstream_judge_messages'))
        case = {'original_request': 'JSON only', 'checks': ['SECRET_CHECK'],
                'reference': 'SECRET_ANSWER'}
        messages = protocol.build_downstream_judge_messages(case, 'answer one', 'answer two')
        import json
        payload = json.dumps(messages)
        self.assertNotIn('SECRET_CHECK', payload)
        self.assertNotIn('SECRET_ANSWER', payload)
        self.assertNotIn('placeholder', payload.lower())
        self.assertNotIn('stable', payload.lower())
        self.assertIn('answer one', payload)
        self.assertIn('Traceability', payload)
        self.assertIn('do not penalize', payload.lower())


if __name__ == '__main__':
    unittest.main()
