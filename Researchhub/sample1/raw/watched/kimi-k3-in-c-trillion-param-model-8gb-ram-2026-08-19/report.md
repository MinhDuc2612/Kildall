---
title: kimi-k3-in-c — 2.78T model on 8GB RAM
source_url: https://www.instagram.com/reel/Dbz8HtFtXq7/
watched: 2026-08-19
intent: research about hardware-usage minimization
hero_frames:
  - hero-readme-stats.jpg
  - hero-675x-chart.jpg
  - hero-verified-tests.jpg
---

## TL;DR
- kimi-k3-in-c (FareedKhan-dev, Apache-2.0) is a 176KB pure-C99 inference engine that runs Moonshot AI's 2.78T-parameter Kimi K3 on one CPU with 8.24GB peak RAM measured — no GPU, no BLAS, no framework.
- The trick: Kimi K3 only activates 16 of 896 experts per token, so ~93% of the 1.56TB checkpoint never needs to be resident — it streams from NVMe in packed 4-bit form on demand instead.
- Output is byte-identical at every memory budget from 8GB to 224GB+ — more RAM only buys speed (fewer disk round-trips), never a different answer.
- Real cost: ~26-33s/token at the 8GB floor, ~1.7TB fast NVMe storage required. Proof-of-concept, not a production serving path.

## Key moments
- 0:00–0:05 — Hook: someone ran the biggest AI model in the world on a laptop with 8GB RAM.
- 0:05–0:17 — Developer (Fareed Khan) rewrote the entire inference engine in pure C, no GPU, no framework; whole engine is 176KB.
- 0:17–0:24 — Runs the 1.56TB model on one CPU by streaming experts straight off SSD in packed 4-bit form.
- 0:24–0:37 — Output is byte-for-byte identical to a 224GB-RAM server version — same answer, same tokens, ~700% less hardware (repo's own chart: "675x smaller, and it answers with the same words").
- 0:37–0:44 — ~2,600 GitHub stars, fully free and open source.
- On-screen (frames): full hardware/speed table (8GB→32GB→64GB→128GB+, time-per-token dropping as more sits in memory), setup steps (clone → k3-doctor.sh → make), and a weights-free verification suite ending "ALL WEIGHTLESS TESTS PASSED."

## Hook microscope
Opens on an audacious, testable claim ("biggest AI model in the world... laptop with only 8GB RAM") stated flatly with no hedge, immediately followed by concrete technical specifics (pure C, no GPU, 176KB) that function as credibility proof rather than hype — pattern is contrarian-claim-then-immediate-evidence, which is what earns it real engineering interest rather than reading as a stunt.

## Editorial profile
Talking-head over dark studio lighting, cut against on-screen GitHub README screen-recording synced tightly to narration — numeric proof points (parameter count, RAM figures, star count) shown as literal repo text rather than graphics, which reads as "look, it's real, here's the receipts" rather than a marketing card.

## Quotable moments
- "This developer... rewrote the entire inference engine in pure C with no GPU and no framework to run Kimi K3 on a laptop."
- "The whole engine is 176 KB. This is smaller than the most images on your phone."
- "You will get same answer and same tokens with 700% less hardware."

## Entities mentioned
- [[kimi-k3]]
- [[moonshot-ai]]
- [[fareedkhan-dev]]

## Concepts surfaced
- **Mixture-of-Experts sparsity** — 16 of 896 experts active per token means ~93% of weights are irrelevant to any single token.
- **Expert streaming from SSD** — never load the full model; fetch only the selected experts, in their packed 4-bit form, on demand.
- **Memory-as-a-dial** — same deterministic output at any RAM budget; more memory only reduces disk round-trips, never changes the answer.
- **Quantization-aware training** — K3 was trained to tolerate MXFP4 weights from the SFT stage onward, not just post-hoc quantized.

## Full research
See `Research docs/kimi k3 hw mini.md` in this vault for the full write-up: Kimi K3's actual architecture (Kimi Delta Attention, Attention Residuals, Stable LatentMoE), a detailed breakdown of the four hardware-minimization techniques, and how this fits the broader MoE-offloading research lineage (HOBBIT, DynaExq, and an energy-cost caveat from the literature).

## Transcript
Auto-transcribed locally via whisper.cpp (base.en). Opens: "Someone just made the biggest AI model in the world run on a laptop with only 8GB of RAM..." — full transcript stored at `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch5/transcript.txt`; substance is fully captured in Key Moments and the linked Research doc above.
