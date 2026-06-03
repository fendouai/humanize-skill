`humanize-skill` is a small Python helper for cleaning up AI-looking prose, building a compact voice profile from local samples, and checking claim-like sentences against evidence.

It reads plain text and Markdown, plus JSON, JSONL, CSV, and TSV exports with common text fields. The helper uses only the Python standard library.

The fact-check pass is conservative. It can compare claims with local evidence files and, when enabled, try external references. It does not promise perfect accuracy; it gives you a review surface so an editor or agent can decide what to keep, soften, cite, or remove.
