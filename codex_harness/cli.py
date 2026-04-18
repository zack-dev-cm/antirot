from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import AuditReport, audit_repository
from .system_audit import SystemAuditReport, audit_local_codex_environment
from .templates import derive_project_name, scaffold_files


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-harness",
        description="Scaffold and audit a Codex-native engineering harness with open-source release gates.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init",
        help="Write AGENTS.md, project-scoped agents, and Codex docs into a repo.",
    )
    init_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to initialize. Defaults to the current directory.",
    )
    init_parser.add_argument(
        "--project-name",
        help="Optional display name. Defaults to the target directory name.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing scaffold files.",
    )
    init_parser.set_defaults(func=run_init)

    audit_parser = subparsers.add_parser(
        "audit",
        help="Audit whether a repo has a usable Codex harness and publishable public surface.",
    )
    audit_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to audit. Defaults to the current directory.",
    )
    audit_parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Output format.",
    )
    audit_parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any ERROR issue is found.",
    )
    audit_parser.add_argument(
        "--min-score",
        type=int,
        default=None,
        help="Exit non-zero when the audit score falls below this threshold.",
    )
    audit_parser.set_defaults(func=run_audit)

    system_audit_parser = subparsers.add_parser(
        "system-audit",
        help="Audit local Codex skills, cached plugins, project references, and recent usage.",
    )
    system_audit_parser.add_argument(
        "--codex-home",
        default="~/.codex",
        help="Codex home directory to inspect. Defaults to ~/.codex.",
    )
    system_audit_parser.add_argument(
        "--scan-root",
        action="append",
        default=[],
        help="Root directory to scan for git repos and project-level Codex assets. Repeat as needed.",
    )
    system_audit_parser.add_argument(
        "--recent-usage-days",
        type=int,
        default=14,
        help="Number of recent days of session usage to summarize. Default: 14.",
    )
    system_audit_parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum depth for repo discovery under scan roots. Default: 3.",
    )
    system_audit_parser.add_argument(
        "--marker-discovery",
        action="store_true",
        help="Discover only repos with Codex markers such as SKILL.md or plugin manifests. Recommended for large workspace roots.",
    )
    system_audit_parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Output format.",
    )
    system_audit_parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any ERROR issue is found.",
    )
    system_audit_parser.add_argument(
        "--min-score",
        type=int,
        default=None,
        help="Exit non-zero when the audit score falls below this threshold.",
    )
    system_audit_parser.set_defaults(func=run_system_audit)
    return parser


def run_init(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    root.mkdir(parents=True, exist_ok=True)

    project_name = args.project_name or derive_project_name(root)
    files = scaffold_files(project_name)
    conflicts = [item.path for item in files if (root / item.path).exists()]
    if conflicts and not args.force:
        print("Refusing to overwrite existing Codex harness files:")
        for path in conflicts:
            print(f"- {path}")
        print("Re-run with --force to replace them.")
        return 1

    for item in files:
        target = root / item.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item.content, encoding="utf-8")

    print(f"Initialized Codex harness for {project_name} at {root}")
    print(f"Wrote {len(files)} files.")
    return 0


def run_audit(args: argparse.Namespace) -> int:
    report = audit_repository(Path(args.path))
    print(_render_report(report, args.format))
    if args.strict and report.has_errors:
        return 1
    if args.min_score is not None and report.score < args.min_score:
        return 1
    return 0


def run_system_audit(args: argparse.Namespace) -> int:
    report = audit_local_codex_environment(
        Path(args.codex_home),
        scan_roots=[Path(path) for path in args.scan_root] if args.scan_root else None,
        recent_usage_days=args.recent_usage_days,
        max_depth=args.max_depth,
        marker_discovery=args.marker_discovery,
    )
    print(_render_report(report, args.format))
    if args.strict and report.has_errors:
        return 1
    if args.min_score is not None and report.score < args.min_score:
        return 1
    return 0


def _render_report(report: AuditReport | SystemAuditReport, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(report.to_dict(), indent=2)
    if fmt == "markdown":
        return report.to_markdown()
    return report.to_text()
