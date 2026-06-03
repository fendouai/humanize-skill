#!/usr/bin/env python3
"""Lightweight local helper for humanize-skill.

The skill itself is the primary product. This CLI gives the project a repeatable
local baseline for style profiling, AI-pattern auditing, simple rewriting, and
evidence-file fact checks without external dependencies.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence


AI_PATTERNS: list[tuple[str, str, str]] = [
    ("inflated_significance", r"\b(pivotal|crucial|vital|testament|landscape|underscores?|showcases?|transformative|groundbreaking)\b", "Inflated significance or generic AI vocabulary."),
    ("promotional_language", r"\b(boasts?|nestled|breathtaking|vibrant|renowned|stunning|must-visit|seamless|powerful)\b", "Promotional or ad-like language."),
    ("vague_attribution", r"\b(experts|observers|industry reports|some critics|several sources)\b", "Vague attribution needs a named source."),
    ("participle_depth", r"\b(highlighting|underscoring|showcasing|reflecting|symbolizing|fostering|cultivating|contributing)\b", "Superficial -ing analysis."),
    ("copula_avoidance", r"\b(serves as|stands as|functions as|features|offers|represents)\b", "Likely over-elaborate replacement for is/has."),
    ("negative_parallelism", r"\b(not just|not only|not merely)\b.*\b(but|it's)\b", "Formulaic negative parallelism."),
    ("filler", r"\b(in order to|due to the fact that|it is worth noting|at its core|in conclusion|moving forward)\b", "Filler or signposting phrase."),
    ("chatbot_residue", r"\b(great question|hope this helps|let me know if|here's what you need to know|let's dive in)\b", "Chatbot residue."),
    ("decorative_formatting", r"(\*\*[^*]+\*\*|[\U0001F300-\U0001FAFF]|—|–)", "Decorative formatting, emoji, or dash overuse."),
]

REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bGreat question[!.]?\s*", re.I), ""),
    (re.compile(r"\bI hope this helps[!.]?\s*", re.I), ""),
    (re.compile(r"\bLet me know if[^.?!]*[.?!]", re.I), ""),
    (re.compile(r"\bIn order to\b", re.I), "To"),
    (re.compile(r"\bDue to the fact that\b", re.I), "Because"),
    (re.compile(r"\bAdditionally\b", re.I), "Also"),
    (re.compile(r"\bserves as\b", re.I), "is"),
    (re.compile(r"\bstands as\b", re.I), "is"),
    (re.compile(r"\bboasts\b", re.I), "has"),
    (re.compile(r"\bshowcases\b", re.I), "shows"),
    (re.compile(r"\bunderscores\b", re.I), "shows"),
    (re.compile(r"\bhighlights\b", re.I), "shows"),
    (re.compile(r"\bseamless\b", re.I), "straightforward"),
]

STOPWORDS = {
    "the", "and", "that", "this", "with", "from", "have", "has", "for", "you",
    "your", "are", "was", "were", "will", "would", "about", "into", "over",
    "under", "than", "then", "there", "here", "they", "them", "their", "its",
    "our", "ours", "but", "not", "can", "could", "should", "because", "also",
}


@dataclass
class VoiceProfile:
    sample_count: int
    word_count: int
    sentence_count: int
    avg_sentence_words: float
    sentence_rhythm: str
    paragraph_style: str
    punctuation: dict[str, int]
    top_words: list[str]
    likely_tone: list[str]


@dataclass
class ReferenceSource:
    provider: str
    title: str
    url: str
    snippet: str


def read_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".json", ".jsonl"}:
        return read_jsonish(path)
    if suffix in {".csv", ".tsv"}:
        return read_delimited(path, delimiter="\t" if suffix == ".tsv" else ",")
    return path.read_text(encoding="utf-8", errors="replace")


def read_jsonish(path: Path) -> str:
    lines: list[str] = []
    raw = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(raw)
        collect_json_strings(data, lines)
    except json.JSONDecodeError:
        for row in raw.splitlines():
            try:
                collect_json_strings(json.loads(row), lines)
            except json.JSONDecodeError:
                continue
    return "\n".join(lines)


def collect_json_strings(value: object, out: list[str]) -> None:
    if isinstance(value, str):
        if len(value.split()) >= 3:
            out.append(value)
    elif isinstance(value, dict):
        preferred = ["text", "body", "content", "message", "full_text", "title"]
        for key in preferred:
            if key in value:
                collect_json_strings(value[key], out)
        for key, child in value.items():
            if key not in preferred:
                collect_json_strings(child, out)
    elif isinstance(value, list):
        for child in value:
            collect_json_strings(child, out)


def read_delimited(path: Path, delimiter: str) -> str:
    rows: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        for row in reader:
            for key in ("text", "body", "content", "message", "full_text"):
                value = row.get(key)
                if value:
                    rows.append(value)
                    break
    return "\n".join(rows)


def sentences(text: str) -> list[str]:
    text = normalize_markdown_for_sentences(text)
    parts = re.split(r"(?<=[.!?。！？])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def normalize_markdown_for_sentences(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if re.match(r"^#{1,6}\s+", stripped):
            lines.append("")
            continue
        stripped = re.sub(r"^[-*+]\s+", "", stripped)
        stripped = re.sub(r"^\d+[.)]\s+", "", stripped)
        lines.append(stripped)
    return "\n".join(lines)


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", text.lower())


def key_terms(text: str, limit: int = 10) -> list[str]:
    counts = Counter(w for w in words(text) if len(w) > 3 and w not in STOPWORDS)
    return [word for word, _ in counts.most_common(limit)]


def build_profile(paths: Sequence[Path]) -> VoiceProfile:
    texts = [read_text(path) for path in paths]
    merged = "\n\n".join(texts)
    sents = sentences(merged)
    tokenized = words(merged)
    sent_lengths = [len(words(sentence)) for sentence in sents] or [0]
    avg = statistics.mean(sent_lengths)
    stdev = statistics.pstdev(sent_lengths) if len(sent_lengths) > 1 else 0
    paragraphs = [p for p in re.split(r"\n\s*\n", merged) if p.strip()]
    punctuation = {mark: merged.count(mark) for mark in [".", ",", "!", "?", ";", ":", "(", ")", "-", "—"]}
    content_words = [w for w in tokenized if len(w) > 2 and w not in STOPWORDS]
    top = [word for word, _ in Counter(content_words).most_common(15)]
    tone = infer_tone(merged, avg, punctuation)
    return VoiceProfile(
        sample_count=len(paths),
        word_count=len(tokenized),
        sentence_count=len(sents),
        avg_sentence_words=round(avg, 2),
        sentence_rhythm="mixed" if stdev >= 8 else ("short" if avg < 14 else "long"),
        paragraph_style="brief" if paragraphs and statistics.mean([len(words(p)) for p in paragraphs]) < 60 else "developed",
        punctuation=punctuation,
        top_words=top,
        likely_tone=tone,
    )


def infer_tone(text: str, avg_sentence_words: float, punctuation: dict[str, int]) -> list[str]:
    tone: list[str] = []
    lower = text.lower()
    if re.search(r"\b(i|me|my|we|our)\b", lower):
        tone.append("personal")
    if re.search(r"\b(shit|fuck|damn|lol|haha)\b", lower):
        tone.append("casual")
    if punctuation.get("?", 0) > max(2, punctuation.get("!", 0)):
        tone.append("question-led")
    if avg_sentence_words < 14:
        tone.append("direct")
    if avg_sentence_words > 24:
        tone.append("expansive")
    if re.search(r"\b(api|apis|cli|model|repo|code|system|workflow|架构|模型|代码)\b", lower):
        tone.append("technical")
    return tone or ["plain"]


def audit_text(text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for name, pattern, message in AI_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.I):
            snippet = text[max(0, match.start() - 50): match.end() + 50].strip()
            findings.append({"pattern": name, "match": match.group(0), "message": message, "snippet": snippet})
    return findings


def simple_humanize(text: str, profile: VoiceProfile | None = None) -> str:
    out = text
    out = re.sub(r"\*\*([^*]+)\*\*", r"\1", out)
    out = re.sub(r"[\U0001F300-\U0001FAFF]", "", out)
    out = out.replace("—", ". ").replace("–", "-")
    for pattern, replacement in REPLACEMENTS:
        out = pattern.sub(replacement, out)
    out = re.sub(r"\b(not just|not only|not merely)\s+([^,.;]+),?\s+but\s+", r"", out, flags=re.I)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r" ?\n ?", "\n", out)
    if profile and profile.sentence_rhythm == "short":
        out = shorten_long_sentences(out)
    return out.strip()


def shorten_long_sentences(text: str) -> str:
    chunks: list[str] = []
    for sentence in sentences(text):
        if len(words(sentence)) > 28 and "," in sentence:
            first, rest = sentence.split(",", 1)
            chunks.append(first.strip().rstrip(".") + ".")
            chunks.append(rest.strip().lstrip().capitalize())
        else:
            chunks.append(sentence)
    return " ".join(chunks)


def claim_like(sentence: str) -> bool:
    if len(words(sentence)) < 6:
        return False
    if re.search(r"\b(i think|i feel|in my opinion|should|prefer|like|love|hate)\b", sentence, re.I):
        return False
    return bool(re.search(r"\b(is|are|was|were|has|have|stores?|contains?|includes?|launched|released|founded|costs?|claims?|according|research|study|report|20\d{2}|19\d{2})\b", sentence, re.I))


def extract_claims(text: str) -> list[str]:
    return [sentence for sentence in sentences(text) if claim_like(sentence)]


def fetch_json(url: str, timeout: float = 6.0) -> object:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "humanize-skill/0.1 (+https://github.com/)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def fetch_text(url: str, timeout: float = 6.0) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "humanize-skill/0.1 (+https://github.com/)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("&quot;", '"').replace("&#x27;", "'").replace("&#039;", "'").replace("&amp;", "&")
    return re.sub(r"\s+", " ", value).strip()


def reconstruct_openalex_abstract(index: object, max_words: int = 80) -> str:
    if not isinstance(index, dict):
        return ""
    positioned: list[tuple[int, str]] = []
    for word, positions in index.items():
        if not isinstance(word, str) or not isinstance(positions, list):
            continue
        for pos in positions:
            if isinstance(pos, int):
                positioned.append((pos, word))
    positioned.sort()
    return " ".join(word for _, word in positioned[:max_words])


def search_wikipedia(query: str, limit: int = 3) -> list[ReferenceSource]:
    params = urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "format": "json",
        "srlimit": str(limit),
        "srsearch": query,
    })
    data = fetch_json(f"https://en.wikipedia.org/w/api.php?{params}")
    results: list[ReferenceSource] = []
    if not isinstance(data, dict):
        return results
    for item in data.get("query", {}).get("search", []):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        pageid = item.get("pageid")
        snippet = strip_html(str(item.get("snippet", "")))
        if title and pageid:
            results.append(ReferenceSource(
                provider="wikipedia",
                title=title,
                url=f"https://en.wikipedia.org/?curid={pageid}",
                snippet=snippet,
            ))
    return results


def search_openalex(query: str, limit: int = 3) -> list[ReferenceSource]:
    params = urllib.parse.urlencode({"search": query, "per-page": str(limit)})
    data = fetch_json(f"https://api.openalex.org/works?{params}")
    results: list[ReferenceSource] = []
    if not isinstance(data, dict):
        return results
    for item in data.get("results", []):
        if not isinstance(item, dict):
            continue
        title = str(item.get("display_name", "")).strip()
        url = str(item.get("doi") or item.get("id") or "").strip()
        if url.startswith("https://doi.org/"):
            pass
        elif url.startswith("10."):
            url = f"https://doi.org/{url}"
        snippet = reconstruct_openalex_abstract(item.get("abstract_inverted_index"))
        if title:
            results.append(ReferenceSource(
                provider="openalex",
                title=title,
                url=url,
                snippet=snippet,
            ))
    return results


def search_crossref(query: str, limit: int = 3) -> list[ReferenceSource]:
    params = urllib.parse.urlencode({"query": query, "rows": str(limit)})
    data = fetch_json(f"https://api.crossref.org/works?{params}")
    results: list[ReferenceSource] = []
    if not isinstance(data, dict):
        return results
    items = data.get("message", {}).get("items", [])
    for item in items:
        if not isinstance(item, dict):
            continue
        title_value = item.get("title") or []
        title = str(title_value[0] if title_value else "").strip()
        url = str(item.get("URL") or "").strip()
        snippet = strip_html(str(item.get("abstract") or ""))
        if title:
            results.append(ReferenceSource(
                provider="crossref",
                title=title,
                url=url,
                snippet=snippet,
            ))
    return results


def search_duckduckgo(query: str, limit: int = 3) -> list[ReferenceSource]:
    params = urllib.parse.urlencode({"q": query})
    html = fetch_text(f"https://html.duckduckgo.com/html/?{params}")
    results: list[ReferenceSource] = []
    pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>.*?'
        r'<a[^>]+class="result__snippet"[^>]*>(?P<snippet>.*?)</a>',
        re.S,
    )
    for match in pattern.finditer(html):
        href = urllib.parse.unquote(match.group("href"))
        parsed = urllib.parse.urlparse(href)
        query_values = urllib.parse.parse_qs(parsed.query)
        url = query_values.get("uddg", [href])[0]
        title = strip_html(match.group("title"))
        snippet = strip_html(match.group("snippet"))
        if title and url:
            results.append(ReferenceSource(
                provider="duckduckgo",
                title=title,
                url=url,
                snippet=snippet,
            ))
        if len(results) >= limit:
            break
    return results


def external_references_for_claim(claim: str, max_results: int = 5) -> list[ReferenceSource]:
    query = " ".join(key_terms(claim, limit=8)) or claim
    sources: list[ReferenceSource] = []
    for searcher in (search_duckduckgo, search_wikipedia, search_openalex, search_crossref):
        try:
            sources.extend(searcher(query, limit=max(1, max_results // 2)))
        except Exception:
            continue
        if len(sources) >= max_results:
            break
    return sources[:max_results]


def source_text(source: ReferenceSource) -> str:
    return f"{source.title}. {source.snippet}"


def support_score(
    claim_terms: Sequence[str],
    evidence_words: set[str],
    *,
    min_threshold: int = 2,
    min_ratio: float = 0.0,
) -> tuple[list[str], bool, float]:
    overlap = [w for w in claim_terms if w in evidence_words]
    unique_claim_terms = set(claim_terms)
    threshold = max(min_threshold, min(6, len(unique_claim_terms) // 2))
    ratio = len(set(overlap)) / max(1, len(unique_claim_terms))
    supported = len(set(overlap)) >= threshold and ratio >= min_ratio
    confidence = min(0.9, 0.4 + len(set(overlap)) / max(1, len(set(claim_terms)))) if supported else 0.35
    return sorted(set(overlap))[:12], supported, confidence


def best_reference_support(claim_terms: Sequence[str], sources: Sequence[ReferenceSource]) -> tuple[list[str], bool, float, list[ReferenceSource]]:
    best_overlap: list[str] = []
    best_confidence = 0.2
    supporting: list[ReferenceSource] = []
    for source in sources:
        overlap, supported, confidence = support_score(
            claim_terms,
            set(words(source_text(source))),
            min_threshold=3,
            min_ratio=0.6,
        )
        if confidence > best_confidence:
            best_overlap = overlap
            best_confidence = confidence
        if supported:
            supporting.append(source)
    return best_overlap, bool(supporting), best_confidence, supporting


def factcheck(
    text: str,
    evidence_texts: Sequence[str],
    *,
    external: bool = False,
    max_external_results: int = 5,
    external_lookup: Callable[[str, int], list[ReferenceSource]] | None = None,
) -> list[dict[str, object]]:
    evidence = "\n".join(evidence_texts)
    evidence_words = set(words(evidence))
    results: list[dict[str, object]] = []
    for claim in extract_claims(text):
        claim_terms = key_terms(claim, limit=20)
        overlap, supported, confidence = support_score(claim_terms, evidence_words)
        sources: list[ReferenceSource] = []
        source_type = "provided_evidence" if evidence_texts else "none"
        if supported:
            status = "supported"
        elif external:
            lookup = external_lookup or external_references_for_claim
            sources = lookup(claim, max_external_results)
            overlap, supported, confidence, supporting_sources = best_reference_support(claim_terms, sources)
            if supported:
                status = "supported"
                source_type = "external_reference"
                sources = supporting_sources
            else:
                status = "needs_evidence"
                source_type = "external_reference" if sources else "none"
        elif not evidence_texts:
            status = "needs_evidence"
            confidence = 0.2
        else:
            status = "needs_evidence"
        results.append({
            "claim": claim,
            "status": status,
            "confidence": round(confidence, 2),
            "source_type": source_type,
            "matched_terms": overlap,
            "references": [asdict(source) for source in sources],
        })
    return results


def load_profile(path: Path | None) -> VoiceProfile | None:
    if not path:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return VoiceProfile(**data)


def print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def cmd_profile(args: argparse.Namespace) -> None:
    profile = build_profile(args.paths)
    data = asdict(profile)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print_json(data)


def cmd_audit(args: argparse.Namespace) -> None:
    print_json(audit_text(read_text(args.path)))


def cmd_humanize(args: argparse.Namespace) -> None:
    profile = load_profile(args.profile)
    print(simple_humanize(read_text(args.path), profile))


def cmd_factcheck(args: argparse.Namespace) -> None:
    draft = read_text(args.path)
    evidence = [read_text(path) for path in args.evidence]
    print_json(factcheck(
        draft,
        evidence,
        external=args.external,
        max_external_results=args.max_external_results,
    ))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local helper for humanize-skill")
    sub = parser.add_subparsers(dest="command", required=True)

    profile = sub.add_parser("profile", help="Build a compact voice profile from local samples")
    profile.add_argument("paths", nargs="+", type=Path)
    profile.add_argument("--out", type=Path)
    profile.set_defaults(func=cmd_profile)

    audit = sub.add_parser("audit", help="Find AI-writing patterns")
    audit.add_argument("path", type=Path)
    audit.set_defaults(func=cmd_audit)

    humanize = sub.add_parser("humanize", help="Apply a simple rules-based cleanup")
    humanize.add_argument("path", type=Path)
    humanize.add_argument("--profile", type=Path)
    humanize.set_defaults(func=cmd_humanize)

    fc = sub.add_parser("factcheck", help="Extract claim-like sentences and compare to evidence files")
    fc.add_argument("path", type=Path)
    fc.add_argument("--evidence", nargs="*", type=Path, default=[])
    fc.add_argument("--external", action="store_true", help="Search public external references when provided evidence is insufficient")
    fc.add_argument("--max-external-results", type=int, default=5)
    fc.set_defaults(func=cmd_factcheck)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
