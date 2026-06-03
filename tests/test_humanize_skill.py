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

    def test_json_exports_are_read_for_text_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "messages.json"
            path.write_text(json.dumps([{"text": "This is my actual writing sample."}]), encoding="utf-8")
            self.assertIn("actual writing sample", humanize_skill.read_text(path))

    def test_reconstruct_openalex_abstract(self):
        abstract = humanize_skill.reconstruct_openalex_abstract({
            "claim": [0],
            "verification": [1],
            "model": [2],
        })
        self.assertEqual(abstract, "claim verification model")


if __name__ == "__main__":
    unittest.main()
