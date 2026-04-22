# Publish Checklist

Use this when preparing the skill for GitHub and ClawHub.

## Local Review

1. Confirm `SKILL.md` frontmatter:
   - `name: agentic-codex-dev`
   - `description: ...`
   - `version: 0.1.0`
2. Confirm the folder name is the intended ClawHub slug: `agentic-codex-dev`.
3. Confirm every file is text-based and needed:
   - `SKILL.md`
   - `agents/openai.yaml`
   - `references/source-review.md`
   - `references/publish-checklist.md`
4. Search for private paths, local URLs, tokens, and copied private notes.
5. Run the repository gate:

```bash
python3 -m pytest -q
python3 -m codex_harness audit . --strict --min-score 90
```

## GitHub Publish

From the repository root:

```bash
git status --short
git add skills/agentic-codex-dev docs/codex/agentic-codex-dev-skill.md
git commit -m "Add agentic Codex development skill"
git push
```

If the worktree contains unrelated user changes, stage only the files above.

## ClawHub Publish

The ClawHub CLI must be installed and logged in:

```bash
clawhub whoami
```

Publish the skill:

```bash
clawhub skill publish skills/agentic-codex-dev --version 0.1.0
```

After publishing:

```bash
clawhub inspect agentic-codex-dev --files
```

Check that the listing shows the expected files, summary, version, and homepage. Remember that ClawHub publishes skills under MIT-0.

## Manual Acceptance

The skill is publish-ready when:

- a reviewer can understand the runtime behavior by reading `SKILL.md` alone
- the source review explains why each major rule exists
- no command in the skill installs software, reads credentials, restarts services, or changes global agent state
- the repository tests and audit gate pass
- the ClawHub listing, if published, points back to the GitHub source
