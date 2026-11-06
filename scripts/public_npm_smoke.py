#!/usr/bin/env python3
"""Verify an exact public npm package without credentials or publishing."""
import argparse
import base64
import binascii
import hashlib
import hmac
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import npm_release as release


def check_integrity(value):
    if not isinstance(value, str) or not value.startswith("sha512-"):
        raise ValueError("Expected a trusted sha512 integrity value")
    try:
        digest = base64.b64decode(value[7:], validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Invalid sha512 integrity value") from exc
    if len(digest) != 64 or base64.b64encode(digest).decode() != value[7:]:
        raise ValueError("Invalid sha512 integrity value")


def run(args, *, cwd, env, expected=0):
    try:
        result = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                                text=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"Could not run {args[0]}: {type(exc).__name__}") from exc
    if result.returncode != expected:
        if args[0] == "npm" and "E404" in result.stderr:
            raise ValueError("npm registry returned 404 for the requested version")
        raise ValueError(f"{args[0]} command failed (exit {result.returncode}, expected {expected})")
    return result.stdout


def verify_installed_files(archive, installed):
    expected = {}
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar:
            if member.isfile():
                name = "/".join(PurePosixPath(member.name).parts[1:])
                expected[name] = tar.extractfile(member).read()
    actual = {}
    if not installed.is_dir() or installed.is_symlink():
        raise ValueError("Installed package directory missing or symlinked")
    for path in installed.rglob("*"):
        if path.is_symlink():
            raise ValueError("Installed package contains a symlink")
        if path.is_file():
            actual[path.relative_to(installed).as_posix()] = path.read_bytes()
        elif not path.is_dir():
            raise ValueError("Installed package contains a special file")
    if actual.keys() != expected.keys() or any(actual[name] != data for name, data in expected.items()):
        raise ValueError("Installed package files differ from the verified archive")


def verified_entrypoint(installed):
    entry = installed.parent / ".bin" / release.NAME
    cli = installed / "bin/cli.mjs"
    if (not entry.is_symlink() or not cli.is_file() or
            entry.resolve() != cli.resolve() or not os.access(entry, os.X_OK)):
        raise ValueError("Installed npm entrypoint is missing, invalid, or not executable")
    return entry


def exercise_installation(installed, project, home, env, tag):
    cli = verified_entrypoint(installed)
    target = project / ".agents/skills" / release.NAME
    version = release.validate_tag(tag)

    def execute(*args, expected=0):
        return run([str(cli), *args], cwd=project, env=env, expected=expected)

    def lifecycle(command, *extra, expected=0):
        return execute(command, "--runtime", "codex", "--project", *extra, expected=expected)

    if execute("--version").strip() != version:
        raise ValueError("Installed CLI version differs from the reviewed version")
    if "Usage:" not in execute():
        raise ValueError("Installed CLI did not show help")
    if (home / ".agents").exists() or target.exists():
        raise ValueError("Package installation or help changed skill directories")
    lifecycle("check", expected=1)
    lifecycle("install", "--copy")
    lifecycle("check", "--copy")
    current = (target / "SKILL.md").read_bytes()
    lifecycle("install", "--copy")
    (target / "SKILL.md").write_bytes(current + b"\nPublic smoke local edit\n")
    lifecycle("check", "--copy", expected=1)
    lifecycle("update", "--copy")
    recovery = list((project / ".make-prompt-better/backups").glob("*/payload/SKILL.md"))
    edited = next((path for path in recovery if path.read_bytes().endswith(b"Public smoke local edit\n")), None)
    if edited is None:
        raise ValueError("Local edit was not preserved in recovery")
    lifecycle("check", "--copy")
    lifecycle("uninstall")
    if target.exists() or (home / ".agents").exists():
        raise ValueError("Uninstall left an active skill or changed the user home")
    shutil.move(str(edited.parent), str(target))
    lifecycle("check", "--copy", expected=1)
    lifecycle("update", "--copy")
    lifecycle("check", "--copy")
    lifecycle("uninstall")
    if target.exists():
        raise ValueError("Restored skill remained after uninstall")


def public_smoke(tag, expected_integrity, *, _registry=release.REGISTRY):
    version = release.validate_tag(tag)
    check_integrity(expected_integrity)
    with tempfile.TemporaryDirectory(prefix="mpb-public-npm-smoke-") as tmp:
        base = Path(tmp).resolve()
        home, project, pack, prefix = (base / name for name in ("home", "project", "pack", "prefix"))
        for directory in (home, project, pack, prefix):
            directory.mkdir()
        user_config, global_config = base / "user.npmrc", base / "global.npmrc"
        user_config.write_text("")
        global_config.write_text("")
        env = {"PATH": os.environ["PATH"], "HOME": str(home), "LANG": "C",
               "npm_config_userconfig": str(user_config), "npm_config_globalconfig": str(global_config),
               "npm_config_fetch_retries": "0", "npm_config_fetch_timeout": "15000"}
        pack_env = dict(env, npm_config_cache=str(base / "pack-cache"))
        name = f"{release.NAME}@{version}"
        output = run(["npm", "pack", name, "--ignore-scripts", "--json", "--pack-destination", str(pack),
                      "--registry", _registry], cwd=project, env=pack_env)
        try:
            metadata = json.loads(output)
            if len(metadata) != 1 or metadata[0].get("name") != release.NAME or metadata[0].get("version") != version:
                raise ValueError("Unexpected package identity from npm pack")
            filename = metadata[0]["filename"]
            if not isinstance(filename, str) or Path(filename).name != filename:
                raise ValueError("Unsafe npm archive filename")
            archive = pack / filename
        except (TypeError, KeyError, IndexError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid npm pack response") from exc
        checked = release.inspect_archive(archive, tag)
        reported_integrity = metadata[0].get("integrity")
        if (not isinstance(reported_integrity, str) or
                not hmac.compare_digest(checked["integrity"], expected_integrity) or
                not hmac.compare_digest(reported_integrity, expected_integrity)):
            raise ValueError("Public package integrity does not match the trusted value")
        install_env = dict(env, npm_config_cache=str(base / "install-cache"))
        run(["npm", "install", name, "--ignore-scripts", "--no-audit", "--no-fund", "--prefix", str(prefix),
             "--registry", _registry], cwd=project, env=install_env)
        installed = prefix / "node_modules" / release.NAME
        verify_installed_files(archive, installed)
        exercise_installation(installed, project, home, install_env, tag)
        return {"name": release.NAME, "version": version, "integrity": expected_integrity,
                "public_install_smoke": "passed", "host_discovery": "not tested by filesystem smoke"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Stable vX.Y.Z release tag")
    parser.add_argument("--integrity", required=True, help="Trusted SHA-512 integrity of the reviewed artifact")
    args = parser.parse_args()
    try:
        print(json.dumps(public_smoke(args.tag, args.integrity), indent=2))
    except (ValueError, OSError, tarfile.TarError) as exc:
        raise SystemExit(f"Public smoke failed: {exc}")


if __name__ == "__main__":
    main()
