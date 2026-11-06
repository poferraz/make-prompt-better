# Example: rewrite a code-review request

This example was produced in the current Codex conversation on 2026-11-06 by applying the working repository's skill instructions. It is an illustration of one rewrite, not an independently repeated host-discovery test or a benchmark. No code or tests were executed as part of this example.

## Input

> Improve this prompt without answering it: Review `def discount(price, pct): return price - price * pct`. Treat `pct` as a percentage from 0 to 100. Preserve the signature. Put a one-sentence verdict first, then a patch and two tests. Keep the result under 180 words.

## Rewritten prompt

```text
Review the following Python function. The caller supplies pct as a percentage
from 0 to 100, and the function signature must remain unchanged.

def discount(price, pct): return price - price * pct

Check the calculation against that percentage convention. Present the result
in this order:
1. A one-sentence verdict.
2. A corrected patch that preserves discount(price, pct).
3. Two tests that cover the relevant percentage behavior.

Keep the entire response under 180 words. If the tests are not executed,
identify them as unrun rather than reporting them as passing.
```

## What was checked

The rewrite contains the original function, percentage range, signature requirement, requested output order, patch, two tests, and word limit. That is a manual check of this example only. It does not prove that every model or host preserves every requirement.
