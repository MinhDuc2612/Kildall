# Kimi K3 HW Mini

Source: Instagram reel (https://www.instagram.com/reel/Dbz8HtFtXq7/). Audio transcribed locally via whisper.cpp (no captions on Instagram's side — whisper misheard the developer's name "Fareed Khan" as "readcon"); frames (screen recording of the GitHub README) confirmed and expanded on the audio. Researched further via web search. Compiled 2026-08-19.

---

## 1. What the video shows

A demo/explainer of **kimi-k3-in-c** (github.com/FareedKhan-dev/kimi-k3-in-c) — an open-source project by developer Fareed Khan that runs Moonshot AI's **Kimi K3**, a 2.78-trillion-parameter model, on a single CPU with 8GB of RAM, no GPU. Confirmed directly from the on-screen README: "kimi-k3-in-c — A 2.78-trillion-parameter model. One CPU. 8 GB of RAM. Kimi K3 inference in portable C99. No BLAS. No framework. No GPU." Headline numbers shown: 2.78T parameters, 1.56 TB checkpoint on disk, 8.24 GB peak RSS (measured), 176 KB total engine size, 0 GPUs. Output is claimed byte-identical to a version of the same model running on a server with 224GB of RAM — same answer, same tokens, at roughly 700% less hardware (the video's phrasing) — or more precisely, per the repo's own chart, "675x smaller" than the naive multi-GPU-cluster requirement.

The repo's own hardware/speed table (shown on screen):

| Machine | RAM | Time/token | What's happening |
|---|---|---|---|
| Ordinary laptop | 8 GB | ~26.5–32.7 s | Whole model streams off disk every step |
| High-end laptop | 32 GB | ~24.2 s | Some of the model now sits in memory |
| Desktop | 64 GB | ~19.8 s | More of it sits in memory |
| Heavy workstation | 128 GB+ | ~5.6–10.7 s | Model fits (mostly) in memory, disk wait mostly gone |

