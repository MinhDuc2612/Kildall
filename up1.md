# up1 — speed tricks: what this Mac can use, what the server can use

**Answer first.** Nothing here changes Kildall today.
- **This Mac (M4, 24 GB):** one thing to test in Phase R — **MTPLX**. Everything else in these notes either does not fit this Mac or is already done.
- **Reward server (MI210 64 GB + 512 GB RAM, Linux, ROCm):** five things to test when it arrives — **expert cache + CPU share**, **MTP**, **DFlash**, **full-GPU fit**, and **ROCm vs Vulkan**. One more is a maybe (**Avalon**).

All speed numbers below are **reported by others, not measured on our machines**. Each item is a test to run, not a setting to switch on.

Written 2026-11-09 from two videos (sources at the end) and checked against the tool pages.

---

## 1. This Mac — M4, 24 GB unified memory

### Test in Phase R: MTPLX

| | |
|---|---|
| What | Mac app + CLI that runs MLX models with **MTP** (multi-token prediction): the model guesses a few tokens ahead, then checks them in one pass. Same output, faster. |
| Licence | Apache-2.0 |
| Reported speed | **1.6× on a 16 GB M4 Mac mini** (maker). 1.9× on an M5 Max in video 1 (25.2 → 48.6 tok/s, Qwen3.8-27B Q4, coding). Prose task held the same gain. |
| Needs | A model with built-in MTP heads. On disk now: **Qwen3.6-35B-A3B** (29 tok/s on llama.cpp today). Also Qwen3.8-27B (not on disk; 5.4 tok/s measured here for Swift-1.5-Qwen3.8-27B). Gemma 4 support in MTPLX: unknown. |
| Where it fits | Phase R, step R3/R4 (runtime and Lane A re-pick). Measure only. |
| Risk | It is a **different server** from llama-server. Kildall's GBNF tool grammar, 3 pinned slots, router slot 0 and prompt cache are all built on llama-server. MTPLX is not a drop-in swap. |
| Earlier history | The MLX fork was closed on 2026-09-22 because of one routing over-match (r17), not speed — MLX was +24% faster with far fewer memory-pressure warnings. |

**How to test (when Phase R runs):** same prompts as the Lane A speed gate (code + prose), greedy, fixed seed. Report tok/s, accept rate, first-token time, peak memory, and pressure samples. Then the frozen routing, recall and tool suites. Adopt only if every standing gate holds.

### Not for this Mac

| Trick | Why not |
|---|---|
| **Splash** (incoai/splash, DFlash on Mac, 97 tok/s in video 1) | Needs **at least 36 GB** unified memory (48 GB recommended) and macOS 26.4+. This Mac has 24 GB. Revisit only on a Mac with 48 GB+. |
| **llama.cpp MTP** (`--spec-type draft-mtp`) | Others measured **no gain on an M4**. llama.cpp also turns MTP off with `--parallel > 1`, and Kildall runs 3 slots. |
| **Expert cache + CPU share** (video 2) | Built for a separate graphics card joined to RAM by a PCIe slot. This Mac has one shared memory pool, so there is nothing to fix. |
| **Lower thinking budget** | Already done: Lane A runs with thinking off; Lane C (Flash-Next) has thinking off by default. |

---

## 2. Reward server — MI210 64 GB HBM2e, EPYC 7543P, 512 GB DDR4 (8 channels), Linux + ROCm

The server has the exact shape these GPU tricks were built for: a 64 GB card, a large RAM pool, and a PCIe link between them. The Linux + ROCm port must exist first (plan: cross-platform slice), then run **pre-purchase check B** (ROCm gfx90a, test report, 600 s cooling, 8-channel BIOS) before any of these.

### 2.1 Expert cache + CPU share (llama.cpp, merged 2026-11-07)

| | |
|---|---|
| For | MoE models **bigger than 64 GB**, where experts live in system RAM (`--cpu-moe` / `--n-cpu-moe`). Example: Qwen3.8-Flash-Next 4-bit (~100 GB), GLM-5.x class. |
| How it works | The most-used experts are cached in spare VRAM. On a cache miss, the CPU computes that expert from RAM (the "CPU share") instead of waiting to upload it over PCIe. Same maths, same output. |
| Reported | 1.4×–2.4× on 8–32 GB cards. 3090 on Flash-Next: 19.5 → ~32 tok/s. AMD RX 6700 on ROCm (PCIe 3): 8 → 16 tok/s. |
| Use the tuner | It starts the server 6 times (2 cache sizes × 3 shares), measures PCIe upload and RAM read speed, and prints one recommended line. Takes a few minutes. |
| Traps | **Cache on with CPU share 0, cache small next to the model = slower than no cache** (2080 Ti: 42 → 23.5 tok/s). Load mode changes the answer (mmap vs locked/direct-IO). Longer context = smaller cache. The tuner does not count a vision projector's memory — set a lower max cache if it runs out. On a fast PCIe 5 card it made decode ~15% slower; the MI210 is PCIe 4, so measure. |
| Not for | Models that fit fully on the 64 GB card — run those fully on the GPU instead. |

