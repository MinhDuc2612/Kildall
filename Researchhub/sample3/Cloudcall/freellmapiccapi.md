# freellmapiccapi — `tashfeenahmed/freellmapi`

**Repo:** [github.com/tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi)
**Built:** 2026-09-01 · Sample 2 · self-contained
**Part of the `ccapi` set** — see `mnfstccapi.md`, `publicapisccapi.md`, and the 18 per-provider files.

**One line:** **not a list — a working router.** A self-hosted, OpenAI-compatible `/v1` endpoint that
stacks 34 providers' free tiers into a claimed **7.4 billion tokens per month**, with failover,
encrypted keys and per-key quota tracking. Its own README says **do not use it in production**.

## ⚡ ANSWER FIRST — tashfeenahmed/freellmapi

| | |
|---|---|
| **Free tier** | **MIT**, 23,451 stars |
| **Limits** | claims 34 providers, 635 endpoints |

**Verdict:** ⚠️ **Its "7.4 billion tokens/month" headline is inflated ~8x** — it sums per-model budgets while many models share one pool. Real figure on one install: **294M, not 2.37B**. The router itself is real and useful.

---

---

## 1. Verified repository facts

Live GitHub API, 2026-09-01:

| Field | Value |
|---|---|
| Repo | `tashfeenahmed/freellmapi` |
| Licence | **MIT** |
| Stars / forks | **23,451 / 3,219** |
| Created | 2026-04-21 |
| Last push | **2026-09-01** — same day as this file |
| Archived | No |

**Headline claim, verbatim:** *"7.4 billion tokens per month. 34 free LLM providers. 635 free model
endpoints. One OpenAI-compatible endpoint."* Elsewhere: **"474 model families / 635 provider
endpoints."**

**Distribution:** Google Play app, macOS and Windows desktop builds, Docker image on `ghcr.io`,
Docker Compose self-host path. English and 简体中文.

---

## 2. What it actually is

The core argument, in the README's own words:

> *"Every serious AI lab now offers a free tier, a few million tokens a month, a few thousand
> requests a day. On its own each tier is a toy. Stacked together, they add up to roughly 7.4 billion
> tokens per month of working inference capacity."*

> *"The problem is that stacking them by hand is painful: thirty-four different SDKs, thirty-four
> different rate limits, thirty-four places a request can fail. FreeLLMAPI collapses that into one
> OpenAI-compatible endpoint."*

**Mechanically:**
- One local `/v1` endpoint; point any OpenAI client at it
- **Smart routing** — picks the best available model per request
- **Automatic failover** — moves to the next provider when one rate-limits
- **Per-key usage tracking** — keeps you under each free-tier cap
- **Encrypted key storage**
- Also accepts **any custom OpenAI-compatible endpoint**, so your own local server can join the pool

**This is the structural difference from the other two repos.** `mnfst` and `public-apis` tell you
what exists. This one *runs*.

---

## 3. Providers

The README's provider grid shows **12 logos**: Google, Groq, Cerebras, OpenCode Zen, Mistral,
OpenRouter, Cloudflare, Cohere, Z.ai (Zhipu), NVIDIA, HuggingFace, ModelScope.

> ⚠️ **The repo claims 34 providers but names only 12 here.** The other 22 are not enumerated in the
> README's provider section. Any claim about "all 34" in this file would be invented, so it is not
> made. **Overlap with `mnfst`:** 10 of the 12 shown appear in both. **Only in freellmapi:**
> **Cerebras** and **OpenCode Zen**.

**Compatible clients**, per the README: Claude Code, Codex CLI, Gemini CLI, Qwen Code, Aider, Cline,
Roo Code, Kilo Code, Continue, Cursor, Crush, Goose, OpenCode, Zed, JetBrains AI, DeepSeek Harness.
That list is the practical point — it is designed to sit behind a coding agent.

---

## 4. The business model, stated openly

The router **updates its own model catalog from a signed feed** rather than a `git pull`:

