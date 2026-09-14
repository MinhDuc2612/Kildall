# Mach 1 HW Mini

Source: Syzygy Research's own site (withsyzygy.com) and launch announcement (LinkedIn). Researched via /deep-research; workflow hit the session rate limit mid-verification and its synthesis step failed (recurring failure mode this session — see the methodology note below). Compiled 2026-08-23.

---

## 1. What Mach-1 is

**Mach-1** is Syzygy Research's combined model+engine package for running a 35B-parameter model **entirely on a Mac**, with no cloud, no API key, no internet dependency at inference time. It has two parts:

- **Mach-1 Additive (the model)** — a 35B-parameter Mixture-of-Experts model, based on Qwen 3.6 35B, compressed down to **1.7 bits per weight**, producing a **7GB file**. Confirmed directly from Syzygy's own launch announcement.
- **Mach Engine (the runtime)** — an inference engine built specifically for Apple Silicon that runs Mach-1 model packs via **"fused decode-in-GEMV Metal kernels"** and exposes an OpenAI-compatible API. Requires an Apple Silicon Mac and Python 3.12+.

Syzygy's own hardware guidance: a 35B-parameter model needs roughly **8GB of weights** under Mach-1's compression scheme and fits on a **16GB Mac** — a dramatically smaller footprint than the same parameter count would need at even aggressive GGUF quantization (compare: Qwen3.8-27B, a smaller 27.78B-param model, needs ~9-11GB at 2-bit GGUF — see `qwen 3.8 hw mini.md` in this folder).

## 2. How the hardware-usage minimization actually works

**A. Extreme sub-2-bit quantization (1.7 bits/weight).** This is well below the practical floor GGUF-style quantization usually stops at (2-bit is typically the lowest usable tier before quality collapses badly — see the Qwen3.8-27B doc). Getting useful quality out of 1.7 bits per weight isn't standard post-training GGUF quantization; it implies a purpose-built compression + likely some retraining/calibration process specific to Syzygy's own pipeline, though the exact training/calibration methodology wasn't independently confirmed before the research hit its rate limit (a specific claim of "under 15 GPU hours" training cost was checked and found unsupported by the sources — not repeated here).

