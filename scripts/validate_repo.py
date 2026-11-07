#!/usr/bin/env python3
"""Run the repository's structural checks without installing or changing files."""
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CORE_FILES = (
    'make-prompt-better/SKILL.md',
    'make-prompt-better/references/domain-templates.md',
    'make-prompt-better/references/research-principles.md',
    'make-prompt-better/references/examples.md',
    'docs/installation.md', 'docs/quickstart.md', 'docs/compatibility.md',
    'docs/demo.md', 'docs/testing.md', 'docs/releasing.md',
    'docs/npm-publishing.md', 'docs/benchmark-runs.md', 'docs/continuous-quality.md',
    'README.md', 'CLAUDE.md', 'AGENTS.md', 'SUPPORT.md', 'SECURITY.md',
    'CHANGELOG.md', 'CODE_OF_CONDUCT.md', '.github/CONTRIBUTING.md',
)


def validate(root=ROOT):
    root = Path(root).resolve()
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
            if target.startswith(('mailto:', '#')):
                continue
            url = urlsplit(target)
            if url.scheme in {'http', 'https'}:
                prefixes = {
                    'github.com': '/poferraz/make-prompt-better/blob/main/',
                    'raw.githubusercontent.com': '/poferraz/make-prompt-better/main/',
                }
                prefix = prefixes.get(url.netloc)
                if not prefix or not url.path.startswith(prefix):
                    continue
                linked = root / unquote(url.path[len(prefix):])
            else:
                linked = path.parent / unquote(url.path)
            linked = linked.resolve()
            if not linked.is_relative_to(root) or '.private' in linked.relative_to(root).parts:
                raise ValueError(f'Nonpublic link in {name}: {raw}')
            if not linked.exists():
                raise ValueError(f'Broken relative link in {name}: {raw}')
    return 'VALIDATED OK: frontmatter, skill size, templates, punctuation, and local links'


if __name__ == '__main__':
    try:
        print(validate())
    except (ValueError, OSError) as error:
        raise SystemExit(f'Validation failed: {error}')