Setup shown on screen: clone the repo (`git clone https://github.com/FareedKhan-dev/kimi-k3-in-c.git`), run `./scripts/k3-doctor.sh` to validate the machine can run it, then `make -j` to build. A weights-free test suite ("ALL WEIGHTLESS TESTS PASSED") verifies the engine matches a PyTorch reference before anyone commits to the 1.56TB download. License: Apache-2.0 for the engine code (the Kimi K3 model weights themselves are governed separately by Moonshot AI's own model license).

## 2. What Kimi K3 actually is (the model being run)

Kimi K3 is Moonshot AI's flagship model, released July 16, 2026 (open weights July 27, 2026) — a 2.8-trillion-parameter sparse Mixture-of-Experts (MoE) model, described as the first open model to reach the 3-trillion-parameter class. Specs:
- **896 experts, 16 activated per token** (~1.8% of the expert pool) — an unusually extreme sparsity ratio even by MoE standards (for comparison, DeepSeek-R1 activates 8 of 256 experts plus 1 shared expert).
- **Kimi Delta Attention (KDA)** — a hybrid linear-attention mechanism (from the earlier "Kimi Linear" research, Oct 2025) that interleaves cheap linear-attention layers with periodic full-attention layers (roughly 3:1), cutting KV-cache memory by up to 75% and enabling the 1,048,576-token (1M) context window without full quadratic attention cost.
- **Attention Residuals (AttnRes)** — replaces standard uniform residual connections with selective retrieval of representations across depth, so later layers can pull directly from useful earlier-layer representations instead of everything being blended uniformly.
- **Stable LatentMoE** with **Quantile Balancing** — the routing framework that decides which 16 of 896 experts fire per token, using router-score quantiles (rather than hand-tuned heuristics) to keep expert load balanced at this scale.
- **Quantization-aware training from the SFT stage onward**, shipping in **MXFP4 weights** (4-bit floating point with per-block scaling) with **MXFP8 activations** — meaning the low-bit representation isn't a lossy afterthought bolted on post-training, the model was trained to tolerate it.
- Native multimodal (text + vision, via a ~401M-parameter MoonViT-V2 encoder).

## 3. How the hardware-usage minimization actually works

This is the part the video's "700% less hardware" hook is built on, and it's worth being precise about, because it's architecture, not compression trickery layered on afterward.

**The core enabling fact:** because Kimi K3 only activates 16 of 896 experts per token (~1.8%), roughly 93% of the 1.56TB checkpoint (the ~1.45TB of routed expert weights) is irrelevant to any single token's computation. The naive approach — load the entire 1.56TB model into RAM — would need on the order of 5.5TB of memory once you account for working buffers. kimi-k3-in-c's insight is: **never load the sleeping 93%. Only fetch what's about to be used, and throw it away right after.**

Mechanically, this breaks into four techniques working together:

**A. Dense-trunk residency, expert streaming.** The small always-active "trunk" of the model (attention layers, layer norms, routing weights, the shared/dense components that touch every token) stays resident in RAM — sized to whatever memory budget you give it via a "packed trunk" (~109GB at full precision, prepared once via `pack-trunk.sh`). The 1.45TB of routed expert weights are never loaded wholesale; instead they live on NVMe SSD in their packed 4-bit (MXFP4) form.

**B. On-demand expert fetch, direct from packed form.** When the router selects which 16 experts a given token needs, the engine streams exactly those expert weight blocks off disk (using low-level direct I/O, bypassing the OS page cache) and multiplies them straight out of their packed 4-bit representation — no separate "unpack, then compute" step, no full-precision intermediate copy sitting in memory. This is the piece that makes 4-bit quantization and disk streaming compound rather than just stack: you save the memory cost of quantization AND avoid ever materializing a decompressed copy.

**C. LRU expert cache.** Because certain experts get selected more often across nearby tokens (specialization means some experts really are "hotter" than others for a given kind of input), a small least-recently-used cache keeps recently-fetched experts around briefly, cutting down on redundant disk reads for the same expert being needed again soon.

**D. Memory as a dial, not a wall.** Because the same on-disk 4-bit representation is the source of truth at every memory tier, the engine produces byte-identical output whether it's running with only 8GB resident (streaming almost everything, every step) or 128GB+ resident (most of the trunk and even some experts staying cached, only true cache-misses hitting disk). More RAM only buys speed — because it means fewer disk round-trips per token — it never changes the answer. That's the "memory becomes a dial" framing used by multiple people covering this project.

**The real cost, made explicit by the project itself:** this trades memory for time and storage. At the 8GB floor, generation runs roughly 26–33 seconds per token — this is a proof-of-concept for feasibility, explicitly not a production serving path. It also requires ~1.7TB of fast local NVMe storage (1.56TB checkpoint + ~109GB packed trunk) and a CPU with AVX2+FMA, Linux x86-64 only. The project's own README is upfront that the headline isn't speed, it's the demonstration that the wall between a normal computer and a frontier-scale model is storage capacity and patience, not GPU access.

## 4. This is a known pattern, not a one-off trick

kimi-k3-in-c is a from-scratch, dependency-free (no PyTorch, no BLAS, no CUDA) implementation of a technique that already has an active research and tooling lineage:

- **MoE-specific offloading + mixed quantization** (Eliseev & Mazur, "Fast MoE Inference with Offloading," 2023) — established the pattern of keeping non-expert weights resident and offloading/quantizing experts, informed by the observation that expert-access patterns have exploitable regularities, enabling Mixtral-8x7B on free-tier Colab.
- **HOBBIT** (2024) — adds token-level dynamic expert loading, layer-level adaptive prefetching (predicting which experts the *next* layer will need while the current layer still computes), and a multidimensional expert caching policy — the same prefetch-to-hide-latency idea kimi-k3-in-c's LRU cache is a simpler version of.
- **DynaExq** (2025) — goes further with a per-expert "hot/warm/cold" precision state machine, dynamically promoting frequently-used experts to higher precision and demoting rare ones, rather than kimi-k3-in-c's simpler fixed 4-bit-for-everything approach.
- Similar SSD-expert-streaming requests/implementations exist for consumer-hardware inference stacks generally (e.g. an open feature request for MLX on Apple Silicon citing the same "MoE models only activate a subset of experts" logic to fit models like GLM-5.2 into 128GB unified memory).

**One caveat worth knowing from the research literature:** at least one 2026 study on SSD offloading for MoE weights found that while offloading successfully reduces peak memory, it can significantly increase *energy* consumed per generated token during decode (3.8×–12.5× higher per-token energy reported for some models/batch sizes) due to Flash SSD read energy costs — a tradeoff kimi-k3-in-c's own README implicitly acknowledges by being upfront that this is a memory-vs-time tradeoff, not a free lunch.

## 5. Sources

- kimi-k3-in-c (repo) — https://github.com/FareedKhan-dev/kimi-k3-in-c
- Deep-dive writeup — https://themenonlab.blog/blog/kimi-k3-in-c-trillion-parameter-model-8gb-ram
- Technical breakdown (4-technique summary) — https://daily.dev/posts/kimi-k3-runs-on-8gb-cpu-no-gpu-khbh5h19l
- Coverage — https://essamamdani.com/blog/kimi-k3-in-c-2-78-trillion-parameters-single-cpu-8gb-ram
- Coverage — https://opensource.aibestnews.com/en/project/20260804-fareedkhan-dev-kimi-k3-in-c/
- Kimi K3 launch coverage — MarkTechPost — https://www.marktechpost.com/2026/07/16/moonshot-ai-releases-kimi-k3-a-2-8-trillion-parameter-open-moe-model-with-kimi-delta-attention-and-1m-context/
- Kimi K3 spec sheet — apidog — https://apidog.com/blog/what-is-kimi-k3/
- Kimi K3 architecture explainer — dplooy — https://www.dplooy.com/blog/kimi-k3-28t-parameters-1m-context-open-weights
- Kimi K3 model overview — Hugging Face blog — https://huggingface.co/blog/ResterChed/kimi-k3-model-overview-mxfp4-quantization-open-wei
- "SSD Offloading for LLM Mixture-of-Experts Weights" (energy cost study) — arXiv:2508.06978 — https://arxiv.org/html/2508.06978v1
- "A Mixed Precision Expert Offloading System for Fast MoE Inference" (HOBBIT) — arXiv:2411.01433 — https://arxiv.org/html/2411.01433
- "Fast MoE Inference with Offloading" — https://www.emergentmind.com/papers/2312.17238
- "Dynamic Expert Quantization for Scalable Mixture-of-Experts" (DynaExq) — arXiv:2511.15015 — https://arxiv.org/html/2511.15015
- "SSD Streaming for AI Models: How to Turn RAM from a Wall into a Dial" — https://www.mindstudio.ai/blog/ssd-streaming-ai-models-ram-dial

## 6. Change log
- 2026-08-19 — Created. Sourced from Instagram reel (whisper.cpp transcript + frame confirmation) + deep research pass.
- 2026-08-20 — Link/claim verification sweep: repo and headline numbers (2.78T params, 8.24GB peak RSS, 176KB engine) reconfirmed unchanged at v1.0.0. Kimi K3 architecture claims reconfirmed. No corrections needed.
