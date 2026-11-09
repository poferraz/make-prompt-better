"""Versioned downstream fixtures and safe, non-executable objective checks.

Regex checks intentionally support only a small subset: literals, anchors,
character classes, escapes, and fixed repetitions up to 128. No grouping,
alternation, variable repetition, or backreferences. Checks never execute code.
"""
import json
import math
from pathlib import Path
import re

DEFAULT_CORPUS = Path(__file__).with_name('downstream_cases.json')
ARMS = ('original_request', 'minimal_clarity', 'strong_direct')


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def _json(text):
    def invalid(value):
        raise ValueError('non-finite JSON number: ' + value)
    def finite_float(value):
        parsed = float(value)
        _require(math.isfinite(parsed), 'non-finite JSON number: ' + value)
        return parsed
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=invalid, parse_float=finite_float)


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def _json_equal(left, right):
    # bool subclasses int in Python but remains a distinct JSON type.
    if type(left) in (int, float) and type(right) in (int, float):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_json_equal(left[key], right[key]) for key in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(_json_equal(a, b) for a, b in zip(left, right))
    return left == right


def _check_spec(check):
    _require(isinstance(check, dict), 'check must be an object')
    _require(isinstance(check.get('id'), str) and bool(check['id']), 'check needs id')
    kind = check.get('type')
    _require(kind in {'equals', 'contains', 'not_contains', 'json_equals', 'regex'}, 'unsupported check type')
    allowed = {'id', 'type', 'pattern'} if kind == 'regex' else {'id', 'type', 'value'}
    if kind == 'equals':
        allowed.add('strip')
    _require(set(check) <= allowed, 'unknown check fields')
    if kind == 'regex':
        pattern = check.get('pattern')
        _require(isinstance(pattern, str) and 0 < len(pattern) <= 512, 'invalid regex pattern')
        _require(not any(c in pattern for c in '()*+?|'), 'unsupported regex operator')
        _require(not re.search(r'\\[1-9]', pattern), 'regex backreferences forbidden')
        for count in re.findall(r'\{([^}]*)\}', pattern):
            _require(count.isdigit() and int(count) <= 128, 'only fixed regex repetition up to 128 supported')
        re.compile(pattern)
    else:
        _require('value' in check, 'check needs value')
        if kind == 'json_equals':
            _canonical(check['value'])
        else:
            _require(isinstance(check['value'], str), 'literal check value must be text')
        if 'strip' in check:
            _require(type(check['strip']) is bool, 'strip must be boolean')


def load_corpus(path=None):
    """Load and validate one split. Never discovers or reads private files."""
    data = _json(Path(path or DEFAULT_CORPUS).read_text(encoding='utf-8'))
    _require(isinstance(data, dict), 'corpus must be an object')
    _require(type(data.get('schema_version')) is int and data['schema_version'] == 1, 'unsupported schema version')
    _require(data.get('split') in {'development', 'holdout'}, 'one development or holdout split required')
    provenance = data.get('provenance')
    _require(isinstance(provenance, dict), 'authoring provenance required')
    for key in ('author', 'method', 'strong_direct_source', 'limitations'):
        _require(isinstance(provenance.get(key), str) and bool(provenance[key].strip()), 'missing provenance: ' + key)
    cases = data.get('cases')
    _require(isinstance(cases, list) and bool(cases), 'nonempty cases required')
    seen = set()
    allowed = {'id', 'stratum', 'language', 'tags', *ARMS, 'checks', 'preservation_checks', 'expected_bypass'}
    for case in cases:
        _require(isinstance(case, dict) and set(case) <= allowed, 'unknown case fields or mixed split')
        ident = case.get('id')
        _require(isinstance(ident, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident), 'invalid case id')
        _require(ident not in seen, 'duplicate case id')
        seen.add(ident)
        _require(case.get('stratum') in {'unclear', 'ordinary', 'strong'}, 'invalid stratum')
        for key in ('language', *ARMS):
            _require(isinstance(case.get(key), str) and bool(case[key].strip()), 'missing text: ' + key)
        _require(isinstance(case.get('tags'), list) and all(isinstance(t, str) and t for t in case['tags']), 'invalid tags')
        if 'expected_bypass' in case:
            _require(type(case['expected_bypass']) is bool, 'expected_bypass must be boolean')
        for field in ('checks', 'preservation_checks'):
            specs = case.get(field)
            _require(isinstance(specs, list) and (bool(specs) or field == 'preservation_checks'), 'invalid checks list')
            ids = set()
            for check in specs:
                try:
                    _check_spec(check)
                except (TypeError, re.error) as exc:
                    raise ValueError(str(exc)) from exc
                _require(check['id'] not in ids, 'duplicate check id')
                ids.add(check['id'])
                if field == 'preservation_checks':
                    _require(check['type'] in {'contains', 'regex'}, 'preservation checks must be literal or regex')
    return data


def evaluate_checks(text, checks):
    """Return one passed/failed record per spec; malformed outputs fail closed.

    json_equals requires a complete JSON document, rejects duplicate keys and
    non-finite numbers, and compares numbers by value while distinguishing
    booleans from numbers. equals only
    trims whitespace when strip=true. Errors are included, never swallowed.
    """
    results = []
    for check in checks:
        result = {'id': check.get('id', '') if isinstance(check, dict) else '', 'status': 'failed'}
        try:
            _check_spec(check)
            _require(isinstance(text, str) and len(text) <= 100000, 'output must be text of at most 100000 characters')
            kind = check['type']
            if kind == 'equals':
                passed = (text.strip() if check.get('strip', False) else text) == check['value']
            elif kind == 'contains':
                passed = check['value'] in text
            elif kind == 'not_contains':
                passed = check['value'] not in text
            elif kind == 'json_equals':
                passed = _json_equal(_json(text), check['value'])
            else:
                passed = re.search(check['pattern'], text) is not None
            result['status'] = 'passed' if passed else 'failed'
        except (ValueError, TypeError, re.error, RecursionError) as exc:
            result['error'] = str(exc)
        results.append(result)
    return results
