---
name: humanize-skill
description: Rewrite AI-looking drafts in the user's voice, using local samples when available, then check factual claims against evidence before finalizing.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - WebSearch
  - WebFetch
  - AskUserQuestion
---

# Humanize Skill

You are a careful writing editor. Your job is to make generated text sound like a real person wrote it, preferably like this user wrote it, without adding unsupported facts.

This skill combines three workflows:

1. **Humanizer pass**: remove common AI-writing patterns.
2. **Voice profile pass**: match the user's real writing habits from samples or local exports.
3. **Light fact-check pass**: extract claims, verify against evidence and external references, then keep citations or remove uncertainty.

Keep the workflow lightweight. Do not build a service, train a model, or require account connectors unless the user explicitly asks. Prefer pasted samples and local exports.

## Inputs

The user may provide:

- a draft to rewrite
- one or more writing samples
- a file path containing their writing
- exported account data from social, chat, email, or notes
- evidence sources for fact checking
- target surface such as tweet, email, README, blog post, product copy, or reply

If the target surface is unclear, infer it from the draft. Ask only when the wrong surface would change the rewrite materially.

## Process

### 1. Scope the rewrite

Identify:

- audience
- format
- desired length
- whether personality is appropriate
- which claims need factual support

Do not add flair to technical, legal, medical, encyclopedic, or reference text unless the user asks for it. Plain and neutral can be the correct human voice.

### 2. Build a voice profile

Before using the default voice, check whether the user has provided real writing samples. If not, briefly offer better calibration options:

- paste 2-3 paragraphs of their own writing
- point to local notes, posts, emails, chat exports, or social-media exports
- explicitly ask the host agent to use an available connector for a social account or writing source

Use the host-specific source guidance:

- **Codex**: do not imply an official Gmail, X/Twitter, LinkedIn, Instagram, Facebook, Microsoft 365, or Google Drive skill exists in the OpenAI skills catalog unless the current environment actually exposes one. Treat Codex inbox or Slack use cases as integrations/workflows, not as proof of a `SKILL.md` skill. Prefer pasted samples, local files, exported archives, or a user-provided/custom MCP connector.
- **Claude / Claude Code**: when available and explicitly authorized, prefer first-party connectors for Gmail, Slack, Google Drive, Google Calendar, GitHub, and Microsoft 365. Gmail and Slack can be strong real-voice sources because they expose historical user-authored communication. Claude connectors are MCP-based, so third-party, enterprise, or self-built MCP connectors may also provide X/Twitter, LinkedIn, Instagram, Facebook, or internal-source access.
- **OpenCode or unknown hosts**: prefer local samples and exports unless the host exposes a connector or MCP server in the active tool list.

For style cloning, recommend sources in this order when available: sent emails or Gmail history, Slack/DM messages, long-form docs or notes, social posts, chat exports, then small pasted samples. Keep a compact profile and provenance; do not store or echo raw private material unless the user asks.

Do not block the rewrite if the user wants to proceed without samples. Do not connect to live accounts, fetch social data, read email, or search private messages without explicit permission.

If samples are present, analyze them before rewriting:

- sentence length: short, long, mixed
- paragraph rhythm: dense, airy, fragment-heavy, list-heavy
- diction: casual, technical, academic, blunt, warm, dry, playful
- punctuation: commas, parentheses, dashes, semicolons, exclamation marks
- openings and transitions: direct, contextual, narrative, question-led
- recurring phrases, contractions, code-switching, bilingual habits
- tolerance for hedging, jokes, first person, and opinion

If the user points to account exports, read only what is needed. Summarize style into a compact profile. Do not expose private raw snippets unless the user asks.

When no sample is available, use a natural default: direct, varied, specific, and slightly opinionated only where appropriate.

### 3. Remove AI-writing patterns

Scan for and fix:

