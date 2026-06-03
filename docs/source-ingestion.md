# Source ingestion

`humanize-skill` can learn from real user writing without becoming a heavy account-ingestion product.

## Preferred order

1. Pasted writing sample.
2. Local files selected by the user.
3. Exported account archives selected by the user.
4. Host-agent connectors, only after explicit permission.

## Supported local formats

The helper currently reads:

- `.txt`, `.md`, and other plain text files
- `.json` and `.jsonl`, recursively collecting text-like fields
- `.csv` and `.tsv`, reading common text columns such as `text`, `body`, `content`, `message`, and `full_text`

This is enough for many X/Twitter archive extracts, chat exports, newsletter drafts, support replies, and note collections after light preprocessing.

## Privacy rules

- Build compact profiles, not raw-message stores.
- Keep source labels and counts for provenance.
- Do not print private sample text in final answers.
- Use only user-controlled data.
- Treat live connectors as optional, explicit, and revocable.

## Profile shape

The local helper writes inspectable JSON:

```json
{
  "sample_count": 3,
  "sources": ["samples/email.txt", "samples/posts.jsonl"],
  "word_count": 1200,
  "sentence_count": 80,
  "avg_sentence_words": 15.2,
  "sentence_rhythm": "mixed",
  "paragraph_style": "brief",
  "punctuation": { ".": 80, ",": 42 },
  "top_words": ["product", "ship", "users"],
  "likely_tone": ["personal", "technical", "direct"]
}
```

Agents should use this profile as guidance, not as a rigid template.
