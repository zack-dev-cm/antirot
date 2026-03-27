# Publish Checklist

Target repo:

- owner: `zack-dev-cm`
- name: `antirot`
- visibility: `public`

Recommended GitHub metadata:

- description: `Harness engineering for research agents. Catch unsupported claims, citation drift, and paper slop before publishing.`
- homepage: leave empty for `v0.1.0` unless you add a dedicated landing page
- topics:
  - `ai-agents`
  - `llm`
  - `research`
  - `scientific-writing`
  - `hallucination-detection`
  - `markdown`
  - `citations`
  - `harness-engineering`

## Before publish

1. Record a 20-40 second terminal demo.
2. Export a PNG social preview image from `assets/antirot-social-card.svg`.
3. Set the GitHub social preview image in repository settings.
4. Confirm the README top section still reflects actual CLI output.
5. Tag the first release as `v0.1.0`.

## Current remote state

As of **March 27, 2026**, `https://github.com/zack-dev-cm/antirot` exists and is **empty**.

That means the remaining publish steps are:

1. refresh the local `gh` token to include `workflow` scope
2. push `main`
3. create `v0.1.0`
4. upload the social preview image in repo settings

## Push commands

If you need to create the repo from scratch in a fresh environment:

```bash
git branch -M main
git add .
git commit -m "Initial public release: AntiRot v0.1.0"
gh repo create zack-dev-cm/antirot \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description "Harness engineering for research agents. Catch unsupported claims, citation drift, and paper slop before publishing."
```

Then set topics:

```bash
gh repo edit zack-dev-cm/antirot \
  --add-topic ai-agents \
  --add-topic llm \
  --add-topic research \
  --add-topic scientific-writing \
  --add-topic hallucination-detection \
  --add-topic markdown \
  --add-topic citations \
  --add-topic harness-engineering
```

Create the first release:

```bash
gh release create v0.1.0 \
  --repo zack-dev-cm/antirot \
  --title "AntiRot v0.1.0" \
  --notes-file docs/releases/v0.1.0.md
```

## GitHub auth gotcha

If your initial push fails with an error about updating `.github/workflows/ci.yml`, your GitHub CLI token likely does not have the `workflow` scope.

Refresh auth, then retry the push:

```bash
gh auth refresh -h github.com -s workflow
git push -u origin main
gh release create v0.1.0 \
  --repo zack-dev-cm/antirot \
  --title "AntiRot v0.1.0" \
  --notes-file docs/releases/v0.1.0.md
```

If the repo already exists and is empty, you only need the three commands above.

## After publish

1. Pin the repo on your GitHub profile.
2. Post the launch copy from `docs/social-posts.md`.
3. Submit to Hacker News or a relevant agent/dev tooling community.
4. Open 3 starter issues:
   - section-aware policies
   - richer citation parsing
   - GitHub annotation polish
