#!/usr/bin/env python3
"""Read-only, offline reanalysis of retained downstream campaign records."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

try:
    from research.benchmark.v4 import downstream_protocol as protocol
    from research.benchmark.v4 import downstream_design as design
    from research.benchmark.v4.blind_stats_engine import deterministic_ab_assignment, unblind_parsed_scores
except ImportError:
    import downstream_protocol as protocol
    import downstream_design as design
    from blind_stats_engine import deterministic_ab_assignment, unblind_parsed_scores


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_path(path: Path) -> Path:
    lexical = path if path.is_absolute() else Path.cwd() / path
    for component in (lexical, *lexical.parents):
        if component.is_symlink():
            raise ValueError('Symlinked paths are not accepted')
    absolute = Path(os.path.abspath(path))
    for component in (absolute, *absolute.parents):
        if component.is_symlink():
            raise ValueError('Symlinked paths are not accepted')
    return absolute


def _read(path: Path, inputs: dict) -> dict:
    _safe_path(path)
    data = path.read_bytes()
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError('Campaign evidence must be an object')
    inputs[str(path)] = _sha(data)
    return value



def _scheduled_pairs(manifest: dict) -> list[tuple[str, str]]:
    arms = manifest.get('arms')
    if (not isinstance(arms, list) or not arms or
            any(not isinstance(arm, str) or not arm for arm in arms) or len(set(arms)) != len(arms)):
        raise ValueError('Invalid campaign arms')
    pairs = manifest['pairs'] if 'pairs' in manifest else list(itertools.combinations(arms, 2))
    if not isinstance(pairs, list) or not pairs:
        raise ValueError('Invalid scheduled pairs')
    normalized = []
    seen = set()
    for pair in pairs:
        if (not isinstance(pair, (tuple, list)) or len(pair) != 2 or
                not all(isinstance(arm, str) and arm in arms for arm in pair) or pair[0] == pair[1]):
            raise ValueError('Invalid scheduled pair endpoints')
        identity = frozenset(pair)
        if identity in seen:
            raise ValueError('Duplicate scheduled pair')
        seen.add(identity)
        normalized.append((pair[0], pair[1]))
    if 'recipe' in manifest:
        recipe = design.recipe_definition(manifest['recipe'])
        if (manifest.get('schema') != 3 or arms != recipe['arms'] or
                [list(pair) for pair in normalized] != recipe['pairs'] or
                manifest.get('calls_per_cell') != recipe['calls_per_cell']):
            raise ValueError('Recipe differs from scheduled work')
        if manifest['recipe'] == 'primary-aa':
            skills = manifest.get('skills', {})
            stable, candidate = skills.get('stable', {}), skills.get('candidate', {})
            if (stable.get('mode') != 'full' or candidate.get('mode') != 'full' or
                    not isinstance(stable.get('bundle_sha256'), str) or
                    not re.fullmatch(r'[0-9a-f]{64}', stable['bundle_sha256']) or
                    stable['bundle_sha256'] != candidate.get('bundle_sha256')):
                raise ValueError('A/A recipe requires identical full bundles')
    return normalized


def _valid_arm_order(order, arms: list[str]) -> bool:
    return (isinstance(order, list) and len(order) == len(arms) and
            all(isinstance(arm, str) for arm in order) and len(set(order)) == len(order) and
            set(order) == set(arms))


def _expected(manifest: dict) -> list[dict]:
    if manifest.get('schema') not in (2, 3) or manifest.get('protocol') not in (
            'five-arm-downstream-v2', 'five-arm-downstream-v3'):
        raise ValueError('Unsupported campaign schema')
    if (manifest['schema'] == 2) != (manifest['protocol'].endswith('-v2')):
        raise ValueError('Inconsistent campaign schema')
    cases, models, seeds = manifest['cases'], manifest['models'], manifest['seeds']
    identities = [(c['id'], m, seed) for c, m, seed in itertools.product(cases, models, seeds)]
    if len(set(identities)) != len(identities):
        raise ValueError('Duplicate campaign identity')
    if 'cell_schedule' in manifest:
        schedule = manifest['cell_schedule']
        if not isinstance(schedule, list) or len(schedule) != len(identities):
            raise ValueError('Invalid saved schedule')
        actual = [(c['task_id'], c['model'], c['seed']) for c in schedule]
        if len(set(actual)) != len(actual) or set(actual) != set(identities):
            raise ValueError('Invalid schedule identities')
        if any(type(c.get('index')) is not int for c in schedule) or [c['index'] for c in schedule] != list(range(len(schedule))):
            raise ValueError('Invalid schedule indexes')
        if not all(_valid_arm_order(c.get('arm_order'), manifest['arms']) for c in schedule):
            raise ValueError('Invalid scheduled arm order')
        return schedule
    return [{'index': i, 'task_id': task, 'model': model, 'seed': seed}
            for i, (task, model, seed) in enumerate(identities)]


def _usage(records: list[dict]) -> dict:
    result = {}
    for stage in ('preparation', 'execution', 'judge'):
        calls = [c for r in records for c in r.get('calls', []) if c.get('stage') == stage]
        attempts, unknown_telemetry = [], 0
        for call in calls:
            telemetry = call.get('telemetry') or call.get('response', {}).get('telemetry')
            if call.get('dispatched') is False:
                continue
            if telemetry is None:
                unknown_telemetry += 1
            else:
                attempts.extend(telemetry.get('attempts', []))
        bucket = {'calls': len(calls), 'unknown_telemetry_calls': unknown_telemetry}
        for field in ('prompt_eval_count', 'eval_count'):
            values = [a.get(field) for a in attempts]
            known = [v for v in values if type(v) is int and v >= 0]
            bucket['known_' + field] = sum(known)
            bucket['unknown_' + field + '_attempts'] = len(values) - len(known)
            bucket[field] = sum(known) if not unknown_telemetry and len(values) == len(known) else None
        result[stage] = bucket
    return result


def _validate_request(call: dict, mapping: dict, record: dict, case: dict, manifest: dict) -> None:
    body_text = call.get('request_body')
    if not isinstance(body_text, str) or _sha(body_text.encode('utf-8')) != call.get('request_body_sha256'):
        raise ValueError('Judge request body hash mismatch')
    body = json.loads(body_text)
    messages = body['messages']
    if (_sha(json.dumps(messages, ensure_ascii=False).encode('utf-8')) != call.get('request_sha256') or
            body.get('model') != manifest['judge_model'] or body['options']['seed'] != record['identity']['seed']):
        raise ValueError('Judge request identity mismatch')
    data = json.loads(messages[-1]['content'])
    expected = {'original_request': case['original_request'],
                'candidate_A': record['arms'][mapping['A']]['answer'],
                'candidate_B': record['arms'][mapping['B']]['answer']}
    if data != expected:
        raise ValueError('Judge mapping contradicts retained request')


def reanalyze(campaign_dir: Path, output_dir: Path) -> dict:
    campaign = _safe_path(Path(campaign_dir))
    output = _safe_path(Path(output_dir))
    if '.private' not in output.parts or output.exists() or output == campaign or campaign in output.parents:
        raise ValueError('Output must be a new private directory outside the campaign')
    if any(part in ('archives', 'extracted') for part in output.parts):
        raise ValueError('Output cannot be in an evidence extraction or archive tree')
    if not campaign.is_dir():
        raise ValueError('Campaign directory is unavailable')
    # The first directory beneath the nearest .private root is the evidence collection.
    # Derived output belongs in a separate sibling tree, never alongside its source records.
    private_positions = [i for i, part in enumerate(campaign.parts) if part == '.private']
    if private_positions:
        position = private_positions[-1]
        if position + 1 < len(campaign.parts):
            evidence_root = Path(*campaign.parts[:position + 2])
            if output == evidence_root or evidence_root in output.parents:
                raise ValueError('Output must be outside the source evidence root')

    inputs = {}
    manifest = _read(campaign / 'manifest.json', inputs)
    state = _read(campaign / 'state.json', inputs)
    official_summary = _read(campaign / 'summary.json', inputs)
    scheduled_pairs = _scheduled_pairs(manifest)
    allowed_pairs = {left + '__' + right for left, right in scheduled_pairs}
    expected = _expected(manifest)
    case_by_id = {case['id']: case for case in manifest['cases']}
    records = []
    missing = []
    for identity in expected:
        path = campaign / 'cells' / f"{identity['index']}.json"
        _safe_path(path)
        if not path.exists():
            missing.append(identity['index'])
            continue
        record = _read(path, inputs)
        if any(record.get('identity', {}).get(key) != identity[key] for key in ('index', 'task_id', 'model', 'seed')):
            raise ValueError('Cell identity differs from manifest')
        if 'arm_order' in identity and record['identity'].get('arm_order') != identity['arm_order']:
            raise ValueError('Cell arm order differs from schedule')
        if not _valid_arm_order(record['identity'].get('arm_order'), manifest['arms']):
            raise ValueError('Invalid recorded arm order')
        records.append(record)

    results, official, orphan = [], 0, 0
    excluded = Counter()
    for record in records:
        cell = record['identity']
        grouped = defaultdict(list)
        comparisons = record.get('comparisons', {})
        if not isinstance(comparisons, dict) or not set(comparisons) <= allowed_pairs:
            raise ValueError('Official comparison is not scheduled')
        official += len(comparisons)
        for call in record.get('calls', []):
            if call.get('stage') == 'judge':
                grouped[call['arm']].append(call)
        for pair, calls in grouped.items():
            if pair not in allowed_pairs:
                raise ValueError('Judge comparison is not scheduled')
            if len(calls) > 2:
                raise ValueError('Duplicate judge passes')
            names = pair.split('__')
            if len(names) != 2 or not all(name in manifest['arms'] for name in names):
                raise ValueError('Invalid judge pair')
            left, right = names
            assignment = deterministic_ab_assignment(cell['seed'], cell['model'] + ':' + pair, cell['task_id'])
            first = {label: left if variant == 'baseline' else right for label, variant in assignment.items()}
            parsed_passes, seen = [], set()
            for offset, call in enumerate(calls, 1):
                if manifest['schema'] == 3:
                    index = call.get('judge_pass_index')
                    mapping = call.get('judge_mapping')
                    if call.get('judge_pair') != pair or index not in (1, 2) or index in seen:
                        raise ValueError('Invalid saved judge pass')
                    if not isinstance(mapping, dict) or set(mapping) != {'A', 'B'} or set(mapping.values()) != {left, right}:
                        raise ValueError('Invalid saved judge mapping')
                else:
                    index = offset
                    mapping = first if index == 1 else {'A': first['B'], 'B': first['A']}
                seen.add(index)
                if 'request_body' not in call:
                    excluded['request_body_missing'] += 1
                    continue
                _validate_request(call, mapping, record, case_by_id[cell['task_id']], manifest)
                if call.get('status') != 'completed' and call.get('error') != 'ValueError':
                    excluded['transport_failed'] += 1
                    continue
                text = call.get('response', {}).get('content')
                try:
                    scores = protocol.parse_judge_table(text)
                except protocol.ProtocolFormatError:
                    excluded['invalid_judge_format'] += 1
                    scores = None
                if scores is not None:
                    mapped = unblind_parsed_scores(scores, {k: 'baseline' if v == left else 'optimized'
                                                          for k, v in mapping.items()})
                    parsed_passes.append((index, mapping, mapped))
            if len(parsed_passes) == 2:
                p1, p2 = sorted(parsed_passes)
                if p1[0] != 1 or p2[0] != 2 or p1[1]['A'] != p2[1]['B'] or p1[1]['B'] != p2[1]['A']:
                    raise ValueError('Judge positions do not swap')
                delta = round((p1[2]['delta_total'] + p2[2]['delta_total']) / 2, 2)
            else:
                delta = None
                orphan += len(parsed_passes)
            official_complete = pair in record.get('comparisons', {})
            results.append({'cell': cell['index'], 'task_id': cell['task_id'], 'model': cell['model'],
                            'seed': cell['seed'], 'pair': pair, 'official_complete': official_complete,
                            'original_statuses': [c['status'] for c in calls],
                            'recovered_format_valid': delta is not None and not official_complete,
                            'valid_passes': len(parsed_passes), 'delta': delta})

    derived = sum(row['delta'] is not None for row in results)
    expected_pairs = len(expected) * len(scheduled_pairs)
    pair_summaries = {}
    for left, right in scheduled_pairs:
        key = left + '__' + right
        rows = [row for row in results if row['pair'] == key and row['delta'] is not None]
        pair_summaries[key] = {'expected_pairs': len(expected), 'completed_pairs': len(rows),
                               'mean_delta': sum(row['delta'] for row in rows) / len(rows) if rows else None,
                               'recovered_pairs': sum(row['recovered_format_valid'] for row in rows)}
    summary = {'official_completed_pairs': official, 'derived_completed_pairs': derived,
               'pair_summaries': pair_summaries,
               'expected_pairs': expected_pairs, 'official_missing_pairs': expected_pairs - official,
               'derived_missing_pairs': expected_pairs - derived, 'excluded_passes': dict(excluded),
               'recovered_pairs': sum(row['recovered_format_valid'] for row in results),
               'orphan_valid_passes': orphan, 'expected_cells': len(expected), 'recorded_cells': len(records),
               'missing_cell_indexes': missing, 'usage': _usage(records),
               'rubric': 'original campaign rubric; parser-only reanalysis',
               'original_summary_completed_cells': official_summary.get('completed_cells')}
    # If any launched reservation lacks a record, full usage totals cannot be known.
    recorded = {r['identity']['index'] for r in records}
    missing_launched = [int(k) for k, value in state.get('cells', {}).items()
                        if int(k) not in recorded and value.get('reserved_request_allowance', 0) > 0]
    if missing_launched:
        for bucket in summary['usage'].values():
            bucket['prompt_eval_count'] = bucket['eval_count'] = None
    summary['missing_launched_cells'] = missing_launched
    analysis_manifest = {'schema': 1, 'campaign_schema': manifest['schema'],
        'parser': 'markdown-dimensions-v2', 'algorithm': 'downstream-reanalysis-v1',
        'source_sha256': {p.name: _sha(p.read_bytes()) for p in (Path(__file__), Path(protocol.__file__), Path(__file__).with_name('blind_stats_engine.py'), Path(design.__file__))},
        'inputs_sha256': inputs}
    verification = {'network_calls_enabled': False, 'original_file_hashes_unchanged': True,
                    'original_statuses_preserved': True}
    if any(_sha(Path(path).read_bytes()) != digest for path, digest in inputs.items()):
        raise ValueError('Evidence changed during reanalysis')

    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _safe_path(output.parent)
    # Exclusive creation prevents overwriting existing output, even on concurrent invocations.
    try:
        output.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise ValueError('Output already exists') from exc
    try:
        for name, value in (('analysis-manifest.json', analysis_manifest), ('comparison-results.json', results),
                            ('summary.json', summary), ('verification.json', verification)):
            fd, temporary = tempfile.mkstemp(prefix='.analysis-', dir=output)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                    json.dump(value, handle, ensure_ascii=False, indent=2)
                    handle.write('\n')
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, output / name)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        if any(_sha(Path(path).read_bytes()) != digest for path, digest in inputs.items()):
            raise ValueError('Evidence changed during reanalysis')
    except BaseException:
        shutil.rmtree(output)
        raise
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(reanalyze(args.campaign_dir, args.output_dir), indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f'Error: {type(exc).__name__}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
