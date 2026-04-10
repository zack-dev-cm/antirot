from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
import sys
from typing import Any

from .linting import LintReport, lint_markdown, severity_rank


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="antirot",
        description="Lint Markdown drafts for unsupported claims, broken citations, and draft markers.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    lint_parser = subparsers.add_parser(
        "lint",
        help="Lint a Markdown draft and print an AntiRot report.",
    )
    lint_parser.add_argument(
        "draft",
        nargs="?",
        help="Path to the Markdown draft. Optional when draft_glob is set in .antirot.toml.",
    )
    lint_parser.add_argument(
        "--references",
        help="Optional references file (.bib, Markdown, or numbered reference list).",
    )
    lint_parser.add_argument(
        "--format",
        choices=("text", "json", "markdown", "sarif"),
        default="text",
        help="Output format.",
    )
    lint_parser.add_argument(
        "--output",
        help="Optional output file. If omitted, the report is printed to stdout.",
    )
    lint_parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any issue is found.",
    )
    lint_parser.add_argument(
        "--min-score",
        type=int,
        default=None,
        help="Exit non-zero when the score falls below this threshold.",
    )
    lint_parser.add_argument(
        "--config",
        help="Optional path to an AntiRot config file. Defaults to .antirot.toml when present.",
    )
    lint_parser.set_defaults(func=run_lint)

    init_parser = subparsers.add_parser(
        "init",
        help="Create a starter AntiRot config in the current directory.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing config file.",
    )
    init_parser.set_defaults(func=run_init)
    return parser


def run_lint(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    references = args.references if args.references is not None else config.get("references")
    references = validate_references_path(references)
    draft_paths = resolve_drafts(args.draft, config, references)
    strict = args.strict or bool(config.get("strict", False))
    min_score = args.min_score if args.min_score is not None else as_int(config.get("min_score"))

    rendered_reports: list[str] = []
    has_failure = False
    reports: list[LintReport] = []
    for draft_path in draft_paths:
        report = lint_markdown(draft_path, references)
        reports.append(report)
        if args.format == "markdown":
            rendered_reports.append(report.to_markdown())
        elif args.format == "text":
            rendered_reports.append(report.to_text())

        if strict and report.issue_count:
            has_failure = True
        if min_score is not None and report.score < min_score:
            has_failure = True

    if args.format == "json":
        payload: object
        if len(reports) == 1:
            payload = reports[0].to_dict()
        else:
            payload = [report.to_dict() for report in reports]
        rendered = json.dumps(payload, indent=2)
    elif args.format == "sarif":
        rendered = json.dumps(build_sarif(reports), indent=2)
    else:
        rendered = "\n\n".join(rendered_reports)

    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if has_failure:
        return 1
    return 0


def run_init(args: argparse.Namespace) -> int:
    config_path = Path(".antirot.toml")
    if config_path.exists() and not args.force:
        print("Refusing to overwrite existing .antirot.toml. Use --force to replace it.")
        return 1

    config_path.write_text(render_starter_config(), encoding="utf-8")
    print(f"Wrote {config_path}")
    print("Update draft_glob and optional references for your project, then run `antirot lint`.")
    return 0


def render_starter_config() -> str:
    return (
        "\n".join(
            [
                "# AntiRot starter config",
                "# Update draft_glob and optional references for your project before linting.",
                "",
                '# draft_glob = "docs/**/*.md"',
                '# references = "docs/references.md"',
                "strict = true",
                "min_score = 80",
            ]
        )
        + "\n"
    )


def load_config(config_arg: str | None) -> dict[str, Any]:
    config_path = Path(config_arg) if config_arg else Path(".antirot.toml")
    if not config_path.exists():
        return {}

    data: dict[str, Any] = {}
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        data[key] = parse_scalar(raw_value)
    return data


def parse_scalar(raw_value: str) -> Any:
    if raw_value.startswith(("'", '"')) and raw_value.endswith(("'", '"')):
        return raw_value[1:-1]
    lowered = raw_value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if raw_value.isdigit():
        return int(raw_value)
    return raw_value


def validate_references_path(references: Any) -> str | None:
    if not isinstance(references, str) or not references:
        return None
    if Path(references).exists():
        return references
    raise SystemExit(
        f"References file not found: {references}. Update --references or .antirot.toml."
    )


def resolve_drafts(
    draft_arg: str | None,
    config: dict[str, Any],
    references: str | None = None,
) -> list[str]:
    if draft_arg:
        return [draft_arg]
    pattern = config.get("draft_glob")
    if isinstance(pattern, str):
        matches = sorted(glob.glob(pattern, recursive=True))
        if references:
            reference_path = str(Path(references))
            matches = [match for match in matches if str(Path(match)) != reference_path]
        if matches:
            return matches
    raise SystemExit(
        "No draft path supplied and no matching draft_glob found in config."
    )


def as_int(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def build_sarif(reports: list[LintReport]) -> dict[str, object]:
    rules: dict[str, dict[str, str]] = {}
    results: list[dict[str, object]] = []
    for report in reports:
        for issue in report.issues:
            if issue.code not in rules:
                rules[issue.code] = {
                    "id": issue.code,
                    "shortDescription": {"text": issue.code.replace("-", " ")},
                    "helpUri": "https://github.com/zack-dev-cm/antirot",
                }
            results.append(
                {
                    "ruleId": issue.code,
                    "level": issue.severity,
                    "message": {"text": issue.detail},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": report.file_path},
                                "region": {"startLine": issue.line},
                            }
                        }
                    ],
                }
            )

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "AntiRot",
                        "informationUri": "https://github.com/zack-dev-cm/antirot",
                        "rules": [
                            rules[rule_id]
                            for rule_id in sorted(
                                rules,
                                key=lambda rule_id: (
                                    severity_rank(
                                        next(
                                            issue.severity
                                            for report in reports
                                            for issue in report.issues
                                            if issue.code == rule_id
                                        )
                                    ),
                                    rule_id,
                                ),
                            )
                        ],
                    }
                },
                "results": results,
            }
        ],
    }


if __name__ == "__main__":
    sys.exit(main())
