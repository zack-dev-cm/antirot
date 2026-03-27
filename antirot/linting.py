from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import re
from pathlib import Path
from typing import Iterable


TODO_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX|HACK)\b", re.IGNORECASE)
CITEKEY_BLOCK_RE = re.compile(r"\[@([^\]]+)\]")
NUMERIC_CITATION_RE = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")
BIB_ENTRY_RE = re.compile(r"@\w+\{([^,]+),")
MARKDOWN_CITE_DEF_RE = re.compile(r"\[@([^\]]+)\]")
NUMBERED_REF_RE = re.compile(
    r"^\s*(?:[-*]\s+)?(?:\[(\d+)\]|(\d+)\.)\s+",
    re.MULTILINE,
)

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


def severity_rank(severity: str) -> int:
    return 0 if severity == "error" else 1

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


def lint_markdown(
    markdown_path: str | Path,
    references_path: str | Path | None = None,
) -> LintReport:
    markdown_path = Path(markdown_path)
    text = markdown_path.read_text(encoding="utf-8")
    reference_ids = load_reference_ids(references_path) if references_path else set()
    issues: list[Issue] = []

    claim_count = 0
    cited_claim_count = 0
    citation_count = 0
    valid_citation_count = 0

    for line_number, sentence in iter_sentences_with_lines(text):
        normalized = sentence.strip()
        if not normalized:
            continue

        citation_ids = extract_citation_ids(normalized)
        sentence_has_citation = bool(citation_ids)
        citation_count += len(citation_ids)
        valid_ids = [cite_id for cite_id in citation_ids if cite_id in reference_ids]
        valid_citation_count += len(valid_ids)

        for cite_id in citation_ids:
            if reference_ids and cite_id not in reference_ids:
                issues.append(
                    Issue(
                        code="citation-not-found",
                        severity="error",
                        line=line_number,
                        sentence=normalized,
                        detail=f"Citation `{cite_id}` is not defined in the references file.",
                    )
                )

        if TODO_RE.search(normalized):
            issues.append(
                Issue(
                    code="draft-marker",
                    severity="warning",
                    line=line_number,
                    sentence=normalized,
                    detail="Draft marker present. Remove TODO/TBD/FIXME before release.",
                )
            )

        claim_like = is_claim_like(normalized)
        if claim_like:
            claim_count += 1
            if sentence_has_citation:
                cited_claim_count += 1
            else:
                issues.append(
                    Issue(
                        code="unsupported-claim",
                        severity="error",
                        line=line_number,
                        sentence=normalized,
                        detail="Claim-like sentence has no visible citation anchor.",
                    )
                )

        if has_numeric_claim(normalized) and not sentence_has_citation:
            issues.append(
                Issue(
                    code="number-without-citation",
                    severity="error",
                    line=line_number,
                    sentence=normalized,
                    detail="Numeric claim appears without a nearby citation.",
                )
            )

        if has_hype_language(normalized) and not sentence_has_citation:
            issues.append(
                Issue(
                    code="hype-without-evidence",
                    severity="warning",
                    line=line_number,
                    sentence=normalized,
                    detail="High-confidence or hype language needs a citation or weaker wording.",
                )
            )

        if has_comparison_language(normalized) and not sentence_has_citation:
            issues.append(
                Issue(
                    code="comparison-without-benchmark",
                    severity="warning",
                    line=line_number,
                    sentence=normalized,
                    detail="Comparative claim appears without benchmark evidence.",
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
    for match in MARKDOWN_CITE_DEF_RE.finditer(text):
        ids.update(_split_citekey_block(match.group(1)))
    for match in NUMBERED_REF_RE.finditer(text):
        ids.add(match.group(1) or match.group(2))
    return {item for item in ids if item}


def extract_citation_ids(sentence: str) -> list[str]:
    ids: list[str] = []
    for match in CITEKEY_BLOCK_RE.finditer(sentence):
        ids.extend(_split_citekey_block(match.group(1)))
    for match in NUMERIC_CITATION_RE.finditer(sentence):
        ids.extend(_expand_numeric_block(match.group(1)))
    return ids


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


def iter_sentences_with_lines(text: str) -> Iterable[tuple[int, str]]:
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("|"):
            continue
        chunks = re.split(r"(?<=[.!?])\s+", line)
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk:
                yield line_number, chunk


def has_numeric_claim(sentence: str) -> bool:
    return bool(re.search(r"\b\d+(?:\.\d+)?%?\b", sentence))


def has_hype_language(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(word in lowered for word in HYPE_WORDS)


def has_comparison_language(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(word in lowered for word in COMPARISON_WORDS)


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
