# GitHub Star Audit

Audit date: **March 27, 2026**

## Profile diagnosis

Your public GitHub profile currently exposes a much smaller surface than your local machine suggests.

Public profile signals pulled from GitHub on March 27, 2026:

- public repos: **22**
- followers: **5**
- following: **4**
- profile `name`: empty
- profile `bio`: empty
- profile `blog`: empty

That means the main problem is not "the algorithm hates you." The main problem is distribution and packaging.

## Why your GitHub is not getting stars

### 1. Most of your interesting work is not public

The local workspace contains many repos, but the public profile does not expose most of the most interesting ones. If the project is not public, it cannot collect ambient discovery from search, recommendations, topic pages, or shares.

### 2. The public profile has weak identity

An empty name, empty bio, and empty blog/homepage field make the profile feel inactive even when you are building. For open-source discovery, identity is packaging.

### 3. The best public repo is still too new for passive stars

`zack-dev-cm/agentic-cv-repro-lab-skill` is public, but as of March 27, 2026 it was created on **March 14, 2026** and still had:

- stars: **0**
- forks: **0**
- watchers: **0**

That is not enough time or distribution to conclude the idea failed. It is enough to conclude the launch did not create a discovery loop.

### 4. Several public repos are old, generic, or forks

A meaningful share of the public surface is made of older repos, narrow utilities, or forks. Forks rarely attract stars unless they carry a very clear differentiated story.

### 5. Your repos skew toward operator-facing documentation

`agentic-cv-repro-lab-skill` is useful, but the README is optimized for people already inside the OpenClaw/Codex/operator workflow. That is good for users who already understand the stack and weak for drive-by visitors.

## Latest project audit

### `hh_proposal_agent`

Current state from the local README:

- positioned as an `hh.ru` counterpart to `upwork_proposal_agent`
- control-plane scaffold complete
- schemas complete
- OpenClaw browser-management and apply CLI complete
- official-surface review captured as of **March 26, 2026**

Why it will not get stars in its current state:

- it is not a public git repo in this workspace
- it is region/platform specific
- the value is operational, not curiosity-driven
- it likely needs live credentials and operator context to appreciate

Recommendation:

- Keep it productized if it makes money.
- Do not make this your flagship star project.
- If open-sourcing anything from it, extract a generic public slice such as safe browser approval gates, application packet schemas, or operator runbooks.

### `agentic-cv-repro-lab-skill`

Public repo facts on **March 27, 2026**:

- repo: `zack-dev-cm/agentic-cv-repro-lab-skill`
- created: **March 14, 2026**
- updated: **March 21, 2026**
- stars: **0**
- forks: **0**
- watchers: **0**
- homepage set to your portfolio page
- topics are actually good: `openclaw`, `computer-vision`, `reproducibility`, `kaggle`, `google-colab`, `llm-agents`, and related tags

Why it still has zero stars:

- title is descriptive but not curiosity-maximizing
- the repo assumes people already understand Codex skills and OpenClaw
- the hook is operator-grade, not "I need this right now"
- there is no visible viral artifact near the top like a short demo GIF, benchmark screenshot, or shocking before/after
- the first-run path is conceptually heavier than the hottest repos in the space

Recommendation:

- Add a 30-second GIF of the skill creating a reproducibility bundle.
- Move one killer example to the top of the README.
- Add a "Use this if..." section with plainer language.
- Publish a short X/Reddit/HN thread using one concrete failure mode the skill prevents.

## What to change at the profile level

1. Add a clear one-line bio anchored on agent systems and reproducible AI workflows.
2. Fill the website/blog field with your portfolio or one landing page.
3. Pin three public repos with distinct theses:
   - one flagship open-source tool with a broad hook
   - one visually impressive demo repo
   - one deeper technical repo with credibility
4. Stop letting low-signal old repos dominate the first impression.
5. Launch fewer repos, but launch them harder.

## What kind of repo is most likely to win for you

Your strongest unfair advantage is not commodity CRUD or a generic wrapper. It is rigorous agent workflows with reproducibility, browser automation, and operator gates.

The best public flagship is therefore:

- broad enough for many people to care
- sharp enough to explain in one sentence
- demonstrable in one screenshot or terminal run
- adjacent to the current agent wave
- grounded in your real systems experience

That is why `AntiRot` is a stronger flagship candidate than `hh_proposal_agent` or another broad "agent platform" repo.