### 2.2 MTP on the GPU (llama.cpp)

| | |
|---|---|
| Reported | 1.6× on 3090/4090, 2× on 5090, **2.5× on AMD 7900 XTX** (Qwen3.8-27B, video 1). |
| Setting | 2 draft tokens is the sweet spot (3090: +60% at 2, +32% at 5). |
| Needs | A model with MTP heads (Qwen 3.5/3.6/3.8), or Gemma 4's own MTP drafter (`unsloth/gemma-4-26B-A4B-it-GGUF`, `MTP/mtp-gemma-4-26B-A4B-it-Q8_0.gguf`, 0.46 GB). |
| Catch | llama.cpp turns MTP off with `--parallel > 1`. Measure 1 slot + MTP against N slots without it, on Kildall's real workload (interactive p99, not only tok/s). Gain is smaller on prose than on code (1.4× → 1.2× in video 1). |

### 2.3 DFlash on the GPU (llama.cpp)

| | |
|---|---|
| What | A separate small drafter (~1 GB) that writes a block of up to 16 tokens at once; the big model checks the block in one pass. |
| Reported | 1.5× on a 3090, **2× on AMD Strix Halo**. On MoE the gain is smaller (maker: 2.2× MoE vs 3× dense). |
| Needs | A drafter made for that exact model (example: `incoai/Qwen3.8-27B-DFlash2-GGUF`). No Gemma 4 DFlash drafter was published as of the 2026-11-01 check. |
| Warning | Never pair a random small model as the drafter — a 0.8B drafter made a 3090 **30% slower**. |

### 2.4 Fit the whole model on the GPU when it fits

A model that spills from VRAM into RAM runs much slower (3090 example: 140 → 89 tok/s). With 64 GB of VRAM, Lane A-size models (Gemma 4 26B-A4B, Qwen3.6-35B-A3B at 4-bit) fit fully — run them with all layers on the GPU and keep 2.1 for the bigger MoE models only.

### 2.5 Backend: ROCm (HIP) vs Vulkan

On NVIDIA, CUDA beat Vulkan by 35–90% on the same task. The MI210 is AMD, so the matching question is **ROCm/HIP vs Vulkan** — measure both on the same model and prompts. Known trap from video 2: an AMD Vulkan build gave garbage output until a fully clean rebuild.

### 2.6 Maybe: Avalon

`freriadoc/Avalon` (MIT, llama.cpp fork) targets Qwen3.8-Flash-Next on Linux **ROCm RDNA3** or CUDA. It is tuned for gfx1100; the MI210 is **gfx90a — untested**. Try it only after 2.1 has a measured baseline, and keep it only if it beats 2.1 on the same test.

### Not for the server

**MTPLX** and **Splash** are Mac-only (Apple MLX / Metal). **Strata** is Mac Metal only.

---

## 3. Rules for every test above

1. Measure on the real machine first; never adopt from a reported number.
2. Same prompts for before and after: one coding task and one prose task, greedy, fixed seed.
3. Report tok/s, draft accept rate, first-token time, peak memory, and interactive p99.
4. Speculative tricks (MTP, DFlash) must give the **same output** as plain decoding at greedy settings — check it.
5. Keep a trick only if every standing Kildall gate still passes (routing, recall 1-slot + per-slot, abstention, tools, CLI, hooks, soak).
6. Plan rule (v46): speculative decoding is decided **per platform by measurement** — the old Metal ban came from a measured loss on Metal, not a general rule.

---

## Sources

- Video 1 — Alex Grankin, "Every Trick to Make Local AI Faster. Here's How." (YouTube `RRUhZ1rpovk`, measured 8 Nov 2026 on a MacBook Pro M5 Max 128 GB, Qwen3.8-27B Q4, thinking low, 2,000 tokens).
- Video 2 — SimplyExplain, "llama.cpp Just Made Your GPU 2x Faster on Big Models (Turn This On)" (YouTube `PD7ntUZ-KE0`; numbers are user reports from the llama.cpp pull request plus their own GTX 1080 Ti test).
- Splash requirements and release notes: <https://lmstudio.ai/blog/splash-engine>, <https://newreleases.io/project/github/incoai/splash/release/1.4.1>
- MTPLX: <https://pypi.org/project/mtplx/2.9.1/>, <https://medium.com/@vinoth.lingam333/i-got-18-tok-s-from-a-27b-model-on-a-macbook-mlx-native-mtp-speculative-decoding-on-apple-5e1211a06d0c>
- Gemma 4 MTP drafter, Avalon and Strata facts: CLAUDE.md change log, 2026-11-01.
