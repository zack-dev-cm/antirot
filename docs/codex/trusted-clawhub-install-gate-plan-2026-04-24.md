# Trusted ClawHub Install Gate

Date: 2026-04-24

## One-line product definition

`Trusted ClawHub Install Gate` is a trust-and-install control plane for ClawHub
skills: it resolves exactly what would be installed, audits provenance and
behavior before install, blocks obviously risky artifacts, warns on ambiguous
ones, and records a signed install receipt.

## Why this should exist

The strongest ClawHub pain is not discovery alone. It is trust under uncertainty.

Users are currently asking:

- Is this skill safe before it touches my machine?
- Who published it, and where is the real source?
- What changed between versions?
- If I install it, will it actually load and work?
- Why should I trust this scanner more than the thing it is scanning?

The live market evidence supports this:

- high ClawHub scale and weak official preventive gating
- strong public traction for vetting/scanner skills
- strong public traction for curated discovery layers
- public security research showing meaningful malicious and vulnerable-skill rates

## Target users

### 1. Cautious installer

Power user or developer who wants to install a public skill but does not want to
read every file by hand.

Primary job:

- "Tell me if I should install this right now."

### 2. Skill operator

Maintains a workspace or team environment with many skills and wants a repeatable
policy gate.

Primary jobs:

- "Block bad skills before they reach my workspace."
- "Show me which installed skills need review after updates."

### 3. Publisher

Wants a public trust signal and a pre-publish gate.

Primary jobs:

- "Catch trust issues before publishing."
- "Show users a concrete audit result, not just marketing claims."

### 4. Curator / index maintainer

Runs a discovery surface and wants machine-readable risk, provenance, and proof
signals.

Primary job:

- "Rank skills by usefulness and trust, not just downloads."

## What the product is not

- Not a malware-proof guarantee.
- Not a generic security scanner for arbitrary repos.
- Not a broad package manager replacement.
- Not a static awesome list.
- Not a cloud-only scanner that uploads users' local skill stacks by default.

## Primary user promise

Before install, the user gets:

1. a resolved source of truth
2. a provenance summary
3. a behavioral risk summary
4. a `PASS`, `REVIEW`, or `BLOCK` install decision
5. a durable receipt for what was approved and installed

## Product surfaces

### A. CLI

This is the flagship surface.

Commands:

```bash
clawhub-install-gate inspect <slug|repo|path>
clawhub-install-gate install <slug>
clawhub-install-gate diff <slug> --from <version> --to <version>
clawhub-install-gate verify <installed-skill-path>
clawhub-install-gate doctor
clawhub-install-gate index sync
```

### B. Codex / OpenClaw skill

Wraps the CLI for assistant-driven workflows.

This should evolve from the existing local skill:

- [clawhub-skills-security.md](clawhub-skills-security.md)
- [SKILL.md](../../skills/clawhub-skills-security/SKILL.md)
- [audit_clawhub_skill.py](../../skills/clawhub-skills-security/scripts/audit_clawhub_skill.py)

### C. Public trust index

Read-only website and JSON snapshots:

- top safe skills
- top reviewed skills
- recently changed risk
- suspicious but popular skills
- verified publishers

### D. Publisher CI / GitHub Action

Lets publishers run the same policy locally and in CI.

Outputs:

- machine-readable audit report
- badge or attestable status
- release receipt

## Core workflow

### 1. Resolve

Input may be:

- ClawHub slug
- GitHub repo URL
- local skill path
- unpacked archive

The gate resolves:

- registry metadata
- publisher identity
- source repo URL
- version / tag / commit if available
- release asset or package artifact
- local files that would actually be installed

### 2. Collect evidence

The gate records:

- source URL
- retrieved timestamp
- version
- content hash / fingerprint
- file manifest
- executable files
- scripts
- binaries / archives
- outbound network indicators
- credential access indicators
- declared vs observed capabilities

### 3. Score

The gate computes:

- provenance score
- behavior risk score
- transparency score
- operability score
- update risk score

### 4. Decide

Decision classes:

- `PASS`
- `REVIEW`
- `BLOCK`

### 5. Install or stop

- `PASS`: install allowed
- `REVIEW`: default deny, allow only with explicit override
- `BLOCK`: no install

### 6. Record receipt

Receipt fields:

- artifact id
- source and version
- hashes
- decision
- findings
- user override flag if any
- installed path
- install time

## Threat model

### Direct malicious behavior

- secret exfiltration
- credential harvesting
- destructive shell commands
- hidden payload execution
- undeclared remote upload
- tunnel / remote browser abuse

