# ClawHub Skills Security

`skills/clawhub-skills-security/` is a reusable Codex skill for pre-install and
pre-publish review of ClawHub skill bundles.

## Contract

- Use it before installing, enabling, or recommending any newly downloaded
  ClawHub skill.
- Use it before publishing a skill when the public surface mentions outreach,
  logged-in browser control, or platform handoffs.
- Treat `PASS` as "no blocking static findings in the reviewed artifact", not
  as proof of absolute safety.
- Treat `REVIEW` and `BLOCK` as no-install outcomes unless the user explicitly
  accepts the residual risk.
- Keep the scanner standard-library-only so reviewers can inspect it without a
  dependency bootstrap.

## Scanner

Run the scanner against an unpacked skill directory:

```bash
python3 skills/clawhub-skills-security/scripts/audit_clawhub_skill.py /path/to/skill
```

Use `--json` for CI or scripted reports. The scanner returns exit code `0` only
for `PASS`; any warning or blocking finding returns non-zero so installation
automation stops by default.

## Review Focus

- frontmatter and `SKILL.md` trigger text
- prompt override attempts and absolute safety claims
- secret-like values, credential files, and private paths
- shell execution, network clients, dynamic code execution, and package installs
- named outreach platforms, logged-in browser-control language, automated
  message delivery, scraping, selfbot, and bulk outreach terms
- archives, binaries, symlinks, and large opaque files
- dependency manifests with loose or unpinned dependencies

Manual review still matters because static signatures cannot prove intent,
runtime behavior, publisher identity, or supply-chain integrity.
