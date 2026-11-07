#!/usr/bin/env python3
"""Check npm release evidence and archives; this tool never publishes a package."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile
import urllib.error
import urllib.request

try:
    from file_scope import included
except ModuleNotFoundError:
    from scripts.file_scope import included

NAME = 'make-prompt-better'
REPOSITORY = 'git+https://github.com/poferraz/make-prompt-better.git'
REGISTRY = 'https://registry.npmjs.org'
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024
EXECUTABLES = {'bin/cli.mjs', 'install.sh', 'lint_context.py'}
REQUIRED_FILES = EXECUTABLES | {
    'package.json', 'README.md', 'LICENSE', 'scripts/lint-prompt.mjs',
    'make-prompt-better/SKILL.md', 'make-prompt-better/agents/openai.yaml',
    'make-prompt-better/references/domain-templates.md',
    'make-prompt-better/references/research-principles.md',
    'make-prompt-better/references/examples.md',
}
LIFECYCLE_HOOKS = {'preinstall', 'install', 'postinstall', 'prepare', 'prepublish',
                   'prepublishOnly', 'prepack', 'postpack', 'publish', 'postpublish'}
CREDENTIAL = re.compile(rb'npm_[A-Za-z0-9]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_tag(tag):
    require(re.fullmatch(r'v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', tag), 'A stable vX.Y.Z tag is required')
    return tag[1:]


def validate_release(tag, commit, release, runs):
    version = validate_tag(tag)
    require(re.fullmatch('[0-9a-f]{40}', commit), 'Invalid source commit')
    require(release.get('tag_name') == tag and release.get('draft') is False
            and release.get('prerelease') is False and release.get('published_at'),
            'A published stable GitHub release for this tag is required')
    # gh --paginate --slurp supplies pages. Keep single-page fixtures compatible.
    pages = runs if isinstance(runs, list) else [runs]
    require(pages and all(isinstance(page, dict) and isinstance(page.get('workflow_runs'), list)
                          for page in pages), 'Malformed workflow-run evidence')
    all_runs = [run for page in pages for run in page['workflow_runs']]
    require(all(isinstance(run, dict) and type(run.get('id')) is int and run['id'] > 0
                and type(run.get('run_attempt', 1)) is int and run.get('run_attempt', 1) > 0
                for run in all_runs), 'Invalid workflow-run identity or attempt')
    count = len({run['id'] for run in all_runs})
    require(all(type(page.get('total_count', count)) is int
                and 0 <= page.get('total_count', count) <= count for page in pages),
            'Incomplete workflow-run evidence; retrieve every page')
    matching = [run for run in all_runs
                if run.get('path') == '.github/workflows/validate-skill.yml'
                and run.get('head_sha') == commit and run.get('event') == 'push'
                and run.get('head_branch') == 'main']
    require(matching, 'No exact-commit main validation run found')
    identity = lambda run: (run['id'], run.get('run_attempt', 1))
    newest = max(map(identity, matching))
    latest = [run for run in matching if identity(run) == newest]
    require(all(run.get('status') == 'completed' and run.get('conclusion') == 'success' for run in latest),
            'Latest exact-commit main validation must succeed')
    return version


def sensitive_path(name):
    for part in PurePosixPath(name).parts:
        if (part in {'.npmrc', '.git', '.env', '.make-prompt-better', 'node_modules', '__pycache__'}
                or part.startswith('.env.') or part.endswith(('.pem', '.key', '.p12', '.pyc'))):
            return True
    return name.startswith(('tests/', 'test-artifacts/', 'research/benchmark/v4/runs/', '.github/workflows/'))


def inspect_archive(archive, tag):
    version = validate_tag(tag)
    archive = Path(archive)
    require(archive.stat().st_size <= MAX_TOTAL_BYTES, 'Compressed archive exceeds the size limit')
    files = {}
    total = 0
    with tarfile.open(archive, 'r:gz') as tar:
        for index, member in enumerate(tar):
            require(index < 500, 'Too many archive entries')
            parts = PurePosixPath(member.name).parts
            require(parts and parts[0] == 'package' and '..' not in parts
                    and not member.name.startswith('/'), 'Unsafe archive path')
            require(member.isfile() or member.isdir(), 'Archive links and special files are prohibited')
            if member.isdir():
                continue
            name = '/'.join(parts[1:])
            require(name and name not in files and not sensitive_path(name), 'Duplicate or sensitive archive path')
            require(included(name, 'runtime'), 'Non-runtime archive file')
            total += member.size
            require(0 <= member.size <= MAX_FILE_BYTES and total <= MAX_TOTAL_BYTES, 'Archive exceeds the size limit')
            content = tar.extractfile(member).read()
            require(not CREDENTIAL.search(content), 'Credential-shaped content found in archive')
            require(name not in EXECUTABLES or member.mode & 0o111, 'Package executable lost its execute permission')
            files[name] = content
    require(REQUIRED_FILES <= files.keys(), 'Required package files are missing')
    package = json.loads(files['package.json'])
    require(package.get('name') == NAME and package.get('version') == version, 'Package identity/version mismatch')
    require(package.get('repository', {}).get('url') == REPOSITORY, 'Package repository mismatch')
    require(package.get('publishConfig') == {'registry': REGISTRY, 'access': 'public'}, 'Explicit public npm publishConfig required')
    require(not LIFECYCLE_HOOKS.intersection(package.get('scripts', {})), 'Lifecycle scripts are prohibited')
    require(not any(package.get(key) for key in ('dependencies', 'optionalDependencies', 'bundledDependencies', 'bundleDependencies')), 'Review required before adding runtime dependencies')
    require(package.get('bin') == {NAME: './bin/cli.mjs', 'lint-context': './lint_context.py'}, 'Unexpected package executables')
    allowlist = package.get('files', []) + ['package.json']
    require(all(isinstance(item, str) and item and '..' not in PurePosixPath(item).parts
                and not item.startswith('/') for item in allowlist), 'Invalid package file allowlist')
    require(all(any(name == item or name.startswith(item.rstrip('/') + '/') for item in allowlist)
                for name in files), 'Unlisted archive file')
    require(f'# Make Prompt Better ({tag})'.encode() in files['make-prompt-better/SKILL.md'], 'Skill version mismatch')
    data = archive.read_bytes()
    return {'name': NAME, 'version': version, 'tag': tag, 'files': len(files),
            'sha256': hashlib.sha256(data).hexdigest(),
            'integrity': 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode()}


def registry_version(version):
    validate_tag('v' + version)
    request = urllib.request.Request(f'{REGISTRY}/{NAME}/{version}', headers={'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(1024 * 1024 + 1)
            require(len(raw) <= 1024 * 1024, 'Registry response exceeds the size limit')
            return json.loads(raw)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def check_registry(tag, expected_integrity=None):
    version = validate_tag(tag)
    data = registry_version(version)
    if expected_integrity is None:
        require(data is None, 'This npm version already exists; publish a new version')
    else:
        require(data and data.get('name') == NAME and data.get('version') == version
                and data.get('dist', {}).get('integrity') == expected_integrity,
                'Published package identity or integrity does not match the verified artifact')


def smoke_archive(archive, tag):
    metadata = inspect_archive(archive, tag)
    with tempfile.TemporaryDirectory(prefix='mpb npm smoke ') as tmp:
        base = Path(tmp).resolve()
        user_dir, project = base / 'home', base / 'project'
        user_dir.mkdir()
        project.mkdir()
        config = base / 'empty.npmrc'
        config.write_text('')
        env = {'PATH': os.environ['PATH'], 'HOME': str(user_dir), 'LANG': 'en_US.UTF-8',
               'npm_config_userconfig': str(config), 'npm_config_cache': str(base / 'cache')}
        if 'NODE_V8_COVERAGE' in os.environ:
            env['NODE_V8_COVERAGE'] = os.environ['NODE_V8_COVERAGE']
        def run(*args, expected=0):
            result = subprocess.run(args, cwd=project, env=env, capture_output=True, text=True, timeout=60)
            require(result.returncode == expected, f'Smoke command failed: {args[0]} (exit {result.returncode})')
            return result.stdout
        run('npm', 'install', '--ignore-scripts', '--no-audit', '--no-fund', '--prefix', str(base), str(Path(archive).resolve()))
        installed = base / 'node_modules' / NAME
        cli = installed / 'bin/cli.mjs'
        require(not (user_dir / '.agents').exists(), 'npm installation modified skill folders')
        require(run('node', str(cli), '--version').strip() == metadata['version'], 'Packaged CLI version mismatch')
        require('Usage:' in run('node', str(cli)), 'Bare CLI must show help')
        require(not (user_dir / '.agents').exists() and not (project / '.agents').exists(), 'Bare CLI modified skill folders')
        target = project / '.agents/skills' / NAME
        def init(*args, expected=0):
            return run('node', str(cli), 'init', '--project', '--runtime', 'codex', '--copy', *args, expected=expected)
        def lifecycle(command, *args, expected=0):
            return run('node', str(cli), command, '--project', '--runtime', 'codex', '--copy', *args, expected=expected)
        init('--check', expected=1)
        lifecycle('install')
        lifecycle('install')
        lifecycle('check')
        init()
        init('--check')
        for root in ('.agents/skills', '.codex/skills'):
            for suffix in ('', '.bak.one', '.bak.two'):
                old = project / root / (NAME + suffix)
                old.mkdir(parents=True, exist_ok=True)
                (old / 'SKILL.md').write_text('---\nname: make-prompt-better\ndescription: "Legacy fixture"\n---\n')
                (old / 'keep.txt').write_text(root + suffix)
        lifecycle('check', expected=1)
        update_output = lifecycle('update')
        require(metadata['version'] in update_output and 'no version is fetched' in update_output,
                'Update must report its source version and no-fetch behavior')
        init('--check')
        backups = list((project / '.make-prompt-better/backups').glob('*/payload/keep.txt'))
        require(len(backups) == 6 and len({p.read_text() for p in backups}) == 6, 'Legacy payloads were not preserved')
        require(len(list((project / '.agents/skills').glob('*/SKILL.md'))) == 1
                and not list((project / '.codex/skills').glob('*/SKILL.md')), 'Duplicate skill files remain')
        init('--unknown', expected=1)
        current = (target / 'SKILL.md').read_bytes()
        (target / 'SKILL.md').write_bytes(current + b'\nLocal edit\n')
        lifecycle('check', expected=1)
        lifecycle('update')
        require(any((p / 'SKILL.md').read_bytes().endswith(b'Local edit\n')
                    for p in (project / '.make-prompt-better/backups').glob('*/payload')), 'Local edit lost')
        moved = base / 'moved-package'
        installed.rename(moved)
        cli = moved / 'bin/cli.mjs'
        require(not target.is_symlink() and (target / 'SKILL.md').read_bytes() == current, 'Copy depends on package/cache location')
        lifecycle('check')
        lifecycle('uninstall')
        require(not target.exists(), 'Uninstall left an active copy')
        init()
        init('--uninstall')
        require(not target.exists(), 'Legacy uninstall left an active copy')
        require(not (user_dir / '.agents').exists(), 'Project install changed user skills')
    return {'package_smoke': 'passed', 'host_discovery': 'not tested by filesystem smoke'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('audit', 'smoke'):
        command = sub.add_parser(name)
        command.add_argument('archive', type=Path)
        command.add_argument('--tag', required=True)
    command = sub.add_parser('release')
    for name in ('tag', 'commit', 'release-file', 'runs-file'):
        command.add_argument('--' + name, required=True)
    command = sub.add_parser('registry')
    command.add_argument('--tag', required=True)
    command.add_argument('--integrity')
    args = parser.parse_args()
    if args.command == 'audit':
        result = inspect_archive(args.archive, args.tag)
    elif args.command == 'smoke':
        result = smoke_archive(args.archive, args.tag)
    elif args.command == 'registry':
        check_registry(args.tag, args.integrity)
        result = {'registry_check': 'matching artifact' if args.integrity else 'version absent; ownership unverified'}
    else:
        version = validate_release(args.tag, args.commit, json.loads(Path(args.release_file).read_text()),
                                   json.loads(Path(args.runs_file).read_text()))
        result = {'version': version, 'commit': args.commit, 'release_check': 'passed'}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, tarfile.TarError, urllib.error.URLError) as error:
        raise SystemExit(f'Check failed: {error}')
