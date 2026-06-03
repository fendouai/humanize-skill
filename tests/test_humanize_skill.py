import json
import tempfile
import unittest
from pathlib import Path

from scripts import humanize_skill


class HumanizeSkillTests(unittest.TestCase):
    def test_audit_finds_common_ai_patterns(self):
        findings = humanize_skill.audit_text(
            "Great question. This groundbreaking platform serves as a testament to the evolving landscape."
        )
        names = {item["pattern"] for item in findings}
        self.assertIn("chatbot_residue", names)
        self.assertIn("inflated_significance", names)
        self.assertIn("copula_avoidance", names)

    def test_simple_humanize_removes_chatbot_residue_and_bold(self):
        text = "Great question! **Speed:** In order to move fast, the tool serves as a helper.\n\nKeep this paragraph."
        result = humanize_skill.simple_humanize(text)
        self.assertNotIn("Great question", result)
        self.assertNotIn("**", result)
        self.assertIn("To move fast", result)
        self.assertIn("is a helper", result)
        self.assertIn("\n\nKeep this paragraph.", result)

    def test_profile_builds_compact_voice_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("I ship small things. Then I see what breaks.\n\nAPIs are easier that way.", encoding="utf-8")
            profile = humanize_skill.build_profile([path])
        self.assertEqual(profile.sample_count, 1)
        self.assertEqual(len(profile.sources), 1)
        self.assertIn("technical", profile.likely_tone)
        self.assertEqual(profile.sentence_rhythm, "short")

    def test_factcheck_marks_supported_with_evidence_overlap(self):
        results = humanize_skill.factcheck(
            "OpenHuman stores its Memory Tree and Markdown vault locally.",
            ["OpenHuman stores Memory Tree data and an Obsidian-style Markdown vault on the user's machine."],
        )
        self.assertEqual(results[0]["status"], "supported")
        self.assertEqual(results[0]["source_type"], "provided_evidence")

    def test_factcheck_can_use_external_references(self):
        def fake_lookup(claim, max_results):
            return [
                humanize_skill.ReferenceSource(
                    provider="test",
                    title="HallOumi claim verification model",
                    url="https://example.test/halloumi",
                    snippet="HallOumi is a claim verification model that checks generated responses against evidence.",
                )
            ]

        results = humanize_skill.factcheck(
            "HallOumi is a claim verification model.",
            [],
            external=True,
            external_lookup=fake_lookup,
        )

        self.assertEqual(results[0]["status"], "supported")
        self.assertEqual(results[0]["source_type"], "external_reference")
        self.assertEqual(results[0]["references"][0]["provider"], "test")

    def test_external_references_must_independently_support_claim(self):
        def fake_lookup(claim, max_results):
            return [
                humanize_skill.ReferenceSource("test", "Halloumi cheese", "https://example.test/a", "Halloumi is a cheese."),
                humanize_skill.ReferenceSource("test", "Claim verification", "https://example.test/b", "Claim verification compares claims to evidence."),
            ]

        results = humanize_skill.factcheck(
            "HallOumi is a claim verification model.",
            [],
            external=True,
            external_lookup=fake_lookup,
        )

        self.assertEqual(results[0]["status"], "needs_evidence")

    def test_factcheck_can_include_style_only_sentences(self):
        results = humanize_skill.factcheck(
            "I prefer short notes. OpenHuman stores Memory Tree data locally.",
            ["OpenHuman stores Memory Tree data locally."],
            include_style_only=True,
        )

        statuses = [item["status"] for item in results]
        self.assertEqual(statuses, ["style_only", "supported"])

    def test_json_exports_are_read_for_text_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "messages.json"
            path.write_text(json.dumps([{"text": "This is my actual writing sample."}]), encoding="utf-8")
            self.assertIn("actual writing sample", humanize_skill.read_text(path))

    def test_csv_exports_are_read_for_text_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "messages.csv"
            path.write_text("id,message\n1,This is a CSV writing sample.\n", encoding="utf-8")
            self.assertIn("CSV writing sample", humanize_skill.read_text(path))

    def test_review_payload_combines_audit_rewrite_and_factcheck(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            draft.write_text(
                "Great question. OpenHuman stores Memory Tree data locally.",
                encoding="utf-8",
            )
            evidence = Path(tmp) / "evidence.md"
            evidence.write_text("OpenHuman stores Memory Tree data locally.", encoding="utf-8")

            parser = humanize_skill.build_parser()
            args = parser.parse_args(["review", str(draft), "--evidence", str(evidence), "--format", "json"])
            payload = humanize_skill.review_payload(args)

        self.assertIn("rewrite", payload)
        self.assertNotIn("Great question", payload["rewrite"])
        self.assertEqual(payload["factcheck"][0]["status"], "supported")

    def test_reconstruct_openalex_abstract(self):
        abstract = humanize_skill.reconstruct_openalex_abstract({
            "claim": [0],
            "verification": [1],
            "model": [2],
        })
        self.assertEqual(abstract, "claim verification model")

    def test_claim_extraction_ignores_markdown_code_fences(self):
        claims = humanize_skill.extract_claims(
            "```text\nOpenHuman stores Memory Tree data locally.\n```\n\nOutside text is a factual claim here."
        )
        self.assertEqual(claims, ["Outside text is a factual claim here."])

    def test_claim_extraction_catches_tool_capability_verbs(self):
        claims = humanize_skill.extract_claims(
            "The helper reads Markdown files and checks factual claims."
        )
        self.assertEqual(claims, ["The helper reads Markdown files and checks factual claims."])


if __name__ == "__main__":
    unittest.main()
