"""Objective fixture tests use hand-checked answers, never generated execution."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class CorpusTests(unittest.TestCase):
    def setUp(self):
        path = HERE / 'downstream_corpus.py'
        self.assertTrue(path.exists(), 'Corpus loader must exist')
        spec = importlib.util.spec_from_file_location('downstream_corpus', path)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def load(self, value):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'cases.json'
            path.write_text(json.dumps(value))
            return self.mod.load_corpus(path)

    def test_public_corpus_has_checkable_answers_without_private_files(self):
        corpus = self.mod.load_corpus()
        self.assertEqual(corpus['split'], 'development')
        self.assertEqual({c['stratum'] for c in corpus['cases']}, {'unclear', 'ordinary', 'strong'})
        answers = ['18', '[2,4,7]', '3', '{"apples":5,"pears":2}', 'rojo, azul', '2028-03-01', '["A17","B04"]', 'MATCH', '{"total":19,"currency":"EUR"}']
        self.assertEqual(len(corpus['cases']), len(answers))
        for case, answer in zip(corpus['cases'], answers):
            with self.subTest(case=case['id']):
                self.assertTrue(all(r['status'] == 'passed' for r in self.mod.evaluate_checks(answer, case['checks'])))
                self.assertTrue(any(r['status'] == 'failed' for r in self.mod.evaluate_checks('WRONG', case['checks'])))
                for arm in ['original_request', 'minimal_clarity', 'strong_direct']:
                    self.assertTrue(all(r['status'] == 'passed' for r in self.mod.evaluate_checks(case[arm], case['preservation_checks'])), arm)

    def test_rejects_duplicate_ids_mixed_splits_missing_provenance_bad_arms(self):
        original = self.mod.load_corpus()
        mutations = [lambda d: d['cases'].append(copy.deepcopy(d['cases'][0])),
                     lambda d: d['cases'][0].update(split='holdout'),
                     lambda d: d.pop('provenance'),
                     lambda d: d['provenance'].pop('strong_direct_source'),
                     lambda d: d.update(schema_version=True),
                     lambda d: d['cases'][0].update(language=None),
                     lambda d: d['cases'][0].update(tags='arithmetic'),
                     lambda d: d['cases'][0]['checks'].append(copy.deepcopy(d['cases'][0]['checks'][0])),
                     lambda d: d['cases'][0]['preservation_checks'][0].update(type='equals'),
                     lambda d: d.update(split='mixed'),
                     lambda d: d['cases'][0].update(strong_direct=''),
                     lambda d: d['cases'][0].update(expected_bypass='yes'),
                     lambda d: d['cases'][0].update(checks=[]),
                     lambda d: d['cases'][0]['checks'][0].update(type='python', value='raise SystemExit')]
        for mutate in mutations:
            value = copy.deepcopy(original)
            mutate(value)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                self.load(value)

    def test_explicit_holdout_load_requires_no_private_discovery(self):
        value = self.mod.load_corpus()
        value['split'] = 'holdout'
        self.assertEqual(self.load(value)['split'], 'holdout')

    def test_json_numbers_compare_semantically_without_accepting_booleans_or_overflow(self):
        spec = [{'id': 'invoice', 'type': 'json_equals',
                 'value': {'total': 19, 'currency': 'EUR', 'items': [1, {'count': 2}]}}]
        self.assertEqual(self.mod.evaluate_checks(
            '{"total":19.0,"currency":"EUR","items":[1.0,{"count":2.0}]}', spec)[0]['status'], 'passed')
        for output in ['{"total":19,"currency":"EUR","items":[true,{"count":2}]}',
                       '{"total":19,"currency":"EUR","items":[1,{"count":true}]}']:
            self.assertEqual(self.mod.evaluate_checks(output, spec)[0]['status'], 'failed')
        for value in ['1e999', '-1e999', '{"nested":[1e999]}']:
            result = self.mod.evaluate_checks(value, [{'id':'a','type':'json_equals','value':0}])[0]
            self.assertEqual(result['status'], 'failed')
            self.assertIn('non-finite', result['error'])
        corpus = self.mod.load_corpus()
        corpus['cases'][0]['checks'] = [{'id':'a','type':'json_equals','value':float('inf')}]
        with self.assertRaises(ValueError):
            self.load(corpus)

    def test_safe_checks_strict_json_and_errors(self):
        for kind, value, text, status in [
            ('equals','42','42','passed'), ('equals','42',' 42 ','failed'),
            ('contains','OK','OKAY','passed'), ('not_contains','bad','good','passed'),
            ('not_contains','bad','bad','failed'), ('json_equals', {'x':1}, '{"x":1}', 'passed'),
            ('json_equals', {'x':1}, '{"x":true}', 'failed'),
            ('json_equals', {'x':1}, '{"x":0,"x":1}', 'failed'),
            ('json_equals', [1,2], '[2,1]', 'failed'),
            ('json_equals', 1, '1\nextra', 'failed')]:
            with self.subTest(kind=kind, text=text):
                self.assertEqual(self.mod.evaluate_checks(text,[{'id':'a','type':kind,'value':value}])[0]['status'],status)
        self.assertEqual(self.mod.evaluate_checks(' 42\n',[{'id':'a','type':'equals','value':'42','strip':True}])[0]['status'],'passed')
        self.assertEqual(self.mod.evaluate_checks('ABC',[{'id':'a','type':'regex','pattern':'^[A-Z]{3}$'}])[0]['status'],'passed')
        for check in [{'id':'a','type':'exec','value':'1+1'}, {'id':'a','type':'regex','pattern':'['},
                      {'id':'a','type':'regex','pattern':'(a+)+$'},
                      {'id':'a','type':'regex','pattern':'a{129}'},
                      {'id':'a','type':'equals','value':'x','code':'print(1)'}]:
            result = self.mod.evaluate_checks('anything',[check])[0]
            self.assertEqual(result['status'],'failed')
            self.assertIn('error',result)


if __name__ == '__main__':
    unittest.main()
