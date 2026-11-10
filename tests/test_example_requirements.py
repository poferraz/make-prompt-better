"""Selected original requirements in the public rewrite examples, not semantic or model proof."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def rewritten_examples():
    document = (ROOT / "make-prompt-better/references/examples.md").read_text(encoding="utf-8")
    parts = re.split(r"^### Example (\d+):[^\n]*\n", document, flags=re.M)
    return {
        int(parts[index]): re.search(
            r"#### Optimized [^\n]*\n\n```\n(.*?)\n```", parts[index + 1], re.S
        ).group(1)
        for index in range(1, len(parts), 2)
    }


class ExampleRequirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prompts = rewritten_examples()

    def assert_requirements(self, example, requirements):
        prompt = " ".join(self.prompts[example].split())
        for requirement, pattern in requirements.items():
            with self.subTest(example=example, requirement=requirement):
                self.assertRegex(prompt, "(?i)" + pattern, requirement)

    def test_code_review_preserves_demo_deadline_and_priorities(self):
        self.assert_requirements(1, {
            "client demo": r"client demo", "deadline": r"tomorrow",
            "depth": r"thorough", "bugs": r"bugs?|correctness",
            "performance": r"performance",
        })

    def test_financial_review_preserves_investment_and_valuation_decisions(self):
        self.assert_requirements(2, {
            "investment size": r"\$500[Kk]|\$500,000", "company stage": r"Series B",
            "business type": r"SaaS", "revenue growth": r"revenue growth",
            "valuation": r"valuation",
            "derived calculations": r"(?:calculate|derive).{0,60}(?:supplied|provided) (?:inputs|data)",
            "investment assessment": r"(?:whether|assess|evaluate).{0,120}invest|investment (?:assessment|recommendation|decision)",
        })
        self.assertNotRegex(self.prompts[2], r"(?i)do not render an investment recommendation")

    def test_research_summary_preserves_thesis_topic_and_key_contributions(self):
        self.assert_requirements(3, {
            "five papers": r"(?:five|5) (?:provided |supplied )?papers",
            "RAG": r"retrieval-augmented generation|\bRAG\b",
            "thesis": r"thesis", "literature review": r"literature review",
            "optimization subject": r"RAG optimization", "contributions": r"key contributions",
        })

    def test_clinical_review_preserves_case_facts_and_urgent_first_order(self):
        self.assert_requirements(4, {
            "duration": r"3 weeks", "dizziness": r"dizziness", "vision": r"blurred vision",
            "first pressure": r"148/92", "second pressure": r"152/96",
            "medication": r"lisinopril 10\s?mg daily",
        })
        prompt = self.prompts[4]
        urgency = re.search(r"(?im)^(?:Urgent[^\n]*|Risk stratification) \[T\d+\]:", prompt)
        differential = re.search(r"(?im)^Differential[^\n]* \[T\d+\]:", prompt)
        self.assertIsNotNone(urgency)
        self.assertIsNotNone(differential)
        self.assertLess(urgency.start(), differential.start(), "urgent assessment must be first")

    def test_content_audit_preserves_target_period_and_competitors(self):
        self.assert_requirements(5, {
            "traffic channel": r"organic traffic", "target": r"30%",
            "period": r"this quarter", "first competitor": r"Company A",
            "second competitor": r"Company B", "topic assessment": r"topic",
            "comparison": r"compar|benchmark",
        })

    def test_contract_review_keeps_requested_risk_and_cap_fairness_assessment(self):
        self.assert_requirements(6, {
            "agreement": r"SaaS agreement", "party": r"small startup",
            "counterparty": r"(?:larger|large) enterprise client",
            "risk assessment": r"risk", "one-sided terms": r"one-sided|asymmetr",
            "liability": r"liability cap", "fairness": r"fair(?:ness)?",
        })
        self.assertNotRegex(self.prompts[6], r'(?i)do not characterize provisions as "fair"')

    def test_compliance_audit_keeps_german_complaint_and_pre_response_assessment(self):
        self.assert_requirements(7, {
            "standard": r"GDPR", "complaint": r"complaint",
            "location": r"Germany|German user", "sequence": r"before.{0,35}respond|before.{0,35}response",
            "requested determination": r"non-compliant|noncompliance|non-compliance",
        })
        self.assertNotRegex(self.prompts[7], r'(?i)do not render a "compliant" or "non-compliant" judgment')

    def test_context_contract_keeps_layout_style_and_timeline_without_invented_tooling(self):
        self.assert_requirements(8, {
            "stack": r"FastAPI", "purpose": r"billing", "models": r"SQLAlchemy",
            "routers": r"src/api/", "model path": r"src/models/",
            "service path": r"src/services/", "tests": r"tests/",
            "clean code": r"clean", "modularity": r"modular", "style": r"PEP8",
            "documentation": r"well-documented", "audit": r"investor audit", "timeline": r"next week",
            "pre-action review": r"before (?:each|every) action|(?:review|assess|plan).{0,30}(?:each|every) action",
        })
        self.assertNotRegex(self.prompts[8], r"uv run|ruff check|mypy src|ROUND_HALF_EVEN|AsyncSession|alembic")

    def test_creative_prompt_keeps_exact_length_channel_and_signup_intent(self):
        self.assert_requirements(9, {
            "length": r"800[- ]word|800 words", "publication": r"engineering blog",
            "old approach": r"manual prompt tweaking", "new approach": r"structured context engineering",
            "channel": r"Hacker News", "conversion": r"signups|sign-ups",
            "product": r"developer platform",
        })
        self.assertNotRegex(self.prompts[9], r"750-850|zero product promotion")


if __name__ == "__main__":
    unittest.main()
