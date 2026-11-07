# Your first prompt

You can [try the starter in the README](../README.md#try-it-without-installing) in a normal AI chat. A prompt is simply the request you give the assistant. A skill saves reusable instructions so you can call them again by name.

## Install the full skill

This v4.5.1 release snapshot includes the guided installer. From this checkout, run `node bin/cli.mjs` in a terminal. Check the [current distribution status](https://github.com/poferraz/make-prompt-better/blob/main/docs/npm-publishing.md); after v4.5.1 is published and publicly verified, start the same guide with:

```bash
npx make-prompt-better
```

You need Node.js 22+ and Bash. Choose your coding agent and whether the skill should be available in this project or across your user account. Enter a number or name; `q` cancels. The guide installs a copy, verifies it, and prints the next step. No publisher token is needed.

Choose one route and one scope. A user installation works across your projects; a project installation belongs to one repository. Installing both can produce two entries in a host that loads both scopes.

A successful filesystem check says:

```text
Check passed. Selected installations match this checkout; no duplicate entries in the checked roots.
```

This confirms files in the selected locations. Next, open the skill picker and confirm that the host can actually load the skill. A filesystem check alone cannot establish that.

### Previously verified npm release: v4.5.0

Public npm 4.5.0 has passed installation checks. Its bare command shows help, so use:

```bash
npx --yes make-prompt-better@4.5.0 install --runtime codex --global --copy
npx --yes make-prompt-better@4.5.0 check --runtime codex --global --copy
```

Replace `codex` with your host: `claude`, `cursor`, `gemini`, `antigravity`, or `qwen`. These commands install for your user account. For one project, run them inside that project and replace `--global` with `--project`. Choose one scope. `--yes` accepts npm's execution prompt; copy mode keeps the skill after the npm cache is cleared. [Update, uninstall, and recovery](installation.md).

### From source

A terminal is the app where you run the commands below. Git downloads the repository. Bash runs its installer. On Windows, use a WSL terminal; native PowerShell installation is untested.

After the [v4.5.1 source release](https://github.com/poferraz/make-prompt-better/releases/tag/v4.5.1) exists, run the commands below. To select the previous source release, substitute `v4.5.0`.

```bash
git clone --branch v4.5.1 --depth 1 https://github.com/poferraz/make-prompt-better.git
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
