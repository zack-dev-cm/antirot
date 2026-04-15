from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import re
from pathlib import Path
from typing import Iterable


TODO_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX|HACK)\b", re.IGNORECASE)
CITEKEY_BLOCK_RE = re.compile(r"\[@([^\]]+)\]")
NUMERIC_CITATION_RE = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")
CITATION_TOKEN_RE = re.compile(r"\[(?:@[^\]]+|\^[^\]]+|\d+(?:\s*[-,]\s*\d+)*)\]")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]]+)\]")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:", re.MULTILINE)
BIB_ENTRY_RE = re.compile(r"@\w+\{([^,]+),")
MARKDOWN_CITE_DEF_RE = re.compile(r"\[@([^\]]+)\]")
NUMBERED_REF_RE = re.compile(
    r"^\s*(?:[-*]\s+)?(?:\[(\d+)\]|(\d+)\.)\s+",
    re.MULTILINE,
)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
RAW_URL_RE = re.compile(r"\bhttps?://[^\s)>]+", re.IGNORECASE)
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
ARXIV_RE = re.compile(r"\barxiv:\d{4}\.\d{4,5}(?:v\d+)?\b", re.IGNORECASE)
REF_HEADING_RE = re.compile(
    r"^\s{0,3}#{1,6}\s+(references|bibliography|works cited)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
REFERENCE_LINK_DEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s+\S+")

HYPE_WORDS = (
    "state-of-the-art",
    "sota",
    "breakthrough",
    "novel",
    "unprecedented",
    "revolutionary",
    "guarantees",
    "proves",
    "world-class",
)
COMPARISON_WORDS = (
    "better",
    "faster",
    "stronger",
    "safer",
    "more accurate",
    "more efficient",
    "outperform",
    "beats",
    "superior",
)
CLAIM_CUES = (
    "we show",
    "we find",
    "results show",
    "demonstrate",
    "achieves",
    "improves",
    "reduces",
    "increases",
    "first",
    "best",
)
ABSOLUTE_PHRASES = (
    "0.0%",
    "100%",
    "representative of all",
    "without any human oversight",
    "all practical",
    "all real-world",
)
ABSOLUTE_WORD_RE = re.compile(
    r"\b(?:guarantee(?:s|d)?|prove(?:s|d)?|never|always|perfect|"
    r"eliminate(?:s|d)?|universal(?:ly)?)\b",
    re.IGNORECASE,
)
NON_CLAIM_NUMBER_PATTERNS = (
    re.compile(
        r"\b(?:section|sec\.|figure|fig\.|table|appendix|chapter|step|phase|"
        r"equation|eq\.|algorithm|page)\s+\d+[a-z]?\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b[A-Z]{2,}-\d+(?:\.\d+)*\b"),
    re.compile(r"\bv\d+(?:\.\d+)+\b", re.IGNORECASE),
    re.compile(r"\[\s*\d+(?:\s*,\s*\d+)+\s*\]"),
)


@dataclass
class Issue:
    code: str
    severity: str
    line: int
    sentence: str
    detail: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class LintReport:
    file_path: str
    score: int
    issue_count: int
    claim_count: int
    cited_claim_count: int
    citation_count: int
    valid_citation_count: int
    issues: list[Issue] = field(default_factory=list)

    @property
    def evidence_coverage(self) -> float:
        if self.claim_count == 0:
            return 1.0
        return round(self.cited_claim_count / self.claim_count, 3)

    @property
    def citation_validity(self) -> float:
        if self.citation_count == 0:
            return 1.0
        return round(self.valid_citation_count / self.citation_count, 3)

    def to_dict(self) -> dict[str, object]:
        return {
            "file_path": self.file_path,
            "score": self.score,
            "issue_count": self.issue_count,
            "claim_count": self.claim_count,
            "cited_claim_count": self.cited_claim_count,
            "citation_count": self.citation_count,
            "valid_citation_count": self.valid_citation_count,
            "evidence_coverage": self.evidence_coverage,
            "citation_validity": self.citation_validity,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_markdown(self) -> str:
        lines = [
            f"# AntiRot Report: `{self.file_path}`",
            "",
            f"- Score: **{self.score}/100**",
            f"- Claims: **{self.claim_count}**",
            f"- Evidence coverage: **{self.evidence_coverage:.1%}**",
            f"- Citation validity: **{self.citation_validity:.1%}**",
            f"- Issues: **{self.issue_count}**",
            "",
        ]
        if not self.issues:
            lines.append("No issues found.")
            return "\n".join(lines)

        lines.extend(
            [
                "| Severity | Code | Line | Detail |",
                "| --- | --- | ---: | --- |",
            ]
        )
        for issue in self.issues:
            detail = issue.detail.replace("|", "\\|")
            lines.append(
                f"| {issue.severity} | `{issue.code}` | {issue.line} | {detail} |"
            )
        return "\n".join(lines)

    def to_text(self) -> str:
        lines = [
            f"AntiRot report for {self.file_path}",
            f"score={self.score}/100 claims={self.claim_count} "
            f"coverage={self.evidence_coverage:.1%} "
            f"citation_validity={self.citation_validity:.1%} issues={self.issue_count}",
        ]
        if not self.issues:
            lines.append("No issues found.")
            return "\n".join(lines)

        for issue in self.issues:
            lines.append(
                f"- {issue.severity.upper()} {issue.code} line {issue.line}: {issue.detail}"
            )
        return "\n".join(lines)


@dataclass
class SentenceRecord:
    line: int
    sentence: str
    paragraph: str


def severity_rank(severity: str) -> int:
    return 0 if severity == "error" else 1


def lint_markdown(
    markdown_path: str | Path,
    references_path: str | Path | None = None,
) -> LintReport:
    markdown_path = Path(markdown_path)
    text = markdown_path.read_text(encoding="utf-8")

    reference_ids = load_reference_ids_from_document(text)
    if references_path:
        reference_ids.update(load_reference_ids(references_path))
    references_loaded = bool(reference_ids)

    issues: list[Issue] = []
    claim_count = 0
    cited_claim_count = 0
    citation_count = 0
    valid_citation_count = 0

    for record in iter_sentence_records(text):
        normalized = record.sentence.strip()
        if not normalized:
            continue

        citation_ids = extract_citation_ids(normalized, reference_ids)
        sentence_support_ids = extract_support_ids(normalized, reference_ids)
        paragraph_support_ids = extract_support_ids(record.paragraph, reference_ids)
        sentence_has_support = (
            has_non_citation_support(sentence_support_ids)
            or has_non_citation_support(paragraph_support_ids)
            or has_valid_citation(citation_ids, reference_ids)
            or has_valid_citation(
                extract_citation_ids(record.paragraph, reference_ids),
                reference_ids,
            )
        )
        citation_count += len(citation_ids)

        valid_ids = [cite_id for cite_id in citation_ids if cite_id in reference_ids]
        valid_citation_count += len(valid_ids)

        if citation_ids and not references_loaded:
            issues.append(
                Issue(
                    code="citation-unverified",
                    severity="warning",
                    line=record.line,
                    sentence=normalized,
                    detail="Citation-like marker found, but no references file or document references section was loaded. It does not count as verified evidence.",
                )
            )

        for cite_id in citation_ids:
            if references_loaded and cite_id not in reference_ids:
                issues.append(
                    Issue(
                        code="citation-not-found",
                        severity="error",
                        line=record.line,
                        sentence=normalized,
                        detail=f"Citation `{cite_id}` is not defined in the references file or document references section.",
                    )
                )

        if TODO_RE.search(normalized):
            issues.append(
                Issue(
                    code="draft-marker",
                    severity="warning",
                    line=record.line,
                    sentence=normalized,
                    detail="Draft marker present. Remove TODO/TBD/FIXME before release.",
                )
            )

        claim_like = is_claim_like(normalized)
        if claim_like:
            claim_count += 1
            if sentence_has_support:
                cited_claim_count += 1
            else:
                issues.append(
                    Issue(
                        code="unsupported-claim",
                        severity="error",
                        line=record.line,
                        sentence=normalized,
                        detail="Claim-like sentence has no nearby evidence anchor in the sentence or paragraph.",
                    )
                )

        if has_numeric_claim(normalized) and not sentence_has_support:
            issues.append(
                Issue(
                    code="number-without-citation",
                    severity="error",
                    line=record.line,
                    sentence=normalized,
                    detail="Numeric claim appears without a nearby citation, link, DOI, arXiv id, or paragraph-level evidence anchor.",
                )
            )

        if has_hype_language(normalized) and not sentence_has_support:
            issues.append(
                Issue(
                    code="hype-without-evidence",
                    severity="warning",
                    line=record.line,
                    sentence=normalized,
                    detail="High-confidence or hype language needs evidence or weaker wording.",
                )
            )

        if has_comparison_language(normalized) and not sentence_has_support:
            issues.append(
                Issue(
                    code="comparison-without-benchmark",
                    severity="warning",
                    line=record.line,
                    sentence=normalized,
                    detail="Comparative claim appears without benchmark evidence nearby.",
                )
            )

        if has_absolute_language(normalized):
            issues.append(
                Issue(
                    code="absolute-claim",
                    severity="warning",
                    line=record.line,
                    sentence=normalized,
                    detail="Absolute or universal wording should be narrowed, scoped, or backed by unusually strong evidence.",
                )
            )

    score = max(
        0,
        100
        - severity_penalty(issues)
        - missing_evidence_penalty(claim_count, cited_claim_count)
        - citation_validity_penalty(citation_count, valid_citation_count),
    )

    return LintReport(
        file_path=str(markdown_path),
        score=score,
        issue_count=len(issues),
        claim_count=claim_count,
        cited_claim_count=cited_claim_count,
        citation_count=citation_count,
        valid_citation_count=valid_citation_count,
        issues=sorted(issues, key=lambda issue: (issue.line, issue.code)),
    )


def load_reference_ids(references_path: str | Path | None) -> set[str]:
    if references_path is None:
        return set()
    text = Path(references_path).read_text(encoding="utf-8")
    ids = set()
    ids.update(match.group(1).strip() for match in BIB_ENTRY_RE.finditer(text))
    ids.update(match.group(1).strip() for match in FOOTNOTE_DEF_RE.finditer(text))
    for match in MARKDOWN_CITE_DEF_RE.finditer(text):
        ids.update(_split_citekey_block(match.group(1)))
    for match in NUMBERED_REF_RE.finditer(text):
        ids.add(match.group(1) or match.group(2))
    return {item for item in ids if item}


def load_reference_ids_from_document(text: str) -> set[str]:
    ids = set(match.group(1).strip() for match in FOOTNOTE_DEF_RE.finditer(text))
    reference_section = extract_reference_section(text)
    if not reference_section:
        return ids

    ids.update(match.group(1).strip() for match in BIB_ENTRY_RE.finditer(reference_section))
    for match in MARKDOWN_CITE_DEF_RE.finditer(reference_section):
        ids.update(_split_citekey_block(match.group(1)))
    for match in NUMBERED_REF_RE.finditer(reference_section):
        ids.add(match.group(1) or match.group(2))
    return {item for item in ids if item}


def extract_reference_section(text: str) -> str:
    heading_match = REF_HEADING_RE.search(text)
    if not heading_match:
        return ""

    start = heading_match.end()
    next_heading = re.search(r"^\s{0,3}#{1,6}\s+", text[start:], re.MULTILINE)
    if next_heading:
        return text[start : start + next_heading.start()]
    return text[start:]


def extract_citation_ids(
    sentence: str,
    reference_ids: set[str] | None = None,
) -> list[str]:
    ids: list[str] = []
    for match in CITEKEY_BLOCK_RE.finditer(sentence):
        ids.extend(_split_citekey_block(match.group(1)))
    if reference_ids is None or any(item.isdigit() for item in reference_ids):
        for match in NUMERIC_CITATION_RE.finditer(sentence):
            numeric_ids = _expand_numeric_block(match.group(1))
            if reference_ids is None or all(item in reference_ids for item in numeric_ids):
                ids.extend(numeric_ids)
    for match in FOOTNOTE_REF_RE.finditer(sentence):
        ids.append(match.group(1).strip())
    return _unique_preserve_order(ids)


def extract_support_ids(
    text: str,
    reference_ids: set[str] | None = None,
) -> list[str]:
    anchors: list[str] = [f"cite:{item}" for item in extract_citation_ids(text, reference_ids)]
    anchors.extend(f"link:{match.group(1).strip()}" for match in MARKDOWN_LINK_RE.finditer(text))
    anchors.extend(f"url:{match.group(0)}" for match in RAW_URL_RE.finditer(text))
    anchors.extend(f"doi:{match.group(0).lower()}" for match in DOI_RE.finditer(text))
    anchors.extend(f"arxiv:{match.group(0).lower()}" for match in ARXIV_RE.finditer(text))
    return _unique_preserve_order(anchors)


def _unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def has_non_citation_support(support_ids: Iterable[str]) -> bool:
    return any(not item.startswith("cite:") for item in support_ids)


def has_valid_citation(citation_ids: Iterable[str], reference_ids: set[str]) -> bool:
    ids = [item for item in citation_ids if item]
    if not ids:
        return False
    if not reference_ids:
        return False
    return any(item in reference_ids for item in ids)


def _split_citekey_block(block: str) -> list[str]:
    keys = []
    for raw_part in re.split(r"[;,]", block):
        part = raw_part.strip()
        if part.startswith("@"):
            part = part[1:]
        if part:
            keys.append(part)
    return keys


def _expand_numeric_block(block: str) -> list[str]:
    parts = [part.strip() for part in block.split(",")]
    ids: list[str] = []
    for part in parts:
        if "-" in part:
            start_text, end_text = [segment.strip() for segment in part.split("-", 1)]
            if start_text.isdigit() and end_text.isdigit():
                start = int(start_text)
                end = int(end_text)
                if start <= end:
                    ids.extend(str(number) for number in range(start, end + 1))
                    continue
        if part.isdigit():
            ids.append(part)
    return ids


def iter_sentence_records(text: str) -> Iterable[SentenceRecord]:
    for line_number, paragraph in iter_paragraphs(text):
        for sentence in split_sentences(paragraph):
            normalized = sentence.strip()
            if not normalized:
                continue
            yield SentenceRecord(
                line=line_number,
                sentence=normalized,
                paragraph=paragraph,
            )


def iter_paragraphs(text: str) -> Iterable[tuple[int, str]]:
    buffer: list[str] = []
    start_line: int | None = None
    in_fence = False
    in_comment = False
    in_frontmatter = False

    def flush() -> Iterable[tuple[int, str]]:
        nonlocal buffer, start_line
        if not buffer or start_line is None:
            buffer = []
            start_line = None
            return []
        paragraph = " ".join(part.strip() for part in buffer if part.strip())
        result = [(start_line, paragraph)] if paragraph else []
        buffer = []
        start_line = None
        return result

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if line_number == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped in {"---", "..."}:
                in_frontmatter = False
            continue

        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue

        if "<!--" in stripped:
            before_comment = stripped.split("<!--", 1)[0].strip()
            if before_comment:
                stripped = before_comment
            else:
                yield from flush()
                if "-->" not in raw_line:
                    in_comment = True
                continue

        if FENCE_RE.match(stripped):
            yield from flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if not stripped:
            yield from flush()
            continue
        if stripped.startswith("#") or stripped.startswith("|") or stripped.startswith(">"):
            yield from flush()
            continue
        if FOOTNOTE_DEF_RE.match(stripped) or REFERENCE_LINK_DEF_RE.match(stripped):
            yield from flush()
            continue
        if LIST_ITEM_RE.match(stripped):
            yield from flush()
            content = LIST_ITEM_RE.sub("", stripped, count=1).strip()
            if content:
                yield line_number, content
            continue

        if start_line is None:
            start_line = line_number
        buffer.append(stripped)

    yield from flush()


def split_sentences(paragraph: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", paragraph) if part.strip()]


def has_numeric_claim(sentence: str) -> bool:
    candidate = CITATION_TOKEN_RE.sub(" ", sentence)
    for pattern in NON_CLAIM_NUMBER_PATTERNS:
        candidate = pattern.sub(" ", candidate)
    return bool(re.search(r"\b\d+(?:\.\d+)?%?\b", candidate))


def has_hype_language(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(word in lowered for word in HYPE_WORDS)


def has_comparison_language(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(word in lowered for word in COMPARISON_WORDS)


def has_absolute_language(sentence: str) -> bool:
    lowered = sentence.lower()
    return bool(ABSOLUTE_WORD_RE.search(sentence)) or any(
        phrase in lowered for phrase in ABSOLUTE_PHRASES
    )


def is_claim_like(sentence: str) -> bool:
    lowered = sentence.lower()
    if has_numeric_claim(sentence):
        return True
    if has_hype_language(sentence):
        return True
    if has_comparison_language(sentence):
        return True
    return any(cue in lowered for cue in CLAIM_CUES)


def severity_penalty(issues: list[Issue]) -> int:
    penalty = 0
    for issue in issues:
        penalty += 8 if issue.severity == "error" else 4
    return penalty


def missing_evidence_penalty(claim_count: int, cited_claim_count: int) -> int:
    if claim_count == 0:
        return 0
    missing = claim_count - cited_claim_count
    return round((missing / claim_count) * 20)


def citation_validity_penalty(citation_count: int, valid_citation_count: int) -> int:
    if citation_count == 0:
        return 0
    invalid = citation_count - valid_citation_count
    return round((invalid / citation_count) * 12)