- **Free installs** get the **monthly snapshot** — a new model reaches you **30 days** after it joins the live feed
- **Premium** ($19/yr) gets it **the same day**

So the MIT-licensed code is genuinely free and complete, and **freshness is the paid product**. That
is an honest and unusual split — worth naming rather than treating the repo as purely non-commercial.

---

## 5. The caveats — quoted, because they are unusually candid

**Limitations, verbatim:**

> *"Stacking free tiers has real trade-offs: no frontier models, variable latency, no SLA — and the
> effective intelligence of the endpoint dips late in the day as top models hit their daily caps,
> then resets at UTC midnight."*

That last clause is a genuinely useful operational detail no marketing page would volunteer: **your
answer quality is a function of the time of day.**

**Disclaimer, verbatim:**

> *"This project is for personal experimentation and learning, not production. Free tiers exist so
> developers can prototype against them; they aren't a stable, supported inference substrate and
> shouldn't be treated as one. If you build something real on top of FreeLLMAPI, swap in a paid API
> before you ship. Your relationship with each upstream provider is governed by the terms you
> accepted when you created your account — those terms still apply when the traffic is proxied
> through this project, and you're responsible for complying with them."*

**On the terms-of-service question** — the sharpest risk in this whole category — the repo does not
dodge it. It states it reviewed **provider by provider in May 2026** how each provider's ToS views a
personal single-user proxy, and puts the result in `docs/architecture.md#terms-of-service-review`.

⚠️ **That ToS review was not read for this file.** It is the single most important document in the
repo for anyone actually deploying this, and it is the obvious next step.

---

## 6. Honest assessment

**Credible signals:** MIT, 23.4K stars, 3.2K forks, pushed the same day, CI badge, multi-platform
builds, i18n, an explicit limitations section, an explicit non-production disclaimer, and a
self-reported ToS review. Projects hiding something do not usually write their own disclaimer this
plainly.

**Unverified claims:** every headline number — **7.4B tokens/month**, **34 providers**, **635
endpoints**, **474 model families**. All are self-reported by the README. None was checked against
provider documentation here. The 7.4B figure in particular is a *sum of advertised caps*, which
assumes every provider's free tier is simultaneously available, honoured, and permissible to
aggregate — three assumptions the disclaimer itself partly undercuts.

**The unresolved legal question:** free tiers are offered for prototyping by an individual. Whether a
proxy that stacks 34 of them, even for one user, stays inside each provider's terms is exactly the
question the repo says it answered in May 2026 — and that answer was not read here. **Do not deploy
this commercially on the strength of this file.**


---

## 7. ⚠️ THE 7.4 BILLION TOKEN FIGURE IS INFLATED ~8× — added after the deep-research run

This section was added after the workflow's fetch stage returned it. **It is the most important
finding about this repo.**

A user of the router reported, with numbers:

> *"The 'Monthly token budget' bar on the Fallback page reads **2.37B tokens/month** on my install.
> The real pooled figure for the same account is **294M**, so it's **out by 8×**."*

**The cause is a double-counting bug.** The router **sums per-model budgets** without recognising that
**many models on one provider share a single free pool.** Worked examples from the same report:

| Provider | Reality | Counted as | Inflation |
|---|---|---|---|
| **Mistral** | 13 models sharing **one ~100M/month pool** | 1.30B | **13×** |
| **Cloudflare** | 21 models sharing **one ~45M pool** | 535M | **~12×** |

**And it is not two providers.** The same shared-pool over-count affects at least **11** of them
simultaneously — Ollama, Cerebras, Zhipu, Google, Groq, OpenRouter, Cohere, HuggingFace and Kilo are
all named. That establishes something bigger than a bug:

> **Free-tier quota is per-account-pool, not per-model. Across the whole ecosystem.**

**The headline 7.4B figure is computed the same way**, so it is not credible as stated. The realistic
number is roughly an order of magnitude lower.

**The most damning detail:** the *correct* pooled logic **already exists in the codebase**, in the
`/api/free-tier` endpoint, using `inferQuotaPoolKey`. The reporting path simply does not use it. So
the published number and the internally-correct number are derived differently **inside the same
project**.

