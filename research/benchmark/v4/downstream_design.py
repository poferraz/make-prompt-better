#!/usr/bin/env python3
"""Offline downstream experiment planning. This module cannot launch inference."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import statistics

FIELDS = frozenset({'tasks', 'executors', 'seeds_per_executor', 'aa_tasks', 'feasibility_tasks',
                    'effect', 'task_sd', 'holdout_custodian', 'spend_cap', 'protocol_frozen',
                    'independent_review_complete'})


def _number(value, *, name: str, minimum: float, maximum: float, exclusive_min=False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{name} must be numeric')
    try:
        number = float(value)
    except OverflowError:
        raise ValueError(f'{name} is outside bounds') from None
    if not math.isfinite(number) or number > maximum or (number <= minimum if exclusive_min else number < minimum):
        raise ValueError(f'{name} is outside bounds')
    return number


def _count(value, *, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return value


def required_tasks(effect: float, task_sd: float) -> int:
    """Normal approximation for 80% power, two-sided alpha 0.05."""
    effect = _number(effect, name='effect', minimum=0, maximum=1, exclusive_min=True)
    task_sd = _number(task_sd, name='task_sd', minimum=0, maximum=1)
    if effect * effect == 0:
        raise ValueError('effect is too small to represent')
    return max(1, math.ceil((1.96 + 0.84) ** 2 * task_sd ** 2 / effect ** 2))


def simulate_task_power(n_tasks: int, effect: float, task_sd: float,
                        family_size: int = 1, n_trials: int = 2000, seed: int = 42) -> dict:
    """Stress-test a normal approximation with perfectly correlated family members."""
    n_tasks = _count(n_tasks, name='n_tasks', minimum=2)
    family_size = _count(family_size, name='family_size', minimum=1)
    n_trials = _count(n_trials, name='n_trials', minimum=1)
    if type(seed) is not int or n_tasks % family_size or n_tasks // family_size < 2:
        raise ValueError('Invalid family structure or seed')
    families = n_tasks // family_size
    if families * n_trials > 2_000_000:
        raise ValueError('Simulation exceeds the offline work bound')
    effect = _number(effect, name='effect', minimum=0, maximum=1)
    task_sd = _number(task_sd, name='task_sd', minimum=0, maximum=1)
    second_moment = task_sd ** 2 + effect ** 2
    positive = (second_moment + effect) / 2
    negative = (second_moment - effect) / 2
    if negative < 0 or positive < 0 or positive + negative > 1:
        raise ValueError('Effect and standard deviation do not define valid probabilities')
    rng = random.Random(seed)
    rejected = covered = 0
    for _ in range(n_trials):
        samples = []
        for _ in range(families):
            draw = rng.random()
            samples.append(1 if draw < positive else -1 if draw < positive + negative else 0)
        mean = statistics.fmean(samples)
        half_width = 1.96 * statistics.stdev(samples) / math.sqrt(families)
        low, high = mean - half_width, mean + half_width
        rejected += low > 0 or high < 0
        covered += low <= effect <= high
    rejection = rejected / n_trials
    return {'method': 'normal-approximation-planning-simulation', 'n_tasks': n_tasks,
            'independent_families': families, 'family_size': family_size, 'n_trials': n_trials,
            'seed': seed, 'effect': effect, 'task_sd': task_sd, 'rejection_rate': rejection,
            'coverage': covered / n_trials, 'monte_carlo_se': math.sqrt(rejection * (1 - rejection) / n_trials),
            'limitation': 'Hypothetical independent families, not calibration of the final clustered bootstrap.'}


def build_design(config: dict) -> dict:
    """Calculate request allowances, never granting authorization or dispatch capability."""
    if not isinstance(config, dict) or set(config) != FIELDS:
        raise ValueError('Design requires exactly the documented fields')
    tasks = _count(config['tasks'], name='tasks', minimum=1)
    executors = _count(config['executors'], name='executors', minimum=1)
    seeds = _count(config['seeds_per_executor'], name='seeds_per_executor', minimum=1)
    aa = _count(config['aa_tasks'], name='aa_tasks')
    feasibility = _count(config['feasibility_tasks'], name='feasibility_tasks')
    if aa > tasks:
        raise ValueError('A/A tasks must be a subset of the confirmatory tasks')
    effect = _number(config['effect'], name='effect', minimum=0, maximum=1, exclusive_min=True)
    sd = _number(config['task_sd'], name='task_sd', minimum=0, maximum=1)
    custodian = config['holdout_custodian']
    if custodian is not None and (not isinstance(custodian, str) or not custodian.strip()):
        raise ValueError('Custodian must be a nonempty label or null')
    cap = config['spend_cap']
    if cap is not None:
        if not isinstance(cap, dict) or set(cap) != {'currency', 'amount'} or cap['currency'] != 'USD':
            raise ValueError('Spend cap must specify a USD amount')
        _number(cap['amount'], name='spend cap', minimum=0, maximum=1e300, exclusive_min=True)
    for key in ('protocol_frozen', 'independent_review_complete'):
        if type(config[key]) is not bool:
            raise ValueError(f'{key} must be boolean')
    unresolved = []
    if custodian is None:
        unresolved.append('independent_custody')
    if cap is None:
        unresolved.append('spend_cap')
    if not config['protocol_frozen']:
        unresolved.append('frozen_protocol')
    if not config['independent_review_complete']:
        unresolved.append('independent_review')
    unresolved.extend(['provider_controls_verified', 'live_authorization'])
    cells_per_task = executors * seeds
    primary = tasks * cells_per_task * 5
    aa_increment = aa * cells_per_task * 4
    return {'schema': 1, 'calls_enabled': False, 'launch_ready': False,
            'authorization_status': 'not_requested', 'runner_recipe_support': 'not_verified',
            'tasks': tasks, 'executors': executors, 'seeds_per_executor': seeds,
            'aa_tasks': aa, 'feasibility_tasks': feasibility,
            'primary_calls': primary, 'incremental_aa_calls': aa_increment,
            'confirmatory_calls': primary + aa_increment,
            'feasibility_calls': feasibility * cells_per_task * 5,
            'required_tasks': required_tasks(effect, sd), 'effect': effect, 'task_sd': sd,
            'power_method': 'normal approximation, 80% power, two-sided alpha 0.05',
            'power_caveat': 'Assumes independent task clusters and the supplied standard deviation; not a guarantee.',
            'spend_cap': cap, 'holdout_custodian': custodian, 'unresolved_prerequisites': unresolved}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.config.read_text(encoding='utf-8'))
        print(json.dumps(build_design(config), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f'Error: {type(exc).__name__}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
