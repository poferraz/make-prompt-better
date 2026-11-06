# Your first prompt

You can [try the starter in the README](../README.md#try-it-without-installing) in a normal AI chat. A prompt is simply the request you give the assistant. A skill saves reusable instructions so you can call them again by name.

## Install the full skill

Use the source route below to install without a publisher token. For other distribution routes and their verification status, see the [distribution guide](npm-publishing.md).

The commands select [v4.5.0](https://github.com/poferraz/make-prompt-better/releases/tag/v4.5.0) for a repeatable source installation. A GitHub release does not publish an npm package; public npm installation remains unverified.

Choose one route and one scope. A user installation works across your projects; a project installation belongs to one repository. Installing both can produce two entries in a host that loads both scopes.

### With help from your coding agent

Copy the [installation request](../README.md#let-your-coding-agent-help) into the agent where you want the skill. It should identify the host, inspect the installer, install the appropriate target, and show its check result. This route requires an agent with repository and terminal access; a text-only chat can use the starter instead.

A successful filesystem check says:

```text
Check passed. Selected installations match this checkout; no duplicate entries in the checked roots.
```

This confirms files in the selected locations. Next, open the skill picker and confirm that the host can actually load the skill. A filesystem check alone cannot establish that.

### With a terminal

A terminal is the app where you run the commands below. Git downloads the repository. Bash runs its installer. On Windows, use a WSL terminal; native PowerShell installation is untested.

```bash
git clone --branch v4.5.0 --depth 1 https://github.com/poferraz/make-prompt-better.git
cd make-prompt-better
./install.sh --runtime codex --dry-run
./install.sh --runtime codex
./install.sh --runtime codex --check
```

The first installer command previews changes. Replace `codex` with your host: `claude`, `cursor`, `gemini`, `antigravity`, or `qwen`. These commands install for your user account. For a single project, follow the [project installation instructions](installation.md#choose-a-scope-and-host). You do not need Node or Python for the source installer.

The [Node CLI guide](installation.md#node-cli) describes commands available in checkouts and packages that include them. Commands vary by version; run `node bin/cli.mjs --help` from your checkout to see its options.

## Invoke it

In Codex, type `$make-prompt-better` and select the skill. If the picker has stale entries, restart Codex. Other hosts have their own invocation syntax. Try:

```text
$make-prompt-better Improve this prompt without answering it. Return only
the rewritten prompt:

Write a friendly customer email about a one-day shipping delay. Orders will
arrive Friday instead of Thursday. Apologize, stay under 100 words, and
don't offer a discount.
```

Check that the rewrite keeps Friday, Thursday, the one-day delay, a friendly tone, the apology, the word limit, and the restriction on discounts. Then paste that reviewed prompt into your assistant to produce the email.

The example explains the intended flow; it does not establish consistent outcomes across hosts or models. If the assistant answers the email request immediately, repeat "rewrite the request without answering it" and check that the skill was selected.

## Build confidence with your own work

Start with a short request whose details you know. Add the documents or code you want the assistant to use. Say what you need back and what must stay unchanged. For consequential decisions, verify the resulting answer using the appropriate sources, tests, and expertise.

If the skill is too wordy, ask for "only the rewritten prompt" or use the direct request. [When to skip optimization](when-to-use.md) · [Get help](../SUPPORT.md).
