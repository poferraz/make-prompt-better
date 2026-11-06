from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tests/skill_contract.py"


class SkillContractTests(unittest.TestCase):
    def test_documented_rewrite_retains_observable_requested_details(self):
        doc = (ROOT / "docs/demo.md").read_text()
        prompt = re.search(r"## Rewritten prompt\n\n```text\n(.*?)\n```", doc, re.S).group(1)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "prompt.txt"
            output.write_text(prompt)
            result = subprocess.run([sys.executable, str(CHECKER), "discount-review", str(output)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_required_patch_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "prompt.txt"
            output.write_text("def discount(price, pct), 0 to 100, signature, one-sentence verdict, two tests, 180 words")
            result = subprocess.run([sys.executable, str(CHECKER), "discount-review", str(output)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("patch", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
