# llm7ccapi — LLM7.io

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** one of only three providers here offering **keyless anonymous access** — and among the
least documented.

## Facts

| Field | Value | Tier |
|---|---|---|
| Token page | [token.llm7.io](https://token.llm7.io) 🇬🇧 | ✓P |
| Access | ✅ **Keyless anonymous access offered** | ✓W |
| Class | Inference provider | ✓P |
| Base URL | **not stated in the entry** | — |
| Rate limits | **not stated in the entry** | — |
| Models | **not stated in the entry** | — |

## The keyless group

Three providers in this set offer access **with no API key at all**: `✓W`

| Provider | Notes |
|---|---|
| **LLM7.io** | keyless anonymous |
| **OVHcloud AI Endpoints** | keyless anonymous (`ovhcloudccapi.md`) |
| **Kilo Code** | no key and no card (`kilocodeccapi.md`) |

**Keyless means no signup, no identity, no email** — the lowest possible friction, and the natural
first thing to try when evaluating whether a free tier is worth a signup elsewhere.

It also means **no per-user quota attribution**, which in practice implies aggressive shared rate
limiting and no stability guarantee. Anonymous endpoints are the first thing providers throttle when
abused.

## ⚠️ Honest gap

`mnfst` lists LLM7.io with a country flag and a token URL and **little else** — no base URL, no
limits, no model list. The workflow returned no LLM7-specific source. **Nothing is invented here.**

The presence of a `token.llm7.io` page alongside a keyless claim suggests **both** modes exist —
anonymous with tight limits, token-bearing with looser ones — but **that is inference, not
established fact.**

## Verdict

**Try it first because it costs nothing to try** — no key, no signup. Do not plan around it: an
anonymous endpoint with undocumented limits is the least durable thing in this set. Verify directly
at [token.llm7.io](https://token.llm7.io) before considering it for anything real.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — listing and token URL
2. Workflow run `wf_5cf67b3e-3b8` — the keyless-anonymous grouping

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **LLM7.io**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.
