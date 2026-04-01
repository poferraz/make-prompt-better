# Task Classification Guide

## 1. Introduction

Every prompt you write has a hidden property: its task type. That type determines whether adding a persona helps, hurts, or does nothing. Getting this wrong is not a neutral mistake. Research from PRISM shows that applying a persona to an accuracy-dependent task drops performance by 3 to 5 percentage points on benchmarks like MMLU (Hu, Rostami & Thomason, 2026). That is the difference between a correct answer and a confidently wrong one.

This guide gives you a classification system so you can make the right persona decision before you write a single line of prompt text.

## 2. The Three Categories

### Accuracy-dependent

Tasks where the output must be factually correct, logically sound, or mathematically precise. The model needs to retrieve knowledge, apply reasoning, or compute a result.

Examples:
- "What is the capital of France?"
- "Classify this email as spam or not spam"
- "Find the bug in this function"
- "Calculate the compound interest on $10,000 at 5% over 10 years"
- "What does Section 230 of the Communications Decency Act cover?"
- "Translate this Python function to Rust"

### Alignment-dependent

Tasks where the output must conform to a format, style, tone, or safety constraint. The factual content is secondary (or already determined). What matters is how the output reads and whether it follows rules.

Examples:
- "Write a professional email declining a meeting"
- "Format this data as a markdown table"
- "Rewrite this paragraph to be more concise"
- "Check this text for safety concerns"
- "Convert this bullet list into a formal report"
- "Rephrase this to sound more empathetic"

### Mixed

Tasks that require both accurate reasoning and structured, formatted, or stylized output. These are the most common in real-world use and the trickiest to classify.

Examples:
- "Analyze this financial report and present key findings in a table"
- "Review this code for bugs and write a summary with severity ratings"
- "Summarize these research papers with proper citations in APA format"
- "Extract action items from this meeting transcript and categorize them by department"
- "Evaluate this legal contract clause and explain the risks in plain language"

## 3. Persona Decision Tree

Based on findings from PRISM (Hu, Rostami & Thomason, 2026):

```
START: Classify the task
│
├─► ACCURACY-DEPENDENT
│   └─► Apply NO persona
│       MMLU baseline: 71.6%
│       With persona: 66.3% to 68.0%
│       Net effect: 3.6 to 5.3pp damage
│
├─► ALIGNMENT-DEPENDENT
│   └─► Apply FULL persona
│       MT-Bench improvement: +0.4 to +0.65
│       Persona helps the model match expected
│       format, tone, and style constraints
│
├─► MIXED
│   └─► Apply MINIMAL persona (5 words max)
│       Example: "You are a data analyst."
│       Full persona damages the accuracy component.
│       No persona weakens the alignment component.
│       Minimal persona threads the needle.
│
└─► USING A REASONING-DISTILLED MODEL
    └─► Skip persona entirely
        PRISM finds that distilled models gain accuracy
        from longer, more detailed context, not from
        identity framing. Persona adds noise.
```

Key findings from the paper:

- Personas that assert expertise ("You are a world-class mathematician") consistently reduce accuracy on factual benchmarks, likely because they prime the model to generate confident but unsubstantiated claims rather than reason carefully (Hu, Rostami & Thomason, 2026).
- Personas that describe behavioral expectations ("Respond in a professional tone") improve alignment scores because they give the model concrete output constraints to follow (Hu, Rostami & Thomason, 2026).
- The damage from wrong persona choice is asymmetric: a bad persona hurts accuracy more than a good persona helps alignment (Hu, Rostami & Thomason, 2026).

## 4. Classification Examples Table

