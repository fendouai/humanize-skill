# Reference analysis

This project uses four references, but keeps the final product intentionally small.

## blader/humanizer

What to borrow:

- A concrete catalog of AI-writing tells, organized as a 30-category checklist.
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
compact voice profile notes
```

The profile can be saved as small, inspectable notes or JSON. It should not contain full account dumps.

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

The open-source project has four small layers:

1. `SKILL.md`: the agent-facing workflow and completion contract.
2. `docs/`: reference notes and source-ingestion guidance.
3. `examples/`: real agent runs with draft, sample, evidence, notes, and final output.
4. `assets/`: README visual assets.

There is no CLI layer. The host model performs the semantic rewrite, while the skill supplies the process, guardrails, and artifact shape.

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

Lightweight by default, but with enough structure to leave a clean audit trail. The full method is in [docs/fact-check.md](./fact-check.md): claim taxonomy, source hierarchy, time and staleness, conflict protocol, fix matrix, tool unavailability, AI's specific factual failure modes, and the recommended `evidence.md` shape.

Short form:

- For low-risk drafts, flag unsupported specifics and avoid overclaiming.
- For unsupported, high-risk, or current facts, verify with external references instead of relying on model memory.
- Prefer primary, official, or scholarly sources over generic snippets. Treat the source tier as part of the citation: a peer-reviewed paper, a primary filing, an official changelog, a major-newspaper report, and an SEO blog are not equivalent.
- Watch for staleness. A 2019 statistic is rarely a 2026 fact. Re-date or remove.
- For missing or weak evidence, label precisely (`supported`, `weak_support`, `unverified`, `contested`, `stale`, `wrong`, `style_only`) and apply the fix matrix. The coarse `needs_evidence` label is the public API; the depth split is for the rewrite.
- If web/search tools are unavailable, all claims default to `unverified` and the final output states the limitation explicitly.
- When sources disagree, follow a protocol: higher tier wins, then newer, then primary, then less motivated. If still unresolved, name the tension rather than picking a side.

The skill should never make factual claims more specific during humanization unless those specifics come from the user's draft or cited evidence. Personal experience in the user's draft is theirs; numerical, attributed, identity, and schedule claims still need checking.

## Wikipedia: Signs of AI writing

This is the primary lexical and phrasal reference for the AI-pattern catalog in `docs/anti-ai-patterns.md`. It is maintained by WikiProject AI Cleanup as a community-edited catalog of words, phrases, and structural habits that mark LLM-generated text in Wikipedia and similar surfaces.

What to borrow:

- A community-maintained, regularly-updated list of specific tells.
- The em-dash overuse, significance inflation, vague attribution, and chatbot residue clusters as canonical categories.
- The "rule of three" structural pattern (paragraphs opening with the same grammatical role, three-clause parallelism, three-item lists).

What to change:

- Treat the Wikipedia list as the *lexical and phrasal substrate*, not as the whole catalog. The structural layer (heading cadence, bullet-list overuse, intro-body-summary sandwich) and the cognitive layer (uniform confidence, no stated limits, hidden reasoning, generic examples) are added by `humanize-skill` because the Wikipedia list does not cover them, and they are the patterns detector-style tools pick up most.
- Apply the "rewrite, don't delete" principle from `blader/humanizer` to each Wikipedia pattern: removing the matched phrase without rewriting the surrounding sentence leaves a formula fragment.
- Match the user's voice profile before applying any pattern removal. The Wikipedia list describes a generic AI default. A user with a stable em-dash habit, a personal use of "delve", or a signature that includes "tirelessly" is not the Wikipedia target. The voice profile is the override.
- Do not import the Wikipedia list as a hard rules engine. The list is a diagnostic aid. The final rewrite is editorial judgment.

The catalog in `docs/anti-ai-patterns.md` is layered on this source, plus `blader/humanizer`'s curation, plus the structural and cognitive layers this skill adds.
