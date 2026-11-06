#!/usr/bin/env python3
"""Check a few literal requirements in a supplied example, not model safety or correctness."""
import argparse
import json
from pathlib import Path
import re
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    cases = json.loads((Path(__file__).parent / "fixtures/skill-contract/cases.json").read_text())
    if args.case not in cases:
        print(f"Unknown case: {args.case}", file=sys.stderr)
        return 1
    try:
        output = args.output.read_text()
    except OSError as exc:
        print(f"Cannot read output: {exc}", file=sys.stderr)
        return 1
    missing = [name for name, pattern in cases[args.case]["requirements"].items()
               if not re.search(pattern, output, re.I)]
    if missing:
        print(f"Missing observable details: {', '.join(missing)}", file=sys.stderr)
        return 1
    print("Observable details found; semantic correctness and host behavior remain unverified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
