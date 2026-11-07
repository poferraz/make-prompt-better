#!/usr/bin/env python3
"""Run bounded, paired skill evaluations. Dry runs never call models or write results."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

try:
    from research.benchmark.v4 import run_ollama_benchmarks as runner
    from research.benchmark.v4.blind_stats_engine import cluster_bootstrap_mean_ci
except ImportError:
    import run_ollama_benchmarks as runner
    from blind_stats_engine import cluster_bootstrap_mean_ci


MIN_TASK_CLUSTERS = 5


def save(path: Path, value: dict) -> None:
    runner.atomic_write(path, json.dumps(value, indent=2) + '\n')


def campaign_manifest(args: argparse.Namespace) -> dict:
    models = [m.strip() for m in args.models.split(',') if m.strip()]
    seeds = [int(s.strip()) for s in args.seeds.split(',') if s.strip()]
    tests = [int(s.strip()) for s in args.tests.split(',') if s.strip()]
    if not models or len({runner.slugify_model(m) for m in models}) != len(models):
        raise ValueError('Explicit unique models with distinct result paths are required')
    if any(runner.slugify_model(m) in {'', '.', '..'} for m in models):
        raise ValueError('Invalid model identifier')
    if not args.judge_model.strip() or args.judge_model in models:
        raise ValueError('The judge must be independent of every evaluated model')
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError('Repeat seeds must be unique and nonempty')
    if not tests or len(set(tests)) != len(tests) or not set(tests) <= {t['id'] for t in runner.TEST_CASES}:
        raise ValueError('Test IDs must be unique members of the benchmark suite')
    if not math.isfinite(args.deadline_seconds) or args.deadline_seconds <= 0 or args.timeout <= 0 or args.max_output_tokens <= 0:
        raise ValueError('Deadline, request timeout, and output token bound must be positive and finite')
    runner.validate_host(args.host, args.allow_remote_http)
    cell_allowance = (len(tests) * 5 + 1) * runner.DEFAULT_MAX_RETRIES
    required = 2 * len(models) * len(seeds) * cell_allowance
    if args.max_requests < required:
        raise ValueError(f'Campaign requires an aggregate allowance of {required} HTTP requests, including retries')
    skills = {}
    for name in ('baseline', 'candidate'):
        directory = getattr(args, name + '_skill_dir').resolve()
        bundle = runner.load_skill_bundle(directory)
        skills[name] = {'directory': str(directory), 'bundle_sha256': runner.sha256_text(bundle),
                        'source_sha256': {p: hashlib.sha256((directory / p).read_bytes()).hexdigest()
                                          for p in ('SKILL.md', 'references/domain-templates.md',
                                                    'references/research-principles.md')}}
    return {'schema': 1, 'protocol': 'paired-outcome-campaign-v1', 'skills': skills,
            'models': models, 'judge_model': args.judge_model, 'seeds': seeds, 'test_ids': sorted(tests),
            'host_sha256': runner.sha256_text(args.host), 'timeout': args.timeout,
            'deadline_seconds': args.deadline_seconds, 'max_output_tokens': args.max_output_tokens,
            'max_requests': args.max_requests, 'required_request_allowance': required,
            'cell_request_allowance': cell_allowance, 'strict_preservation': True,
            'blind_eval': True, 'swap_positions': True, 'unprescribed_routing': True,
            'strip_cert_markers': False, 'loading_strategy': 'full skill, templates, and research bundle',
            'pricing_status': 'unknown', 'model_revision': 'unknown: provider identifiers may be mutable',
            'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              (Path(__file__), Path(runner.__file__), Path(__file__).with_name('blind_stats_engine.py'))},
            'test_suite_sha256': runner.sha256_text(json.dumps(runner.TEST_CASES, sort_keys=True))}


def cells(manifest: dict):
    for model in manifest['models']:
        for index, seed in enumerate(manifest['seeds']):
            variants = ('baseline', 'candidate') if index % 2 == 0 else ('candidate', 'baseline')
            for variant in variants:
                key = f'{variant}/{runner.slugify_model(model)}/seed-{seed}'
                yield key, variant, model, seed


def expected_run_manifest(manifest: dict, variant: str, model: str, seed: int, host: str) -> dict:
    directory = Path(manifest['skills'][variant]['directory'])
    bundle = runner.load_skill_bundle(directory)
    if runner.sha256_text(bundle) != manifest['skills'][variant]['bundle_sha256']:
        raise ValueError(f'Skill source changed during campaign: {variant}')
    return runner.build_manifest(model, bundle, manifest['test_ids'],
        host, manifest['timeout'], manifest['judge_model'], True, True, False, True, seed,
        skill_dir=directory, strict_preservation=True, max_output_tokens=manifest['max_output_tokens'])


def read_cell(root: Path, key: str, expected: dict) -> dict | None:
    path = root / 'runs' / key / 'run' / runner.slugify_model(expected['model']) / 'metrics.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('manifest') != expected or data.get('model') != expected['model']:
        raise ValueError(f'Saved run manifest differs: {key}')
    for tid, test in data.get('tests', {}).items():
        if int(tid) not in expected['test_ids'] or test.get('id') != int(tid):
            raise ValueError(f'Saved task differs: {key}/{tid}')
        if test.get('judge_model') != expected['judge_model'] or test.get('self_judged') is not False:
            raise ValueError(f'Saved judge differs: {key}/{tid}')
        scores = test['evaluation']['parsed']
        b, o, d = (scores[k] for k in ('baseline_total', 'optimized_total', 'delta_total'))
        if not (5 <= b <= 25 and 5 <= o <= 25 and abs(o - b - d) < .001):
            raise ValueError(f'Invalid saved scores: {key}/{tid}')
    return data


def summarize_campaign(root: Path, manifest: dict, state: dict, host: str) -> dict:
    records, missing, failed = [], [], []
    completed = {}
    preservation = {'baseline': 0, 'candidate': 0}
    usage = {'baseline': [], 'candidate': []}
    telemetry_incomplete = False
    incomplete_variants = set()
    for key, variant, model, seed in cells(manifest):
        cell = state['cells'].get(key, {'status': 'pending'})
        try:
            data = read_cell(root, key, expected_run_manifest(manifest, variant, model, seed, host))
        except (ValueError, TypeError, KeyError, OSError) as exc:
            data = None
            cell.update(status='failed', error=str(exc))
            state['cells'][key] = cell
        if cell['status'] != 'completed':
            failed.append({'cell': key, **cell})
        if data is None:
            telemetry_incomplete = True
            incomplete_variants.add(variant)
            continue
        # Failed synthesis may leave valid tasks. Retain those pairs and expose the failed cell.
        if 'telemetry' not in data or cell['status'] != 'completed':
            telemetry_incomplete = True
            incomplete_variants.add(variant)
        usage[variant].append(data.get('telemetry') or runner.summarize_stage_usage(data))
        audits = {tid: stages.get('preservation', {}) for tid, stages in data.get('in_progress', {}).items()}
        audits.update({tid: test.get('preservation', {}) for tid, test in data.get('tests', {}).items()})
        preservation[variant] += sum(audit.get('status') == 'failed' for audit in audits.values())
        for tid, test in data.get('tests', {}).items():
            completed[(variant, model, seed, int(tid))] = test
    for model in manifest['models']:
        for seed in manifest['seeds']:
            for tid in manifest['test_ids']:
                pair = [completed.get((v, model, seed, tid)) for v in ('baseline', 'candidate')]
                if any(t is None for t in pair):
                    missing.append({'model': model, 'seed': seed, 'test_id': tid,
                                    'missing': [v for v, t in zip(('baseline', 'candidate'), pair) if t is None]})
                    continue
                b, c = [t['evaluation']['parsed']['optimized_total'] for t in pair]
                records.append({'model': model, 'seed': seed, 'test_id': tid,
                                'baseline_total': b, 'optimized_total': c, 'candidate_minus_baseline': c - b})
    clusters = len({r['test_id'] for r in records})
    interval = None
    if clusters >= MIN_TASK_CLUSTERS:
        _, low, high = cluster_bootstrap_mean_ci(records, cluster_key='test_id')
        interval = [low, high]
    stage_totals = {}
    for variant, runs in usage.items():
        stage_totals[variant] = {}
        for stage in ('baseline', 'optimizer', 'execution', 'judge', 'synthesis'):
            values = [run['stages'][stage] for run in runs]
            totals = {}
            for field in ('attempt_count', 'retry_count', 'failed_attempts', 'failed_calls', 'prompt_eval_count',
                          'eval_count', 'known_prompt_eval_count', 'known_eval_count', 'total_elapsed_seconds'):
                vals = [value.get(field) for value in values]
                totals[field] = sum(vals) if vals and all(v is not None for v in vals) else None
                if variant in incomplete_variants and not field.startswith('known_'):
                    totals[field] = None
            stage_totals[variant][stage] = totals
    return {'protocol': manifest['protocol'], 'description': 'Descriptive independent judge scores, not proof of efficacy.',
            'comparison': 'Candidate skill optimized score minus baseline skill optimized score, paired by task/model/seed.',
            'expected_pairs': len(manifest['models']) * len(manifest['seeds']) * len(manifest['test_ids']),
            'completed_pairs': len(records), 'completed_tasks_by_variant': {
                v: sum(key[0] == v for key in completed) for v in ('baseline', 'candidate')},
            'task_clusters': clusters, 'mean_candidate_minus_baseline':
                round(sum(r['candidate_minus_baseline'] for r in records) / len(records), 4) if records else None,
            'task_cluster_95_ci': interval, 'inference_status': 'descriptive_only' if interval is None else 'task_cluster_bootstrap',
            'uncertainty_note': f'Seeds and models are kept within task clusters; fewer than {MIN_TASK_CLUSTERS} tasks is descriptive only. Judge and task selection limit generalization.',
            'pairs': records, 'missing_pairs': missing, 'failed_cells': failed,
            'preservation_failures': preservation, 'pricing_status': 'unknown', 'stage_totals': stage_totals,
            'telemetry_incomplete': telemetry_incomplete,
            'reserved_request_allowance': state['reserved_request_allowance']}


def run_campaign(args: argparse.Namespace, manifest: dict) -> int:
    root = args.output_dir
    if args.dry_run:
        print(json.dumps({'manifest': manifest, 'output_dir': str(root)}, indent=2))
        return 0
    root.mkdir(parents=True, exist_ok=True)
    lock = root / '.campaign.lock'
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise ValueError(f'Campaign is locked: {root}') from exc
    try:
        manifest_path, state_path = root / 'manifest.json', root / 'state.json'
        if manifest_path.exists():
            if json.loads(manifest_path.read_text()) != manifest:
                raise ValueError('Campaign manifest mismatch; choose a new output directory')
            state = json.loads(state_path.read_text())
        else:
            if any(p != lock for p in root.iterdir()):
                raise ValueError('Refusing to overwrite a nonempty campaign directory')
            state = {'deadline_at': time.time() + args.deadline_seconds,
                     'reserved_request_allowance': 0, 'cells': {}}
            save(manifest_path, manifest)
            save(state_path, state)
        for key, variant, model, seed in cells(manifest):
            previous = state['cells'].get(key)
            if previous:
                if previous['status'] == 'running':
                    previous.update(status='failed', error='Interrupted subprocess; reserved allowance retained')
                continue
            remaining = state['deadline_at'] - time.time()
            cell = {'status': 'failed', 'error': 'Campaign deadline exceeded before launch'}
            state['cells'][key] = cell
            if remaining <= 0:
                save(state_path, state)
                continue
            allowance = manifest['cell_request_allowance']
            if state['reserved_request_allowance'] + allowance > manifest['max_requests']:
                cell['error'] = 'Aggregate request allowance exhausted'
                save(state_path, state)
                continue
            try:
                expected = expected_run_manifest(manifest, variant, model, seed, args.host)
            except (OSError, ValueError) as exc:
                cell.update(status='failed', error=str(exc))
                save(state_path, state)
                continue
            run_root = root / 'runs' / key
            run_root.mkdir(parents=True, exist_ok=True)
            command = [sys.executable, str(Path(runner.__file__).resolve()), '--models', model,
                       '--judge-model', manifest['judge_model'], '--seed', str(seed),
                       '--tests', ','.join(map(str, manifest['test_ids'])), '--host', args.host,
                       '--skill-dir', manifest['skills'][variant]['directory'],
                       '--results-dir', str(run_root), '--run-id', 'run', '--timeout', str(args.timeout),
                       '--max-requests', str(allowance), '--max-output-tokens', str(args.max_output_tokens),
                       '--strict-preservation', '--swap-positions', '--unprescribed-routing']
            if args.allow_remote_http:
                command.append('--allow-remote-http')
            state['reserved_request_allowance'] += allowance
            cell.update(status='running', error=None)
            save(state_path, state)
            started = time.monotonic()
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=remaining, check=False)
                runner.atomic_write(run_root / 'stdout.txt', result.stdout or '')
                runner.atomic_write(run_root / 'stderr.txt', result.stderr or '')
                cell.update(status='completed' if result.returncode == 0 else 'failed', returncode=result.returncode,
                            error=None if result.returncode == 0 else 'Runner exited unsuccessfully')
                data = read_cell(root, key, expected)
                if data is None or not all(str(t) in data.get('tests', {}) for t in manifest['test_ids']):
                    cell.update(status='failed', error='Requested task outputs are missing')
            except subprocess.TimeoutExpired as exc:
                # subprocess.run kills and waits for the active runner before raising.
                for name, content in (('stdout', exc.stdout), ('stderr', exc.stderr)):
                    runner.atomic_write(run_root / (name + '.txt'), content.decode(errors='replace') if isinstance(content, bytes) else content or '')
                cell.update(status='failed', error='Campaign subprocess deadline exceeded')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                cell.update(status='failed', error=str(exc))
            cell['elapsed_seconds'] = round(time.monotonic() - started, 4)
            save(state_path, state)
        summary = summarize_campaign(root, manifest, state, args.host)
        save(state_path, state)
        save(root / 'summary.json', summary)
        print(f"Saved campaign: {summary['completed_pairs']}/{summary['expected_pairs']} pairs, {len(summary['failed_cells'])} failed cells")
        return int(bool(summary['failed_cells'] or summary['missing_pairs']))
    finally:
        lock.rmdir()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-skill-dir', type=Path, required=True)
    parser.add_argument('--candidate-skill-dir', type=Path, required=True)
    parser.add_argument('--models', required=True)
    parser.add_argument('--judge-model', required=True)
    parser.add_argument('--seeds', required=True)
    parser.add_argument('--tests', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--max-requests', type=int, required=True)
    parser.add_argument('--deadline-seconds', type=float, required=True)
    parser.add_argument('--max-output-tokens', type=int, default=4096)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--host', default=os.environ.get('OLLAMA_HOST', 'http://localhost:11434'))
    parser.add_argument('--allow-remote-http', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        return run_campaign(args, campaign_manifest(args))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
