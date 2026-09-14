# nvidianimccapi — NVIDIA NIM

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** **100+ models** free with a developer-program signup — and an explicit, no-opt-out
policy that your prompts are logged and used to improve NVIDIA products.

## Facts

| Field | Value | Tier |
|---|---|---|
| Explore / key page | [build.nvidia.com/explore/discover](https://build.nvidia.com/explore/discover) 🇺🇸 | ✓P |
| Base URL | `https://integrate.api.nvidia.com/v1` | ✓P |
| Requirement | **NVIDIA Developer Program membership** (free) | ✓P |
| Models | **100+** | ✓P |
| Limits | **Rate-limited per model** — no single published number | ✓P |
| Class | Inference provider | ✓P |

## ⚠️ Data policy — explicit, and there is no opt-out

> *"Your use is logged for security purposes and **to improve NVIDIA products and services**."* `✓W`

And via `mnfst`, on the endpoints Kilo Code routes to NVIDIA:
> *"**Trial use only** — do not submit personal or confidential data."* `✓W`

**Two things follow.** First, "trial use only" is a **commercial-use restriction**, which puts NVIDIA
alongside Cohere as the second provider here with one. Second, this is a *transitive* risk: if you
use **Kilo Code**'s Auto Free router, you may be routed to NVIDIA and inherit this policy **without
knowing it** (see `kilocodeccapi.md`).

## Rate limits

**Per-model, and not published as a single figure.** `✓P` No aggregate RPM/RPD/TPD exists to quote,
so none is quoted. Any catalogue giving you one number for "NVIDIA NIM free tier" has invented it.

## Verdict

**Enormous model variety for a free signup**, and NVIDIA is not going to disappear. But the
combination of **explicit training-use logging with no opt-out** plus **trial-use-only** terms makes
it unsuitable for anything proprietary or commercial. Use it to evaluate models, not to run a product
— and be aware you may hit it indirectly through Kilo Code.


## ⚡ ANSWER FIRST — NVIDIA NIM

| | |
|---|---|
| **Free tier** | ✅ free with developer signup |
| **Limits** | per-model, **no published figure** |
| **Data policy** | ❌ **logs and trains, NO opt-out** |

**Verdict:** **82 models** (not the "100+" often claimed). ❌ **Trial use only** — a commercial restriction. You may also hit it *indirectly* through Kilo Code without knowing.

---

---

## ✅ LIVE VERIFICATION — 2026-09-01 · **82 models, not "100+"**

Probed `https://integrate.api.nvidia.com/v1/models` unauthenticated (`200`, open catalogue).

**Live count: 82.** The repo (and this file's earlier draft) said **"100+"** — that is an
**overstatement of roughly 20%**. Sample ids confirm it is a real multi-vendor catalogue
(e.g. `01-ai/yi-large`).

Endpoint and base URL confirmed working exactly as documented. The **data policy and trial-use
restriction could not be verified without a key** and still rest on the workflow-recovered quotes above.

**Correction recorded rather than quietly fixed:** any catalogue repeating "NVIDIA NIM: 100+ free
models" is repeating a figure the live endpoint does not support.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — base URL, 100+ models, per-model limiting, trial-use flag
2. Workflow run `wf_5cf67b3e-3b8` — the NVIDIA logging policy quote, surfaced via Kilo Code's docs

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **NVIDIA NIM**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Live-verified 2026-09-01 against the provider's own `/v1/models` endpoint; see the **LIVE VERIFICATION** section above and `ccapi-verification.md`.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
