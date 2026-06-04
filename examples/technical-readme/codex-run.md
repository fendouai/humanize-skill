# Codex Skill Run: Technical README

## Scope

- Surface: README / project documentation.
- Audience: developers evaluating whether to install the skill.
- Goal: explain behavior and limits without marketing language.
- Evidence policy: preserve agent-native workflow claims; remove file-format, dependency, and perfect-accuracy promises that belonged to the removed CLI.

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
| Host agent performs the semantic rewrite | Kept | Supported by `evidence.md` |
| Uses user-provided samples and evidence | Kept | Supported by `evidence.md` |
| Checks every claim against public sources with perfect accuracy | Rewritten | Evidence says review is conservative and does not guarantee perfect accuracy |

## Final Rewrite

`humanize-skill` is an agent workflow for cleaning up AI-looking prose, building a compact voice profile from user-provided samples, and checking claim-like sentences against evidence.

There is no rewrite CLI. Codex or Claude does the semantic edit: it diagnoses AI-looking patterns, rewrites complete sentences, and uses the text, files, exports, or authorized connectors the user chooses for that run.

The fact-check pass is conservative. It compares claims with provided evidence first and uses current search tools when available and appropriate. It does not promise perfect accuracy; it gives the agent and the writer a review surface for what to keep, soften, cite, or remove.