**This is not a reason to dismiss the project** — the router, failover and per-key tracking are real,
and the repo is actively maintained with ~37 open issues. It is a reason to **ignore the headline
number entirely** and treat capacity as roughly 8× smaller than advertised.

### Corrections to section 4 above

- Premium is **$19/year or $49 one-time** — the one-time option was missing.
- The free build is **~303 models behind** the live feed, not merely "30 days behind" in the abstract.
- The 635 endpoints break down as **584 chat, 41 embeddings, 7 transcription, 3 video**.
- Open feature request **#1100** shows the catalogue does **not yet track live per-model availability**
  (`ready` / `needsKey` / `exhausted`) — so a model listed as available may already be exhausted.

## Sources

1. [`tashfeenahmed/freellmapi`](https://github.com/tashfeenahmed/freellmapi) — README fetched via GitHub API, and repo metadata, both 2026-09-01
2. [freellmapi.co](https://freellmapi.co/) — the catalogue and premium tier
3. `docs/architecture.md#terms-of-service-review` — **identified, not read**

## Change Log

- **2026-09-01** — Created from the repo's own README and live GitHub API metadata (**MIT**, 23,451
  stars, 3,219 forks, created 2026-04-21, **pushed the same day as this file**, not archived).
  Established the key structural point: **this is not a list like the other two repos — it is a
  running OpenAI-compatible router** with smart routing, automatic failover, encrypted key storage
  and per-key quota tracking, distributed via Play Store, macOS/Windows builds and a `ghcr.io` Docker
  image, and designed to sit behind coding agents (Claude Code, Codex CLI, Aider, Cline, Cursor, Zed
  and others named in the README).
  Recorded that the README's provider grid names only **12** providers against a claim of **34**, and
  **declined to invent the other 22**; noted that 10 of the 12 overlap with `mnfst/awesome-free-llm-apis`
  and that **Cerebras** and **OpenCode Zen** are unique to this repo.
  Documented the business model honestly: MIT code is complete and free, but the **model catalogue
  is a signed feed where free installs lag the live feed by 30 days** and a **$19/yr premium tier**
  gets same-day updates — freshness is the paid product.
  Quoted the repo's unusually candid limitations and disclaimer verbatim, including the operational
  detail that **"the effective intelligence of the endpoint dips late in the day as top models hit
  their daily caps, then resets at UTC midnight"**, and the explicit statement that upstream provider
  terms still apply to proxied traffic. Flagged that the repo's own **provider-by-provider ToS review
  (May 2026)** exists at `docs/architecture.md#terms-of-service-review` but **was not read** — the
  most important gap in this file. All headline figures (7.4B tokens/month, 34 providers, 635
  endpoints, 474 model families) are self-reported and unverified.

- **2026-09-01 (update — post-workflow)** — Added section 7 after the deep-research run
  (`wf_5cf67b3e-3b8`) returned it. **The repo's headline "7.4 billion tokens/month" is inflated by
  roughly 8×** through a shared-pool double-counting bug: the router sums per-model budgets while
  many models on a provider draw from one pool. A user measured **2.37B displayed against 294M
  real** on the same install; Mistral's 13 models share one ~100M pool but are counted as 1.30B
  (13×), and Cloudflare's 21 models share one ~45M pool counted as 535M (~12×). At least **11
  providers** are affected simultaneously, which establishes the broader rule that **free quota is
  per-account-pool, not per-model**. Most tellingly, the correct pooled logic **already exists in the
  same codebase** at the `/api/free-tier` endpoint via `inferQuotaPoolKey` — the reporting path just
  does not use it. Also corrected: premium is **$19/yr or $49 one-time** (one-time option was
  missing), the free build sits **~303 models behind** the live feed, and the 635 endpoints are
  **584 chat / 41 embeddings / 7 transcription / 3 video**. Noted open issue #1100: the catalogue
  does not yet track live per-model availability, so a listed model may already be exhausted.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
