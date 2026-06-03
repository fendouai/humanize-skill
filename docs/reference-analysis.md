# Reference analysis

This project uses three references, but keeps the final product intentionally small.

## blader/humanizer

What to borrow:

- A concrete catalog of AI-writing tells.
- A draft -> audit -> final loop.
- Optional voice calibration from user samples.
- Plain editorial rules that work inside a skill without a separate app.

What to change:

- Add provenance and fact-checking.
- Make real user voice the default aspiration, not only an optional paste-in sample.
- Avoid generic "add personality" when the domain calls for neutral technical prose.

## tinyhumansai/openhuman

What to borrow:

- Local-first memory: user context should be readable and controlled by the user.
- Source adapters: different upstreams can feed the same canonical text pipeline.
- Provenance: every style sample and evidence item should have a source label.
- Periodic sync as a concept, but not as a requirement for this skill.

What to avoid:

- A heavy desktop app, OAuth broker, scheduler, database, or managed integration layer.
- Storing raw private messages when a compact style profile is enough.

Humanize-skill adaptation:

```text
user export / pasted sample
        |
        v
canonical text with source label
        |
        v
style statistics + examples summary
        |
        v
compact voice_profile.json
```

The profile is small, inspectable JSON. It should not contain full account dumps.

## Oumi HallOumi

What to borrow:

- Treat fact checking as a separate pass after generation.
- Break output into claim-like sentences.
- Judge each claim against evidence.
- Return a status, confidence, explanation, and citation.

What to avoid:

- Fine-tuning or requiring HallOumi model inference for ordinary skill use.
- Blocking all use when no evidence source exists.

Humanize-skill adaptation:

```text
rewrite
  |
  v
claim extraction
  |
  +--> style/opinion: no evidence required
  |
  +--> factual claim: compare with evidence files or current sources
             |
             v
       supported / needs_evidence / possibly_wrong
              ^
              |
       external reference search when local evidence is insufficient
```

## Proposed architecture

The open-source project has three layers:

1. `SKILL.md`: the agent-facing workflow and completion contract.
2. `scripts/humanize_skill.py`: a dependency-free helper for repeatable local passes.
3. `docs/`: reference notes, source-ingestion guidance, and examples.

## Source ingestion policy

Accept only user-controlled data:

- pasted text
- local files
- exports from social/chat/email tools
- connector output explicitly requested by the user

Default behavior:

- read the minimum needed
- summarize into profile metrics
- keep provenance labels
- do not print private source text in final output

## Fact-check policy

Lightweight by default:

- For low-risk drafts, flag unsupported specifics and avoid overclaiming.
- For unsupported, high-risk, or current facts, verify with external references instead of relying on model memory.
- Prefer primary, official, or scholarly sources over generic snippets.
- For missing evidence, either remove the claim or mark it as `needs_evidence`.

The skill should never make factual claims more specific during humanization unless those specifics come from the user's draft or cited evidence.
