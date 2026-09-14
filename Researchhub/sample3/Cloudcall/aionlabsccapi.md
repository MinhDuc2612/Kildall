# aionlabsccapi — Aion Labs

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** a genuinely permanent free tier with the **clearest, most consistent published limits
of any provider here** — and a deliberate niche: roleplay and storytelling.

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [aionlabs.ai/app/api-keys](https://www.aionlabs.ai/app/api-keys/) 🇮🇱 | ✓P |
| Base URL | `https://api.aionlabs.ai/v1` | ✓P |
| Credit card | **Not required** | ✓P |
| Limits | **15 RPM, 20,000 tokens/day** — uniform across every model | ✓P |
| Class | Provider API (trains its own models) | ✓P |
| Speciality | **Roleplay and storytelling** | ✓P |

## Models — 4, all at the same limit

| Model | Context | Max out | Modality |
|---|---|---|---|
| `aion-labs/aion-3.0` | 128K | 32K | Text (reasoning) |
| `aion-labs/aion-3.0-mini` | 128K | 32K | Text (reasoning) |
| `aion-labs/aion-2.0` | 128K | 32K | Text (reasoning) |
| `aion-labs/aion-rp-llama-3.1-8b` | 32K | 32K | Text (roleplay) |

`✓P` — read from the repo README.

## Why the uniform limit is worth noticing

Every model gets **15 RPM / 20K TPD**. No per-model quota lottery (unlike Gemini, where some models
return quota-zero), no pooled-budget confusion (unlike Mistral's 13-models-one-pool). **You can
actually reason about this quota.**

A separate catalogue lists an `Aion 2.5` at the same 15 RPM / 20K TPD, cited without a provider link
`✓W` ⚠️ — that model does not appear in `mnfst`'s table, so treat the version name with caution.

## The real constraint: 20K tokens/day

That is **very small** — roughly 3–6 substantial reasoning exchanges at 128K-context scale, or a few
dozen short ones. Compare Mistral's ~100M/month pool. **This is a hobby quota, not a working one.**

## Verdict

**Take it for what it says it is.** A reasoning-capable free tier with honest, stable, uniform
limits, aimed at creative writing. The 20K/day ceiling rules out agentic or bulk work. Its value in a
multi-provider pool is as a predictable, never-surprising fallback.


## ⚡ ANSWER FIRST — Aion Labs

| | |
|---|---|
| **Free tier** | ✅ permanent free, no card |
| **Limits** | **15 RPM, 20K tokens/day** — uniform |

**Verdict:** **The most accurately documented provider here** — its 4 model ids match the live endpoint exactly. ⚠️ 20K tokens/day is a hobby quota.

---

---

## ✅ LIVE VERIFICATION — 2026-09-01 · **exact match, and a rival catalogue is wrong**

Probed `https://api.aionlabs.ai/v1/models` unauthenticated (`200`, open catalogue).

**Live count: 4. Exactly the four models documented above, with matching ids:**

`aion-labs/aion-2.0` ✅ · `aion-labs/aion-3.0` ✅ · `aion-labs/aion-3.0-mini` ✅ ·
`aion-labs/aion-rp-llama-3.1-8b` ✅

**This is the only provider in the whole `ccapi` set whose documented model list matches the live
endpoint exactly.** Combined with its uniform 15 RPM / 20K TPD, Aion Labs is the most accurately
documented provider here — small quota, but you can trust what you read.

### A rival catalogue's "Aion 2.5" does not exist

A competing free-LLM catalogue lists **`Aion 2.5` at 15 RPM / 20K TPD**. `✓W` **There is no
`aion-2.5` in the live endpoint.** The ⚠️ flag placed on that claim above was correct — it is a
fabricated or mis-transcribed model name, now disproven against the provider's own API.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — all of the above
2. Workflow run `wf_5cf67b3e-3b8` — the unsourced `Aion 2.5` listing in a rival catalogue

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Aion Labs**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Live-verified 2026-09-01 against the provider's own `/v1/models` endpoint; see the **LIVE VERIFICATION** section above and `ccapi-verification.md`.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