### Supply-chain ambiguity

- registry page does not match source repo
- tag does not match installed files
- binaries with unclear origin
- copied scripts with no source provenance
- update channel changes behavior silently

### Trust erosion / policy abuse

- absolute safety claims
- hidden instruction override attempts
- behavior exceeds declared metadata
- broad capability claims with weak evidence

### Operational failure

- installs but does not load
- watcher/indexing failures
- missing dependencies
- brittle platform assumptions
- incomplete compatibility story

## Decision model

### PASS

Conditions:

- provenance is clear enough to explain the artifact
- no blocking behavioral indicators
- warnings are either absent or narrowly justified
- install/load smoke path is plausible

### REVIEW

Typical triggers:

- remote network behavior that may be legitimate but is underexplained
- weak provenance
- large opaque assets
- unpinned dependencies
- browser profile / cookie access
- background update behavior
- upload or telemetry path requiring user judgment

### BLOCK

Typical triggers:

- prompt override attempts
- secret-like values
- credential theft indicators
- destructive shell patterns
- remote download piped to shell
- undeclared executable payload
- clear mismatch between listing and artifact

## Scoring model

This should not be a vanity trust score. It should be a decomposed score with
visible penalties.

### Provenance score: 0-30

Features:

- public source repo linked: +5
- immutable tag or commit resolved: +5
- artifact hash recorded: +5
- publisher identity consistent across registry and repo: +5
- license present: +3
- release notes or changelog present: +3
- source / artifact mismatch: -10
- opaque binary with no provenance: -10

### Behavior risk score: 0-40

Start at 40 and subtract penalties:

- secret exfiltration indicators: -40
- credential harvesting indicators: -35
- destructive shell: -40
- network client present: -5
- subprocess execution: -5
- dynamic code execution: -10
- package installs at runtime: -8
- browser profile/cookie access: -10
- remote upload / telemetry: -8
- silent auto-update behavior: -8

### Transparency score: 0-15

Features:

- clear README and capability description: +4
- permission/risk manifest present: +4
- docs match observed behavior: +4
- smoke-test/example present: +3
- docs overclaim or conceal behavior: -8

### Operability score: 0-15

Features:

- install/load smoke-test passes or is well specified: +5
- dependencies declared clearly: +4
- compatibility notes present: +3
- update path understandable: +3
- install known broken or watcher/indexing mismatch: -8

### Decision thresholds

This is the initial policy, not the final one:

- `BLOCK` if any blocking finding exists
- else `REVIEW` if:
  - total score < 65
  - provenance score < 15
  - behavior risk score < 20
  - any high-risk warning class is present
- else `PASS`

## Evidence model

The audit output should always show:

- what was inspected
- what was inferred
- what is unknown

Output schema:

```json
{
  "artifact_id": "publisher/skill@version",
  "source": {
    "clawhub_slug": "skill-scan",
    "repo_url": "https://github.com/...",
    "version": "1.2.3",
    "resolved_ref": "commit-or-tag",
    "artifact_sha256": "..."
  },
  "decision": "REVIEW",
  "scores": {
    "provenance": 18,
    "behavior_risk": 22,
    "transparency": 9,
    "operability": 8,
    "total": 57
  },
  "findings": [],
  "unknowns": [],
  "receipt": {
    "generated_at": "2026-04-24T00:00:00Z"
  }
}
```

## MVP

### Must-have

1. `inspect <slug|path|repo>`
2. local-first static audit
3. provenance summary
4. `PASS / REVIEW / BLOCK`
5. install receipt generation
6. install wrapper that defaults to deny on `REVIEW` and `BLOCK`

### Nice-to-have

1. version diff
2. public trust index
3. publisher CI badge
4. local installed-skill verification

### Explicitly out of MVP

1. full sandboxed runtime execution
2. dynamic malware analysis
3. enterprise policy engine
4. broad browser extension
5. upload-your-skill-stack cloud scanner

## Install flow

### User flow

```text
user asks to install a skill
-> gate resolves slug to exact artifact
-> gate downloads into a temp directory
-> gate audits provenance and real files
-> gate prints trust report
-> PASS: install
-> REVIEW: require explicit confirmation
-> BLOCK: stop
-> post-install load verification runs
-> receipt written locally
```

### Example

```bash
clawhub-install-gate inspect skillscan
clawhub-install-gate install skillscan
```

Example output:

```text
Trusted ClawHub Install Gate
artifact=tokauthai/skillscan@1.4.2
decision=REVIEW
why=remote upload path, persistent client identifier, weak provenance on bundled payload
action=not installed by default
```