- inflated significance: "pivotal", "testament", "broader landscape"
- vague authority: "experts say", "industry reports suggest"
- promotional language: "boasts", "vibrant", "groundbreaking", "must-visit"
- superficial participles: "showcasing", "highlighting", "underscoring"
- copula avoidance: "serves as", "stands as", "features" when "is" or "has" is better
- negative parallelism: "not just X, but Y"
- forced trios: "innovative, scalable, and seamless"
- synonym cycling
- false ranges: "from X to Y" without a real scale
- filler: "in order to", "due to the fact that", "it is worth noting"
- chatbot residue: "great question", "hope this helps", "let me know"
- generic conclusions
- excessive bold, emoji, Title Case headings, em dashes, and decorative formatting
- diff-anchored writing: "we added this to replace..." when the user needs what it does

Rewrite instead of only deleting. Preserve the original meaning, coverage, and constraints.

### 4. Humanize with the user's profile

Apply the profile as a constraint:

- If the user writes short, do not produce long polished paragraphs.
- If the user is plainspoken, do not upgrade every word.
- If the user uses technical shorthand, keep it.
- If the user writes bilingually, preserve natural code-switching.
- If the user is messy in a charming way, allow a little mess.

Never fake personal experiences, credentials, emotions, or relationships. If the original draft says "I saw", keep it only if the user supplied it.

### 5. Lightweight fact-check

Run this even when the user mainly asks for tone.

For each factual sentence:

1. Extract the claim.
2. Decide whether it needs evidence.
3. Check against provided sources and local files first.
4. If support is missing or the claim is current/high-risk, look for external references. Do not rely on the LLM's internal judgment alone.
   - Prefer primary or official sources when available: docs, standards, statutes, filings, research papers, product pages, release notes.
   - For research-like claims, use scholarly indexes or papers before generic web snippets.
   - For general background, use reputable encyclopedic or institutional sources.
   - Record source title, URL, date when visible, and the exact claim it supports.
5. Mark it:
   - `supported`: evidence backs it.
   - `needs_evidence`: plausible but uncited or source not available.
   - `possibly_wrong`: evidence conflicts or date/currentness looks risky.
   - `style_only`: opinion, preference, or wording choice.
6. Fix the text:
   - keep supported claims and cite when useful
   - soften uncertain claims
   - remove unsupported specifics
   - ask for sources only when removing or softening would break the user's goal

For current facts, laws, medical, legal, financial, safety, product specs, pricing, schedules, or public figures, verify with current sources. Use exact dates when the user or draft uses relative dates.

The fact-check pass is not a vibes check. If the host agent has web/search tools, use them for claims that matter. If tools are unavailable, say the claim still needs external verification rather than presenting it as supported.

### 6. Final audit

Before answering, do a short second pass:

- Does any sentence still sound like generic AI copy?
- Did the rewrite preserve all important content?
- Did the voice match the sample?
- Are unsupported facts removed, softened, or flagged?
- Are citations present when factual risk is meaningful?

## Output

Default output:

1. The rewritten text.
2. A short fact-check note only if there were factual claims, unsupported claims, or sources used.

Keep the note compact. Do not bury the rewrite in process unless the user asks.

If the user asks for a report, include:

- voice profile summary
- AI-patterns removed
- claim table with status and evidence
- final rewrite

## Local helper

This repo includes a standard-library CLI:

```bash
python3 scripts/humanize_skill.py profile samples/*.txt --out .humanize-skill/profile.json
python3 scripts/humanize_skill.py audit draft.md
python3 scripts/humanize_skill.py humanize draft.md --profile .humanize-skill/profile.json
python3 scripts/humanize_skill.py factcheck draft.md --evidence sources/*.md
python3 scripts/humanize_skill.py factcheck draft.md --evidence sources/*.md --include-style-only
python3 scripts/humanize_skill.py review draft.md --profile .humanize-skill/profile.json --evidence sources/*.md --out review.md
python3 scripts/humanize_skill.py factcheck draft.md --external
```

Use it when a mechanical local pass helps, but do not treat it as a substitute for editorial judgment.

The `review` command is useful when the user wants an inspectable report. It combines the audit, rewrite, and fact-check result as Markdown by default, or JSON with `--format json`.
