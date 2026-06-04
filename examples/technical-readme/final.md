`humanize-skill` is an agent workflow for cleaning up AI-looking prose, building a compact voice profile from user-provided samples, and checking claim-like sentences against evidence.

There is no rewrite CLI. Codex or Claude does the semantic edit: it diagnoses AI-looking patterns, rewrites complete sentences, and uses the text, files, exports, or authorized connectors the user chooses for that run.

The fact-check pass is conservative. It compares claims with provided evidence first and uses current search tools when available and appropriate. It does not promise perfect accuracy; it gives the agent and the writer a review surface for what to keep, soften, cite, or remove.
