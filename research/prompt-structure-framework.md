# Prompt Structure Framework

A reference card for crafting effective prompts. Originally designed by [Lost & Lucky](https://www.instagram.com/lostandlucky/). Adapted with a certificate mapping layer for the make-prompt-better methodology.

## The Five Components

### IDENTITY
Defines the target audience and perspective.

Examples: "experienced Python developers", "a 5th grader", "first-person tone", "third-person perspective"

### TASK
States the primary action using precise verbs.

Examples: "generate 5 blog post titles", "summarize this article", "translate the following text"

### CONTEXT
Provides background information, relevant data, or prior knowledge.

Examples: "the user is a beginner in Python", "the project uses React 18 with TypeScript"

### CONSTRAINTS
Specifies limits and provides examples of desired behavior.

Examples: "under 100 words", "avoid passive voice", "use formal tone"

### OUTPUT FORMAT
Describes the shape and structure of the result.

Examples: "a JSON object", "a bulleted list", "a 250-word essay with introduction and conclusion"

## Prompt Strategy by Complexity

| Complexity | Strategy | Example |
|------------|----------|---------|
| Simple task | Task + Context + Format | "Summarize this article in 3 bullet points" |
| Complex task | Task + Context + Format + Constraints | "Translate this poem into French, keeping the original rhyme scheme" |
| Ongoing project | Task + Context + Format + Constraints | "Continue writing this story, maintaining the tone and characters" |

## Certificate Mapping

In the make-prompt-better methodology, these five components map to the certificate structure:

| Component | Certificate Role |
|-----------|-----------------|
| IDENTITY | Use sparingly per PRISM. Omit for accuracy tasks, minimal for mixed, full for alignment. |
| TASK | Base instruction. Goal-blind: state what to produce, never how it will be evaluated. |
| CONTEXT | PREMISES section. All relevant background, data, source material. |
| CONSTRAINTS | The certificate structure itself. Authority-framed per Geng et al. (2025). |
| OUTPUT FORMAT | FORMAL CONCLUSION template plus structured output (JSON) when parsing needed. |
