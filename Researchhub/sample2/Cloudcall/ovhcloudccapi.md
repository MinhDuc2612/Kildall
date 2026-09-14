# ovhcloudccapi — OVHcloud AI Endpoints

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** a European cloud provider offering **keyless anonymous access** to a model catalogue —
the EU-jurisdiction option in this set.

## Facts

| Field | Value | Tier |
|---|---|---|
| Catalogue | [ovhcloud.com/en/public-cloud/ai-endpoints/catalog](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/) 🇫🇷 | ✓P |
| Access | ✅ **Keyless anonymous access offered** | ✓W |
| Class | Inference provider | ✓P |
| Base URL | **not stated in the entry** | — |
| Rate limits | **not stated in the entry** | — |
| Free-tier terms | **not stated in the entry** | — |

## Why the jurisdiction is the point

OVHcloud is French. Combined with **Mistral** (also French), it makes **two EU-based options** in a
set otherwise split between US and Chinese providers.

That matters concretely for the data question running through this whole `ccapi` set:
- **Google** trains on free-tier prompts **except** for EEA / Switzerland / UK users `✓W`
- **Mistral** trains on free-mode prompts **with an opt-out** `✓W`
- **NVIDIA** logs and uses prompts to improve products, **no opt-out** `✓W`
- **Kilo Code** routes to providers that log, **no opt-out** `✓W`

**An EU provider under GDPR is a structurally different proposition** from a US or Chinese one,
regardless of what any individual policy page says today. OVHcloud's specific free-tier data policy
**was not established** in this research.

## ⚠️ Honest gap

`mnfst` lists OVHcloud with a catalogue link and no free-tier terms, no limits, no base URL. The
workflow's fetch of `docs.ovhcloud.com` **failed on the session limit.** So OVHcloud is one of the
least-resolved entries here, and **nothing is filled in from memory.**

**To complete this file:** read the AI Endpoints catalogue and pricing pages directly — the fetch that
failed is exactly the one that would answer it.

## Verdict

**The EU-jurisdiction pick, on principle rather than on evidence.** Keyless access makes it free to
evaluate. But with no limits, no base URL and no data policy established, it cannot be recommended on
its merits yet — only flagged as the option most likely to suit anyone who needs their prompts to stay
under European law.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — catalogue link and listing
2. Workflow run `wf_5cf67b3e-3b8` — keyless grouping; the `docs.ovhcloud.com` fetch failed on the session limit

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **OVHcloud AI Endpoints**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.
