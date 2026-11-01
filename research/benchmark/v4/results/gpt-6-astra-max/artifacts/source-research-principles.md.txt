# Research Principles Index

Quick reference for explaining why specific optimization decisions were made. Each entry maps a research paper to its actionable constraint on prompt, context, and harness design.

---

## [META] Semi-Formal Reasoning (Ugare & Chandra, 2026)
arXiv: 2603.01896

**Finding:** Structured reasoning templates (premises, traces, conclusion) improved accuracy 10 to 15 percentage points across code analysis tasks (78% to 88% on curated patch equivalence, 93% on real-world patches, 78% to 87% on code QA, +5 to 12 pp on Top-5 fault localization) by preventing the model from skipping cases or making unsupported claims. Cross-architecture benchmarking shows an average token overhead of ~2.2x for a +25.9% relative improvement.

**Constraint:** Every optimized analytical prompt must include the certificate structure. The model states premises before tracing, and traces before concluding. Conclusions must reference traces by identifier.

**When to cite:** Explaining why the prompt has a structured certificate scaffold.

---

## [GOAL-BLIND] Purpose-Conditioned Cognition (Cao, Jiang & Xu, 2026)
arXiv: 2602.09504

**Finding:** Telling an LLM how its output will be used (for example, "this will predict stock returns" or "we need to pass tomorrow's client demo") causes the model to reshape intermediate outputs toward the disclosed goal. In-sample performance improved, but out-of-sample generalization degraded. The effect disappeared after the model's knowledge cutoff, confirming exploitation of training correlations rather than genuine signal improvement.

**Constraint:** Omit evaluation criteria, downstream use cases, business stakes, and success metrics from the prompt. Specify what to measure, trace, or build, never why or how the result will be judged downstream.

**When to cite:** Explaining why language like "this will be used to...", "the goal is to predict...", or "we are a small startup negotiating with..." was removed from the prompt.

---

## [ACE] Agentic Context Engineering (Zhang, Hu et al., 2026)
arXiv: 2510.04618 (ICLR 2026)

**Finding:** Contexts perform best as structured, itemized playbooks with unique identifiers per entry. Two failure modes degrade prompts: brevity bias (optimization collapses to short generic instructions that omit domain specifics) and context collapse (iterative full rewrites erode accumulated detail). Incremental delta updates outperform full rewrites (+10.6% on agent tasks, +8.6% on finance benchmarks, 86.9% lower adaptation latency).

**Constraint:** Use numbered identifiers (`[P1]`, `[T1]`) for every premise and trace so conclusions can cross-reference them. Prefer explicit domain detail over generic brevity in task certificates. When iterating across sessions, make targeted delta edits rather than rewriting the whole prompt.

**When to cite:** Explaining why premises and traces have `[P1]` and `[T1]` identifiers, or why iterative updates use delta edits.

---

## [HIERARCHY] Instruction Hierarchy Failure (Geng et al., 2025)
arXiv: 2502.15851 (AAAI 2026)

**Finding:** System/user prompt separation achieves only 9.6% to 45.8% compliance on conflicting constraints. Societal hierarchy framings achieve 54% to 77.8% compliance: consensus ("90% of experts recommend...") is strongest, expertise ("peer-reviewed methodology requires...") is second, and authority ("leadership requires...") is third. Models also exhibit strong inherent biases toward lowercase text, longer outputs, and keyword avoidance.

**Constraint:** Frame the certificate structure using expertise or consensus language ("The standard analytical protocol requires...") rather than relying on system message placement alone. Reinforce constraints that fight model defaults, especially length caps and brevity constraints.

**When to cite:** Explaining why the preamble uses phrases like "established methodology requires" instead of "please fill out this template."

---

## [CODE-SMELLS] LLM Code Smells (Mahmoudi et al., 2025)
arXiv: 2512.18020

**Finding:** 60.5% of 200 audited open-source LLM systems have integration code smells. Most relevant is "No Structured Output" (40.5% prevalence): when LLM outputs are parsed downstream without enforced schemas, silent failures occur from schema drift, missing fields, and type mismatches. Other common smells include unbounded max tokens (38%), no model version pinning (36%), no system message (34.5%), and unset temperature (36.5%).

**Constraint:** When the optimized prompt's output will be parsed programmatically or piped into another tool, add an explicit JSON schema or typed output specification alongside the certificate. The certificate is the reasoning scaffold; the output format is the delivery contract.

