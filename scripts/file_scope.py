#!/usr/bin/env python3
"""Explicit package and review inputs; generated evidence stays out of context."""
import argparse
import json
from pathlib import Path, PurePosixPath
import subprocess

RUNTIME = frozenset({
    'package.json', 'README.md', 'LICENSE', 'bin/cli.mjs', 'install.sh',
    'lint_context.py', 'scripts/lint-prompt.mjs',
    '.claude-plugin/plugin.json', '.claude-plugin/marketplace.json',
    'make-prompt-better/SKILL.md', 'make-prompt-better/agents/openai.yaml',
    'make-prompt-better/references/domain-templates.md',
    'make-prompt-better/references/research-principles.md',
    'make-prompt-better/references/examples.md',
})
REVIEW_DOCS = frozenset({
    'AGENTS.md', 'CLAUDE.md', 'SECURITY.md', 'pyproject.toml', '.coveragerc',
    '.gitignore', '.gitattributes', '.github/dependabot.yml',
    'docs/testing.md', 'docs/benchmark-runs.md', 'docs/continuous-quality.md',
    'docs/installation.md', 'docs/compatibility.md', 'docs/releasing.md',
    'research/benchmark/v4/routing_cases.json',
    'research/benchmark/v4/EVALUATION_PROMPT_V4.md',
    'research/benchmark/v4/checkpoint-migration-hashes.json',
})


def included(path: str, purpose: str) -> bool:
    if purpose not in {'runtime', 'review'}:
        raise ValueError('Purpose must be runtime or review')
    parts = PurePosixPath(path).parts
    if (not parts or path != PurePosixPath(path).as_posix() or path.startswith('/')
            or '..' in parts or '\\' in path):
        return False
    if path in RUNTIME:
        return True
    if purpose == 'runtime':
        return False
    if path in REVIEW_DOCS:
        return True
    parent, suffix = str(PurePosixPath(path).parent), PurePosixPath(path).suffix
    return ((parent == 'scripts' and suffix in {'.py', '.mjs', '.sh', '.command'})
            or (parent == 'tests' and suffix == '.py')
            or (parent == '.github/workflows' and suffix in {'.yml', '.yaml'})
            or (parent == 'research/benchmark/v4' and suffix == '.py')
            or (path.startswith('tests/fixtures/') and suffix == '.json'))


def collect(root: Path, purpose: str) -> list[str]:
    root = root.resolve()
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    selected = []
    for name in sorted(set(filter(None, names))):
        if not included(name, purpose):
            continue
        path = root / name
        if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
            raise ValueError(f'Symlink is not a review input: {name}')
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f'Missing or escaped input: {name}')
        selected.append(name)
    return selected


def codeql_config(root: Path) -> dict:
    # The Python extractor walks every include root with os.listdir, so use a
    # directory root and the complement of our tracked-file allowlist as exclusions.
    selected = set(collect(root, 'review'))
    tracked = set(filter(None, subprocess.check_output(
        ['git', 'ls-files', '-z'], cwd=root).decode().split('\0')))
    excluded = tracked - selected
    excluded.update({'quality-artifacts', 'test-artifacts', '.superpowers', '.worktrees',
                     'research/benchmark/v4/runs', 'research/benchmark/v4/results'})
    return {'name': 'Functional source', 'paths': ['.'], 'paths-ignore': sorted(excluded)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--purpose', choices=['runtime', 'review'], default='review')
    args = parser.parse_args()
    print(json.dumps(collect(args.root, args.purpose), indent=2))
