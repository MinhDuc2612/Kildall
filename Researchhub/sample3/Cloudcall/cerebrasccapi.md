# cerebrasccapi — Cerebras

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers used in every `ccapi` provider file**
> `✓P` primary source (provider docs or the repo README itself, read this session) ·
> `✓W` recovered from the deep-research workflow's fetch stage, source-attributed but **the
> adversarial verification stage failed** (all 25 verifier panels died on a session limit) ·
> `⚠` inferred or single-source. **No figure below was tested against a live API key.**

**One line:** wafer-scale-fast, **not listed by `mnfst` at all**, and the documented case of a
provider **silently cutting its free model catalogue from about a dozen models to two.**

## ⚡ ANSWER FIRST — Cerebras

| | |
|---|---|
| **Free tier** | ✅ free |
| **Limits** | measured **~30,000 TPM** |

**Verdict:** ⚠️ **Silently cut its free models from ~12 to 2** with no announcement. **Never hardcode a Cerebras model name.** Not listed by the permanence-filtered catalogue at all.

---

## Facts

| Field | Value | Tier |
|---|---|---|
| Listed in `mnfst`? | ❌ **No** — Cerebras and OpenCode Zen are the two providers `freellmapi` carries that `mnfst` does not | ✓P |
| Listed in `freellmapi`? | ✅ Yes, in the 12-logo provider grid | ✓P |
| Measured TPM | **~30,000** | ✓W |
| Class | Inference provider | ✓P |

## ⚠️ The silent catalogue cut — the reason this file exists

> *"Catalog dropped from a dozen models to two without notice ... **Never hardcode a single Cerebras
> model name into anything you depend on**."* `✓W`

The two survivors: **`gpt-oss-120b`** and **`zai-glm-4.7`**. `✓W`

**No announcement, no deprecation window.** This is the sharpest operational warning in the whole
`ccapi` set: on a free tier, the model roster is not a contract. Anything that hardcodes a model name
breaks without warning and without an error message you can act on.

**Design implication:** use a router with failover (that is precisely `freellmapi`'s pitch — see
`freellmapiccapi.md`), or pin nothing and resolve model names at runtime.

## Rate limits

**Measured ~30,000 TPM** `✓W` — 5× Groq's measured ceiling, below Mistral's ~50,000. Since **TPM is
the binding constraint on free tiers**, Cerebras sits mid-pack on usable throughput despite being
among the fastest per-token.

## Verdict

**Fast, and unusually unstable.** Worth having in a multi-provider pool for speed; not worth
depending on alone. The fact that `mnfst` — whose inclusion criterion is *permanence* — **does not
list Cerebras** is itself a signal worth reading.

## Sources
1. Workflow run `wf_5cf67b3e-3b8` — the catalogue cut, surviving model names, ~30,000 TPM
2. [`tashfeenahmed/freellmapi`](https://github.com/tashfeenahmed/freellmapi) — provider grid listing
3. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — verified absence

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Cerebras**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