**When to cite:** Explaining why a JSON schema wrapper was added for pipeline or API prompts.

---

## [PRISM] Persona Effects (Hu, Rostami & Thomason, 2026)
arXiv: 2603.18507

**Finding:** Expert persona prompts help alignment-dependent tasks (format following, safety, style: +0.4 to +0.65 on MT-Bench categories) but damage accuracy-dependent tasks (MMLU drops from 71.6% to 66.3% to 68.0%). Longer personas damage accuracy more. Minimal personas ("You are a data analyst." at 5 words or fewer) limit accuracy damage on mixed tasks. Reasoning-distilled models (such as DeepSeek-R1 or o-series variants) benefit from context detail rather than persona identity.

**Constraint:** Classify each task before adding persona:
- Accuracy task (fact retrieval, classification, math, code verification): omit persona
- Alignment task (format, style, safety, tone): include full persona
- Mixed task: use minimal persona (5 words or fewer)
- Reasoning-distilled model: omit persona

**When to cite:** Explaining why an identity or persona line was omitted, capped at 5 words, or expanded.

---

## [VS] Verbalized Sampling for Diversity (Zhang, Yu, Chong, Sicilia, Tomz, Manning & Shi, 2025)
arXiv: 2510.01171

**Finding:** Post-training alignment (RLHF, DPO) induces mode collapse driven by typicality bias in human preference data, where annotators systematically favor familiar, prototypical responses. Prompting the model to verbalize a probability or typicality distribution over a set of candidate responses (for example, generating 3 to 5 distinct candidates with estimated typicality probabilities and sampling from the lower-typicality tail) circumvents mode collapse without sacrificing accuracy or safety. In creative writing, dialogue simulation, and open-ended synthesis, Verbalized Sampling increases output diversity by 1.6x to 2.1x, with larger gains on more capable models.

**Constraint:** For creative, editorial, brainstorming, and multi-hypothesis prompts, include a backstage `[NT0] Verbalized Distribution Sampling` trace that enumerates 3 to 5 structurally distinct candidate angles with estimated typicality probabilities (`p`), then selects the strongest low-typicality angle (`p < 0.25`) that satisfies all premises.

**When to cite:** Explaining why creative or divergent prompts generate multiple probability-weighted candidate angles before drafting the final piece.

---

## [SLOPSHAPE] Structural Signatures of AI Writing (Madler, 2026; Russell et al., 2026)
arXiv: 2609.15369