| Prompt | Category | Persona Decision | Rationale |
|--------|----------|-----------------|-----------|
| "What is the melting point of titanium?" | Accuracy | None | Single fact retrieval. Persona adds no value and risks 3-5pp accuracy loss (Hu, Rostami & Thomason, 2026). |
| "Explain quantum entanglement to a 12-year-old" | Alignment | Full: "You are a middle school science teacher." | The accuracy bar is low (basic concepts). The alignment bar is high (age-appropriate language). Persona helps tone matching. |
| "Find the security vulnerability in this C function" | Accuracy | None | Requires precise code analysis. Persona primes confident-but-wrong answers per PRISM findings. |
| "Write a haiku about autumn" | Alignment | Full: "You are a poet." | Creative generation with format constraints. Persona supports stylistic alignment. |
| "Calculate the ROI given these cash flows: [...]" | Accuracy | None | Mathematical computation. Persona provides no computational benefit. |
| "Rewrite this error message to be user-friendly" | Alignment | Full: "You are a UX writer." | Tone and clarity matter more than factual precision. |
| "Debug this Python script and document the fixes" | Mixed | Minimal: "You are a Python developer." | Accuracy needed for debugging, alignment needed for documentation. Minimal persona balances both. |
| "Summarize this 10-K filing and highlight risks in a table" | Mixed | Minimal: "You are a financial analyst." | Accuracy needed to identify real risks, alignment needed for table format and professional tone. |
| "Convert 100 miles to kilometers" | Accuracy | None | Unit conversion. Trivially correct without persona. |
| "Write a GDPR-compliant privacy policy for a SaaS app" | Mixed | Minimal: "You are a legal consultant." | Legal accuracy is critical, but formatting and tone compliance are also required. |
| "List the primary colors" | Accuracy | None | Simple retrieval. Persona is pure overhead. |
| "Compose a heartfelt apology email to a client" | Alignment | Full: "You are a customer success manager." | Emotional tone and professional framing matter. Facts are secondary. |
| "Optimize this SQL query and explain the changes" | Mixed | Minimal: "You are a database engineer." | Performance tuning requires accuracy. Explanation requires clarity. Minimal persona serves both. |
| "Is this image safe for a children's website?" | Accuracy | None | Safety classification is a judgment call that benefits from neutral, unbiased reasoning. Persona introduces bias. |
| "Create a style guide for our brand voice" | Alignment | Full: "You are a brand strategist." | The task is inherently about defining alignment constraints. Persona reinforces the framing. |

## 5. Common Misclassification Pitfalls

### Tasks that look accuracy-dependent but are alignment-dependent

**"Explain the causes of World War I."**
Looks accuracy-dependent (it is a history question). But the model already knows the causes with high reliability. What varies is the quality of the explanation: structure, depth, reading level, and narrative coherence. This is alignment-dependent in practice. A persona like "You are a history professor writing for undergraduates" improves the output without meaningful accuracy risk because the baseline accuracy on this topic is already near ceiling.

**"Summarize this article."**
Looks accuracy-dependent (you need to get the facts right). But summarization is predominantly a format and style task. The model will extract the key points reliably. What persona controls is length, tone, and structure. Alignment-dependent in most cases.

### Tasks that look alignment-dependent but are accuracy-dependent

**"Write a professional assessment of this patient's symptoms."**
Looks alignment-dependent (professional tone, medical format). But the clinical reasoning must be accurate. A persona like "You are a board-certified physician" can cause the model to overcommit to a diagnosis rather than present a careful differential. Accuracy-dependent with alignment requirements. Use minimal persona or none.

**"Generate test cases for this function."**
Looks alignment-dependent (structured output, format rules). But the test cases must be logically correct and cover edge cases. This is accuracy-dependent. Persona adds nothing to logical coverage and may cause the model to generate superficially plausible but incomplete tests.

**"Review this contract for unusual clauses."**
Looks alignment-dependent (legal formatting, professional language). But the core task is detecting anomalies in legal text, which requires precise reading comprehension. A "legal expert" persona may cause the model to skip careful analysis in favor of producing polished-sounding but shallow commentary. Accuracy-dependent.

### The "creative" trap

Tasks labeled "creative writing" are not always alignment-only. If the prompt asks for a story that incorporates specific factual details (historical events, scientific concepts, real locations), the creative element is alignment but the factual grounding is accuracy. Classify as mixed and use minimal persona.

---

**Reference:**

Hu, Z., Rostami, M. & Thomason, J. (2026). "Expert Personas Improve LLM Alignment but Damage Accuracy." arXiv:2603.18507.