## Architecture

### Core modules

- `resolver`
  - resolve slug, repo, local path, version
- `fetcher`
  - fetch metadata and artifacts
- `provenance`
  - map publisher, repo, refs, hashes
- `scanner`
  - static file scanner, evolves existing audit script
- `policy`
  - scoring and decision rules
- `installer`
  - safe install wrapper
- `receipts`
  - local audit/install receipts
- `index`
  - public snapshots for curated discovery

### Recommended implementation language

Python, standard-library-first for the scanner path.

Reason:

- matches the existing scanner
- easy distribution
- transparent enough for users to read

### Storage

Local:

- audit receipts
- resolved artifacts
- hashes
- user overrides

Public snapshots:

- signed JSON if publishing an index

## Relationship to the current repo

### Short answer

Split into a dedicated flagship repo now.

### Why

This repo already contains the seed assets, but it is not a clean flagship home.

Current repo is multiproduct:

- `antirot`
- `codex-harness`
- `github-stars-optimizer`
- `clawhub-skills-security`

That is fine for seed discovery, but weak for long-term positioning.

### Final repo decision

Create the flagship repo now:

- `trusted-clawhub-install-gate`

Keep in this repo only:

- the existing bridge skill
- migration docs
- references to the new flagship repo

## Open-source structure

### Separate flagship repo structure

```text
trusted-clawhub-install-gate/
  README.md
  docs/
  src/clawhub_install_gate/
    resolver.py
    fetcher.py
    provenance.py
    scanner.py
    policy.py
    installer.py
    receipts.py
    index.py
  skill/
    trusted-clawhub-install-gate/
  corpus/
  rules/
  examples/
  fixtures/
  tests/
  .github/workflows/
```

### Public vs private

Public:

- scanner and rules
- score model
- receipts schema
- example findings
- public trust snapshots
- publisher CI action

Private:

- any internal allowlists or incident-response notes not safe to publish
- unpublished skill samples containing sensitive details

## Distribution plan

### Primary: GitHub

Why:

- this is where trust tooling earns stars
- publishers and operators evaluate source transparency here

What to ship:

- clear README
- examples of PASS / REVIEW / BLOCK
- public fixture corpus
- comparison to manual install flow

### Secondary: ClawHub

Ship a skill wrapper for the gate.

Why:

- distribution to the exact audience with the exact pain

### Third: ecosystem indexes

Targets:

- awesome-openclaw-skills
- third-party trackers and directories

Why:

- they already aggregate trust-conscious users

## MVP launch assets

1. README GIF showing `inspect -> review -> block/pass`
2. sample reports for:
   - clean skill
   - suspicious but popular skill
   - clearly blocked artifact
3. public fixture corpus
4. comparison table:
   - raw ClawHub install
   - install with gate
5. explanation of limits:
   - static review is not a guarantee

## Success metrics

### Product metrics

- number of audited skills
- pass/review/block distribution
- number of install receipts generated
- number of publisher CI runs
- number of version diffs viewed

### Trust metrics

- fraction of artifacts with verified source mapping
- number of suspicious artifacts clarified or blocked
- false-positive appeal rate

### OSS metrics

- GitHub stars
- ecosystem references
- publishers adding CI badge

## 24-hour plan

1. create the new repo
2. port the existing scanner into `src/clawhub_install_gate/`
3. wrap scanner output in a stable report schema
4. add provenance resolution for local path + repo URL + slug
5. create three public example audits
6. draft README skeleton and migration note from this repo

## 7-day plan

1. `inspect` command working end to end
2. `install` wrapper with deny-by-default on `REVIEW`
3. post-install load verification
4. receipts written locally
5. first fixture corpus
6. public docs on score model and limits

## 30-day plan

1. publish bridge skill on ClawHub
2. add diff mode for updates
3. publish first trust index snapshot
4. add GitHub Action for publishers
5. cut `v0.1.0` from the dedicated repo

## Brutal product test

This product is worth shipping only if it can answer these clearly:

1. What exact artifact will run?
2. Why is this safe enough or unsafe enough?
3. What changed since the last version?
4. What should the user do next?

If it cannot answer those four better than "read the repo yourself", it is not
good enough.

## Final recommendation

Ship this first as a trust gate, not as a discovery site.

Build order:

1. pre-install gate
2. provenance and receipts
3. install wrapper
4. post-install load verification
5. version diff
6. public trust index

That sequence matches the strongest real user pain and gives the product a
clearer reason to exist than a trends dashboard.
