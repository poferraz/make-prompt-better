#!/usr/bin/env python3
"""Run the repository's structural checks without installing or changing files."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CORE_FILES = (
    'make-prompt-better/SKILL.md',
    'make-prompt-better/references/domain-templates.md',
    'make-prompt-better/references/research-principles.md',
    'make-prompt-better/references/examples.md',
    'docs/methodology.md', 'docs/tradeoffs.md', 'docs/when-to-use.md',
    'docs/task-classification.md', 'README.md', 'CLAUDE.md', 'AGENTS.md',
    'research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md',
)


def validate(root=ROOT):
    skill = (root / 'make-prompt-better/SKILL.md').read_text(encoding='utf-8')
    frontmatter = re.match(
        r'^---\nname: make-prompt-better\ndescription: "(Use when [^\n:\"]+)"\n---\n', skill)
    if not frontmatter or len(frontmatter.group(1)) >= 450:
        raise ValueError('Frontmatter must match the agent contract')
    if len(skill.splitlines()) >= 500:
        raise ValueError('SKILL.md must be under 500 lines')
    templates = (root / 'make-prompt-better/references/domain-templates.md').read_text(encoding='utf-8')
    if len(re.findall(r'^## \d+\. .+$', templates, re.M)) != 12:
        raise ValueError('Exactly 12 domain templates are required')
    for name in CORE_FILES:
        path = root / name
        content = path.read_text(encoding='utf-8')
        if re.search(r'[\u2014\u2013]', content):
            raise ValueError(f'Em/en dash in {name}')
        content = re.sub(r'```.*?```', '', content, flags=re.S)
        for raw in re.findall(r'\[[^\]]+\]\(([^)]+)\)', content):
            target = raw.strip().split()[0]
            if target.startswith(('http://', 'https://', 'mailto:', '#')):
                continue
            file_part = target.split('#', 1)[0]
            if file_part and not (path.parent / file_part).exists():
                raise ValueError(f'Broken relative link in {name}: {raw}')
    return 'VALIDATED OK: frontmatter, skill size, templates, punctuation, and local links'


if __name__ == '__main__':
    try:
        print(validate())
    except (ValueError, OSError) as error:
        raise SystemExit(f'Validation failed: {error}')
