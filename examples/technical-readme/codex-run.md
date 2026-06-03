# Codex Skill Run: Technical README

## Scope

- Surface: README / project documentation.
- Audience: developers evaluating whether to install the helper.
- Goal: explain behavior and limits without marketing language.
- Evidence policy: preserve supported file-format and dependency claims; remove perfect-accuracy promise.

## Voice Profile

- Source: `sample.txt`
- Style: plain technical writing.
- Rhythm: short paragraphs, names limits explicitly.
- Constraint: "boring in the good way"; no inflated utility claims.

## AI-pattern Audit

- Removed inflated language: "revolutionary".
- Removed promotional language: "robust and seamless", "effortlessly", "must-have".
- Removed generic conclusion.
- Flagged impossible absolute: "perfect accuracy".

## Fact Decisions

| Claim | Decision | Evidence handling |
| --- | --- | --- |
| Reads Markdown/plain text, JSON, JSONL, CSV, TSV | Kept | Supported by `evidence.md` |
| Uses only Python standard library | Kept | Supported by `evidence.md` |
| Checks every claim against public sources with perfect accuracy | Rewritten | Evidence says optional external search and no perfect accuracy |

## Final Rewrite

`humanize-skill` is a small Python helper for cleaning up AI-looking prose, building a compact voice profile from local samples, and checking claim-like sentences against evidence.

It reads plain text and Markdown, plus JSON, JSONL, CSV, and TSV exports with common text fields. The helper uses only the Python standard library.

The fact-check pass is conservative. It can compare claims with local evidence files and, when enabled, try external references. It does not promise perfect accuracy; it gives you a review surface so an editor or agent can decide what to keep, soften, cite, or remove.