**Finding:** Word-level AI detectors collapse under paraphrasing (DetectGPT drops from 70.3% to 4.6%), but discourse-level structural features detect AI commercial writing at 98.0 macro-F1 (and 98.1 after full self-rewording; StoryScope found 93.2 macro-F1 on fiction). Just 10 core structural features achieve 93.5 macro-F1. AI writing crowds into a "tidy, self-announcing shape" (mean structural rarity percentile 0.435 vs. human 0.838, Cohen's `d = 1.83`): promising the payoff in the title (`PUR_OUT_003`), stating the thesis before the first section (`STR_FLW_006`), setting up a formulaic legacy-versus-modern contrast (`STR_FLW_005`), artificial stakes escalation (`AUD_STK_005`), an editorial-explainer voice (`VOC_VOX_001`), and ending with a restated-thesis or summary synthesis stage (`STR_STG_008`, `STR_STG_001`) while omitting external participation pathways (`VOC_PRT_005`).

**Constraint:** When optimizing creative, editorial, or commercial writing prompts, enforce structural rarity rules in the output contract: (1) open with a concrete observation, friction point, or specific artifact rather than a thesis pre-announcement; (2) develop the thesis inductively rather than front-loading a legacy-versus-modern contrast; (3) adopt a specific practitioner or first-person perspective rather than an institutional explainer voice; and (4) end on a concrete implication or external participation pathway rather than a summary synthesis paragraph.

**When to cite:** Explaining why creative and writing prompts constrain discourse structure and conclusion behavior rather than just banning cliched words.

---

## [CONTEXT-FILES] Repository Context File Evaluation (Gloaguen, Mundler, Muller, Raychev & Vechev, 2026)
arXiv: 2602.11988

**Finding:** Across coding agents (Claude Code, Codex, Qwen Code, Sonnet 4.5, GPT-5.2) on SWE-bench and AGENTBENCH, LLM-generated repository context files (`AGENTS.md`, `CLAUDE.md`) reduced task resolution success by 3% on average while increasing inference costs by over 20% and increasing steps before first file interaction. Developer-written context files improved success by +4% on average (at up to 19% higher cost), but codebase directory overviews (included in 8 of 12 files) failed to speed up file localization. Because agents strictly obey context files, unnecessary instructions trigger redundant file traversal, grep calls, and test runs.

**Constraint:** When optimizing persistent system prompts, `AGENTS.md`, `CLAUDE.md`, or cursor/windsurf rule files, apply the Minimal Viable Context rule: omit auto-generated directory trees, codebase overviews, and generic coding platitudes. Include only (1) exact, non-inferable environment, build, lint, and test commands (such as `uv`, custom scripts, or specific flags), and (2) hard architectural boundary invariants that cannot be discovered by reading the code.

**When to cite:** Explaining why directory trees, file inventories, and generic style guidelines were stripped when optimizing an `AGENTS.md`, `CLAUDE.md`, or system prompt.

---

## [HARNESS] Harness Optimization, Context-as-a-File & Plan Verification (Lee et al., 2026; Zhang et al., 2026; Shao et al., 2026; Nam et al., 2025)
arXiv: 2603.28052 (Meta-Harness), arXiv: 2606.09498 (Self-Harness), arXiv: 2609.37725 (CLM), arXiv: 2509.21825 (DS-STAR)

**Finding:** Agent performance is jointly determined by the model and its operating harness. Meta-Harness shows that optimizing how context is retrieved and presented outperforms static context playbooks by +7.7 points while using 4x fewer context tokens. Self-Harness shows that harness design is model-specific (+14.2 to +21.4 pp pass rate on Terminal-Bench-2.0 across MiniMax, Qwen3.5, and GLM-5). Context Language Models (CLMs) show that treating context as an editable file improves accuracy by +11.4% with 21.5% fewer FLOPs on BrowseComp-Plus. DS-STAR demonstrates that inserting an explicit plan-sufficiency verification gate before execution achieves state-of-the-art accuracy on multi-source data science tasks. Meanwhile, for Large Reasoning Models (LRMs with native extended thinking), forcing verbose step-by-step CoT narration in the visible output triggers overthinking loops and inflates token costs.

**Constraint:** Route prompts by model and execution environment:
- For **Large Reasoning Models (LRMs)** (such as o3, DeepSeek-R1, Claude Extended Thinking, Gemini Thinking), use **LRM / Harness Mode**: keep Premises `[P1]` and Formal Conclusion with `[T]` evidence citations, but replace verbose step-by-step output narration with **Verification Gates** (pre-conditions and post-conditions the internal reasoning must satisfy before emitting the final artifact).
- For **Multi-Turn Agentic Workflows**, instruct the agent to externalize intermediate state to a scratchpad or state file (`Context-as-a-File`) and verify plan sufficiency before mutating target files.

**When to cite:** Explaining why an optimized prompt for a reasoning model or coding agent uses verification gates and file-backed state instead of verbose visible chain-of-thought narration.

---

## [SKILLS-SDO] Skill Residency & Positive Recipe Shaping (Yin, Li, Shi, Zhang, Seong & Wang, 2026)
arXiv: 2608.12610

**Finding:** Across 56,804 published `SKILL.md` files, installed skill descriptions sit permanently in the system prompt (50 to 280 tokens per skill every message), competing for an attention budget of fewer than 100 reliable slots. Furthermore, empirical wording evaluations show that negative prohibitions ("Do not X", "Never narrate") backfire under competing incentives, producing higher variance and more violations than positive structural recipes (stating the exact output parts in order) and conditionals keyed to observable predicates ("When condition X holds, output Y").

**Constraint:** Keep skill frontmatter descriptions compact, universal, and strictly focused on triggering conditions ("Use when..."). Within optimized prompts, express anti-hallucination and formatting rules as positive structural recipes and observable-predicate conditionals (for example, "When a trace lacks direct source evidence in [P1]-[Pn], record `UNABLE TO TRACE: [missing artifact]` and exclude the claim from the Verdict") rather than bare prohibition lists.

**When to cite:** Explaining why negative "Do NOT" rules were rewritten into positive conditional recipes, or why skill metadata uses trigger-only descriptions.
