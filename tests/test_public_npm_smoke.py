"""Public install verification against a disposable local npm registry fixture."""
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("public_npm_smoke", ROOT / "scripts/public_npm_smoke.py")
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


class RegistryFixture:
    def __init__(self, archive, metadata, *, missing=False, tamper_second_download=False):
        self.archive = archive
        self.metadata = metadata
        self.missing = missing
        self.tamper_second_download = tamper_second_download
        self.downloads = 0
        self.requests = []
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                fixture.requests.append((self.path, dict(self.headers)))
                if fixture.missing:
                    self.send_error(404)
                    return
                if self.path.split("?")[0] == "/make-prompt-better":
                    body = json.dumps(fixture.document()).encode()
                    kind = "application/json"
                elif self.path.split("?")[0] == "/make-prompt-better/-/package.tgz":
                    fixture.downloads += 1
                    body = fixture.archive
                    if fixture.tamper_second_download and fixture.downloads > 1:
                        body += b"untrusted modification"
                    kind = "application/octet-stream"
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", kind)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server.server_port}"

    def document(self):
        version = self.metadata["version"]
        manifest = dict(self.metadata)
        manifest["_id"] = f"make-prompt-better@{version}"
        manifest["dist"] = {"tarball": self.url + "/make-prompt-better/-/package.tgz",
                            "integrity": self.integrity}
        return {"name": "make-prompt-better", "dist-tags": {"latest": version},
                "versions": {version: manifest}}

    @property
    def integrity(self):
        return "sha512-" + base64.b64encode(hashlib.sha512(self.archive).digest()).decode()

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_args):
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()


class PublicRegistrySmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="mpb-public-fixture-")
        root = Path(cls.tmp.name)
        env = {"PATH": os.environ["PATH"], "HOME": str(root),
               "npm_config_cache": str(root / "cache"), "npm_config_userconfig": str(root / "empty.npmrc"),
               "npm_config_globalconfig": str(root / "global.npmrc")}
        Path(env["npm_config_userconfig"]).write_text("")
        Path(env["npm_config_globalconfig"]).write_text("")
        packed = subprocess.run(["npm", "pack", "--ignore-scripts", "--json", "--pack-destination", str(root)],
                                cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
        if packed.returncode:
            raise RuntimeError(packed.stderr)
        result = json.loads(packed.stdout)[0]
        cls.archive = (root / result["filename"]).read_bytes()
        cls.metadata = json.loads((ROOT / "package.json").read_text())
        cls.tag = "v" + cls.metadata["version"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_real_npm_registry_install_and_recovery_without_inherited_credentials(self):
        with RegistryFixture(self.archive, self.metadata) as registry, tempfile.TemporaryDirectory() as home:
            sentinel = Path(home) / ".npmrc"
            fixture_config = f"{registry.url.removeprefix('http:')}/:_authToken=fixture-not-a-secret\n"
            sentinel.write_text(fixture_config)
            with patch.dict(os.environ, {"HOME": home, "NODE_AUTH_TOKEN": "fixture-not-a-secret",
                                        "NPM_TOKEN": "fixture-not-a-secret",
                                        "npm_config_userconfig": str(sentinel)}):
                result = smoke.public_smoke(self.tag, registry.integrity, _registry=registry.url)
            self.assertEqual(result["public_install_smoke"], "passed")
            self.assertEqual(result["integrity"], registry.integrity)
            self.assertEqual(result["host_discovery"], "not tested by filesystem smoke")
            self.assertTrue(any("package.tgz" in path for path, _ in registry.requests))
            self.assertTrue(all(not any(k.lower() == "authorization" for k in headers)
                                for _, headers in registry.requests))
            self.assertEqual(sentinel.read_text(), fixture_config)
            self.assertEqual(sorted(p.name for p in Path(home).iterdir()), [".npmrc"])

    def test_wrong_integrity_fails_before_install_or_package_execution(self):
        with RegistryFixture(self.archive, self.metadata) as registry:
            wrong = "sha512-" + base64.b64encode(b"x" * 64).decode()
            with patch.object(smoke, "exercise_installation", side_effect=AssertionError("executed package")):
                with self.assertRaisesRegex(ValueError, "integrity"):
                    smoke.public_smoke(self.tag, wrong, _registry=registry.url)

    def test_missing_package_fails_without_install_or_package_execution(self):
        with RegistryFixture(self.archive, self.metadata, missing=True) as registry:
            with patch.object(smoke, "exercise_installation", side_effect=AssertionError("executed package")):
                with self.assertRaisesRegex(ValueError, "registry|npm pack"):
                    smoke.public_smoke(self.tag, registry.integrity, _registry=registry.url)

    def test_changed_registry_download_fails_before_package_execution(self):
        with RegistryFixture(self.archive, self.metadata, tamper_second_download=True) as registry:
            with patch.object(smoke, "exercise_installation", side_effect=AssertionError("executed package")):
                with self.assertRaisesRegex(ValueError, "npm command failed|[Ii]nstalled"):
                    smoke.public_smoke(self.tag, registry.integrity, _registry=registry.url)
            self.assertGreaterEqual(registry.downloads, 2)

    def test_tampered_installed_file_is_rejected_before_package_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "package.tgz"
            archive.write_bytes(self.archive)
            unpacked = root / "package"
            unpacked.mkdir()
            import tarfile
            with tarfile.open(archive, "r:gz") as tar:
                for member in tar:
                    if member.isfile():
                        target = unpacked.joinpath(*Path(member.name).parts[1:])
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(tar.extractfile(member).read())
            (unpacked / "bin/cli.mjs").write_text("tampered")
            with self.assertRaisesRegex(ValueError, "[Ii]nstalled"):
                smoke.verify_installed_files(archive, unpacked)

    def test_invalid_integrity_rejected_before_registry_access(self):
        with RegistryFixture(self.archive, self.metadata) as registry:
            with self.assertRaisesRegex(ValueError, "integrity"):
                smoke.public_smoke(self.tag, "sha512-not-valid", _registry=registry.url)
            self.assertEqual(registry.requests, [])

    def test_broken_or_redirected_bin_entrypoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            modules = Path(tmp) / "node_modules"
            installed = modules / "make-prompt-better"
            (installed / "bin").mkdir(parents=True)
            cli = installed / "bin/cli.mjs"
            cli.write_text("#!/usr/bin/env node\n")
            cli.chmod(0o755)
            bindir = modules / ".bin"
            bindir.mkdir()
            link = bindir / "make-prompt-better"
            link.symlink_to("../other/bin/cli.mjs")
            with self.assertRaisesRegex(ValueError, "entrypoint"):
                smoke.verified_entrypoint(installed)
            link.unlink()
            link.symlink_to("../make-prompt-better/bin/cli.mjs")
            self.assertEqual(smoke.verified_entrypoint(installed), link)

    def test_unavailable_registry_fails_without_running_package(self):
        with RegistryFixture(self.archive, self.metadata) as registry:
            url = registry.url
        with patch.object(smoke, "exercise_installation", side_effect=AssertionError("executed package")):
            with self.assertRaisesRegex(ValueError, "npm command failed"):
                smoke.public_smoke(self.tag, registry.integrity, _registry=url)


if __name__ == "__main__":
    unittest.main()