**B. Fused decode-in-GEMV Metal kernels — avoiding a decompressed intermediate copy.** This is the same core idea as GGUF quantization's compute-time decode (see Qwen3.8-27B's technique B), but implemented as custom Metal (Apple's GPU compute API) kernels fused directly into the matrix-multiply step (GEMV = general matrix-vector multiply, the core operation in autoregressive decoding). The quantized weights are decoded *during* the multiply-accumulate operation itself, so the engine never materializes a full-precision (or even 4-bit) copy of the weights in memory at any point — confirmed directly from Syzygy's own docs. This is a tighter, more specialized version of what generic llama.cpp does for GGUF models; being purpose-built for one model family and one hardware target (Apple Silicon Metal) is likely what allows the much lower 1.7-bit floor to still produce usable output.

**C. MoE sparsity, stacked on top of the extreme quantization.** Mach-1 Additive is a Mixture-of-Experts model, not dense — meaning it inherits the same "only a fraction of parameters activate per token" property as Kimi K3 (see `kimi k3 hw mini.md`), compounding with the 1.7-bit compression rather than replacing it. This is architecturally different from Qwen3.8-27B (dense, quantization is the *only* lever) and closer in spirit to Kimi K3 (MoE, multiple techniques stack), just at a completely different scale (35B total vs Kimi K3's 2.8T) and with a much more aggressive quantization floor than either.

**Quality retention claim:** Syzygy's own site states Mach-1 Additive retains **96.3%** of its (unquantized/teacher) model's performance across 12 benchmarks. This figure appeared on the company's own site with moderate-confidence verification; a duplicate claim of the same number on a different company page was flagged during adversarial re-check, and the company's own LinkedIn launch post separately rounds this to "~95%" informally. Treat 96.3% as the company's own reported figure, not an independently reproduced benchmark result — no third-party re-run of these 12 benchmarks was found.

## 3. Reported but not independently verified (rate limit hit before these could be checked)

The research workflow's verification pass ran out of budget before checking these — they come from Syzygy's own marketing material and should be treated as claims, not confirmed facts, until checked against a primary technical source (a paper, or the model's actual weight format documentation):

- **"Addition-only" inference** — the "Additive" name and a company social-media post suggest the model performs inference without ever multiplying by a weight, replacing multiplication with addition (a technique in the same family as BitNet-style ternary-weight models, which use {-1, 0, +1} weights specifically so multiply-accumulate degenerates into add/subtract). This would be a meaningfully different mechanism from generic bit-depth quantization — but it's an inference from the naming and an unverified social post, not confirmed against the model architecture directly.
- Reported speed: up to ~120 tokens/second at the 7GB size; speculative decoding (with an optional add-on and a draft checkpoint) reportedly reaching ~163 tok/s vs ~117 tok/s for standard single-stream decoding.
- A separate "Mach-1 Small" variant, described as a compressed multimodal MoE model, also targeting 16GB+ Apple Silicon Macs.
- "Mach Agents" — a TypeScript agents SDK positioned specifically for small/local models rather than large hosted ones.

## 4. How this compares to the other two hardware-minimization docs in this folder

| | Kimi K3 (MoE, 2.8T) | Qwen3.8-27B (dense, 27.78B) | Mach-1 Additive (MoE, 35B) |
|---|---|---|---|
| Core lever | Expert streaming (skip 93%+ of weights per token) | GGUF quantization (2-8 bit) + RAM/VRAM offload | MoE sparsity **+** extreme sub-2-bit (1.7-bit) quantization, stacked |
| Where compute happens | CPU, streaming from NVMe SSD | GPU (Metal/CUDA) + CPU offload for spillover | Apple GPU (Metal), fused decode-in-GEMV kernels |
| Target hardware | Any x86-64 Linux CPU, no GPU needed | Any llama.cpp-supported platform (broad) | Apple Silicon Macs specifically — not portable to other hardware |
| Practical floor | ~8GB RAM, ~26-33s/token (proof-of-concept, not production speed) | ~9GB (2-bit), single-digit tok/s under memory pressure | ~8GB weights, reportedly up to ~120 tok/s (unverified) |
| Novelty | Architecture-level (never load sleeping experts) | Standard technique, well-established tooling (llama.cpp, GGUF) | Custom kernel + compression pipeline, single-vendor/single-platform |

The throughput gap is the most striking reported difference — if the ~120 tok/s figure holds up, Mach-1's purpose-built kernel + compression approach would be an order of magnitude faster than either of the other two techniques at a comparable memory footprint. That figure is unverified, though, so it shouldn't be treated as established until checked against an independent benchmark.

## 5. Sources

- Syzygy's Mach-1 launch announcement (LinkedIn, primary) — https://www.linkedin.com/posts/syzygyeng_today-were-introducing-mach-1-additive-activity-7490098448227008512-2WBp
- Mach Engine docs (primary) — https://withsyzygy.com/docs/mach
- Mach Engine installation docs (primary) — https://withsyzygy.com/docs/mach/installation
- Syzygy homepage (primary) — https://withsyzygy.com/
- Syzygy about page (primary) — https://withsyzygy.com/about
- Mach-1-Additive-35B model card (Hugging Face) — https://huggingface.co/SyzygyResearch/Mach-1-Additive-35B
- Third-party coverage — https://mindpattern.ai/s/2026-08-05-mach-1-additive-claims-a-35b-model-that-never-multiplies-by-a-weight
- Third-party listing — https://futuretools.io/tools/syzygy-o24rji
- Sibling docs for comparison — `kimi k3 hw mini.md`, `qwen 3.8 hw mini.md` (this folder)

## 6. Methodology note

The deep-research workflow hit the session's rate limit mid-verification and its synthesis step failed — the same recurring failure this session has hit on every multi-round research task today (see `cloud call.md` and `qwen 3.8 hw mini.md` for earlier instances). This file was hand-assembled from claims that survived 2-3 vote adversarial verification before the limit hit, cross-checked against Syzygy's own primary pages where possible. A meaningful fraction of Mach-1's more striking claims (addition-only inference, the 120 tok/s figure, speculative-decoding numbers) never finished verification — they're reported in Section 3 as unverified company claims, not folded into Sections 1-2 as established fact.

## 7. Change log

- 2026-08-23 — Created. /deep-research hit the session rate limit and failed synthesis; hand-assembled from verified claims, cross-checked against Syzygy's own primary docs/site.
