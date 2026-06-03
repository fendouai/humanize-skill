# Codex Skill Run: Support Reply

## Scope

- Surface: support reply.
- Audience: user with a profile/export issue.
- Goal: be calm, useful, and accurate.
- Evidence policy: remove unsupported sync and absolute safety claims.

## Voice Profile

- Source: `sample.txt`
- Style: empathetic but precise.
- Rhythm: acknowledge the issue, separate known facts from next steps.
- Constraint: avoid generic apology padding and avoid overpromising.

## AI-pattern Audit

- Removed chatbot residue: "Great question!"
- Reduced generic apology.
- Replaced filler: "In order to".
- Removed unsupported absolute: "your data is always safe".
- Corrected unsupported product behavior: "synchronize your writing profile across every channel".

## Fact Decisions

| Claim | Decision | Evidence handling |
| --- | --- | --- |
| Local helper does not sync writing profile across channels | Kept | Supported by `evidence.md` |
| Reads selected files and writes profile to chosen location | Kept | Supported by `evidence.md` |
| Data is always safe | Removed | Evidence does not support an absolute guarantee |

## Final Rewrite

Thanks for the details. I can see why this is frustrating.

One thing to clarify first: the local helper does not sync your writing profile across channels. It reads the files you choose and writes the profile where you tell it to.

Please try rebuilding the profile from the source file you meant to use. If the output still looks wrong, send the command you ran and the type of export you used, and I will help narrow it down.
