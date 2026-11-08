"""Strict, downstream-specific response contracts; legacy scoring remains unchanged."""
from __future__ import annotations

import math
import re

MAX_CONTENT_CHARS = 100_000
DIMENSIONS = ('accuracy', 'completeness', 'structure', 'actionability', 'traceability')
_SCORE = re.compile(r'[0-9]+(?:\.[0-9]+)?\Z')
_SEPARATOR = re.compile(r':?-{3,}:?\Z')


class ProtocolFormatError(ValueError):
    """A controlled format error that never contains untrusted response text."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _content_limit(content: str) -> None:
    if not isinstance(content, str):
        raise ProtocolFormatError('judge_table_missing')
    if len(content) > MAX_CONTENT_CHARS:
        raise ProtocolFormatError('content_limit')


def _unbold(value: str) -> str:
    value = value.strip()
    if value.startswith('**') and value.endswith('**') and len(value) > 4:
        return value[2:-2].strip()
    return value


def _cells(line: str) -> list[str] | None:
    line = line.strip()
    if not line.startswith('|') or not line.endswith('|'):
        return None
    return [part.strip() for part in line[1:-1].split('|')]


def _candidate(value: str, label: str) -> bool:
    return bool(re.match(r'^candidate\s+' + label + r'(?:\b|\s|\()', _unbold(value), re.IGNORECASE))


def _score(value: str) -> float:
    value = _unbold(value)
    if not _SCORE.fullmatch(value):
        raise ProtocolFormatError('judge_score_invalid')
    number = float(value)
    if not math.isfinite(number) or not 1 <= number <= 5:
        raise ProtocolFormatError('judge_score_invalid')
    return number


def parse_judge_table(content: str) -> dict:
    """Parse one anonymous rubric table, rejecting ambiguous or invalid rows."""
    _content_limit(content)
    lines = content.splitlines()
    headers = []
    for i, line in enumerate(lines):
        row = _cells(line)
        if row and len(row) >= 3 and _unbold(row[0]).lower() == 'dimension':
            if (_candidate(row[1], 'a') and _candidate(row[2], 'b')):
                headers.append(i)
            elif _candidate(row[1], 'b') or _candidate(row[2], 'a'):
                raise ProtocolFormatError('judge_table_ambiguous')
    if not headers:
        raise ProtocolFormatError('judge_table_missing')
    if len(headers) != 1:
        raise ProtocolFormatError('judge_table_ambiguous')

    dimensions = {}
    for line in lines[headers[0] + 1:]:
        row = _cells(line)
        if row is None:
            break
        if not row or _SEPARATOR.fullmatch(row[0]):
            continue
        label = _unbold(row[0]).lower()
        if label.startswith('total'):
            continue
        if label not in DIMENSIONS:
            raise ProtocolFormatError('judge_unknown_dimension')
        if label in dimensions:
            raise ProtocolFormatError('judge_dimension_duplicate')
        if len(row) < 3:
            raise ProtocolFormatError('judge_score_invalid')
        left, right = _score(row[1]), _score(row[2])
        dimensions[label] = {'baseline': left, 'optimized': right, 'delta': round(right - left, 2)}
    if len(dimensions) != len(DIMENSIONS):
        raise ProtocolFormatError('judge_dimension_missing')
    left_total = sum(value['baseline'] for value in dimensions.values())
    right_total = sum(value['optimized'] for value in dimensions.values())
    delta = round(right_total - left_total, 2)
    return {'dimensions': dimensions, 'baseline_total': left_total, 'optimized_total': right_total,
            'delta_total': delta, 'winner': 'Optimized' if delta > 0 else 'Baseline' if delta < 0 else 'Tie'}
