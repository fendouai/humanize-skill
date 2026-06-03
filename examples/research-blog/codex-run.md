# Codex Skill Run: Research Blog

## Scope

- Surface: blog introduction.
- Audience: readers who want a sober explanation of the writing problem.
- Goal: open with the tension, not fake urgency.
- Evidence policy: remove unsupported statistics and soften claims about hallucination prevention.

## Voice Profile

- Source: `sample.txt`
- Style: essay-like, skeptical of universal claims.
- Rhythm: problem first, then mechanism, then limitation.
- Constraint: no fake stats and no "revolutionary" framing.

## AI-pattern Audit

- Removed inflated framing: "today's rapidly evolving landscape", "more important than ever".
- Removed unsupported statistic: "increases reader trust by 87%".
- Replaced impossible claim: "eliminate hallucinations".
- Removed broad transformation language.

## Fact Decisions

| Claim | Decision | Evidence handling |
| --- | --- | --- |
| Combines voice profiling, AI-pattern cleanup, and lightweight fact-checking | Kept | Supported by `evidence.md` |
| Humanized copy increases reader trust by 87% | Removed | Evidence says no study provided |
| Fact-checking eliminates hallucinations | Softened | Evidence says it can reduce unsupported claims, not eliminate hallucinations |

## Final Rewrite

AI drafts often have two separate problems. They sound generic, and they can make unsupported claims feel finished.

`humanize-skill` treats those as separate editing passes. First it uses local samples or exports to build a compact voice profile. Then it rewrites the draft with fewer AI tells. After that, it checks claim-like sentences against evidence and marks what is supported, missing a source, or risky.

That does not eliminate hallucinations. It gives the writer a clearer review step before the text goes out.
