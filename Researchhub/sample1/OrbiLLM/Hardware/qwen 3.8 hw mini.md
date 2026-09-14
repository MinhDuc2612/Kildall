# Qwen 3.8 HW Mini

Source: https://ofox.ai/blog/qwen-3-8-27b-run-locally-vram-gguf-2026/ — a hardware-requirements writeup for running Qwen3.8-27B locally via GGUF quantization. Researched further via deep-research + direct source verification. Compiled 2026-08-23.

---

## 1. What the article shows

The article covers running **Qwen3.8-27B** (Alibaba's dense, vision-capable 27.78B-parameter model — the open-license sibling of the much larger Qwen3.8-Max) locally on consumer hardware, using GGUF quantization via **llama.cpp**.

GGUF quant sizes cited:

| Bits | File size | Combined RAM+VRAM needed |
|---|---|---|
| 2-bit (Unsloth UD-IQ2_XXS) | 9.01–10.68 GB | 9–11 GB |
| 3-bit | 11.91–13.82 GB | — |
| 4-bit (vendor-recommended default) | 16.06–17.92 GB | 16–19 GB |
| 6-bit | 22.43–25.92 GB | — |
| 8-bit | 28.60–31.46 GB | — |

Hardware guidance from the article: 32GB VRAM/unified memory → 4-bit or 6-bit; 24GB → 4-bit; 16GB VRAM → 3-bit fully on GPU or 4-bit with RAM offload; 16GB unified-memory Mac → 2-bit only; under 16GB → not recommended. The article's key clarification: **"the 17GB figure is RAM plus VRAM, not a 16GB card"** — the quant file has to fit in *combined* memory, not VRAM alone, or it pages to disk and slows down badly.

Tooling: `brew install llama.cpp`, referencing build b10450 (Aug 2026) for `qwen3_5` architecture support. Vision needs a separate mmproj file (0.63–0.93GB).

Real-world speed on an M2 Pro 16GB Mac at 2-bit: 7.11 tok/s generation on a short synthetic prompt, dropping to 2.91 tok/s generation on a real 7,072-token prompt — prompt-processing speed itself degrades with context length (43.58 tok/s at token 2,090 → 37.82 tok/s by token 6,186).

**Cross-checked against the actual GGUF repos** (bartowski and Unsloth's Hugging Face quant releases): the specific file sizes differ slightly by quantizer/method but land in the same range — bartowski's Q4_K_M is 17.77GB (matches the ~17GB claim closely), and their IQ2_XXS 2-bit is 9.39GB. Unsloth's own official guidance states 4-bit needs 16–19GB and 2-bit needs 9–11GB combined VRAM/RAM — consistent with the source article's numbers.

## 2. What Qwen3.8-27B actually is (the model being run)

Qwen3.8-27B is a **dense** model — all 27.78B parameters activate on every single token, with no sparse routing. This is architecturally the opposite of Kimi K3 (see `kimi k3 hw mini.md` in this same folder): Kimi K3 is a 2.8T-parameter Mixture-of-Experts model that only activates ~104B parameters (16 of 896 experts) per token, leaving ~93% of its weights untouched for any given token. Qwen3.8-27B has no such untouched fraction — every parameter matters for every token, all the time.

This single architectural fact is why the two models' hardware-minimization techniques are completely different in kind, not just degree (see Section 4).

Qwen3.8-27B ships under Apache-2.0 — the fully open-license sibling in the Qwen3.8 line, positioned as the self-hostable alternative to the much larger, custom-licensed Qwen3.8-2.4T-A95B (Qwen3.8-Max) checkpoint.

## 3. How the hardware-usage minimization actually works

Because there's no sparsity to exploit (unlike an MoE model), Qwen3.8-27B's entire hardware-minimization story comes down to two orthogonal techniques stacked together: **quantization** (making each parameter cheaper to store and compute) and **RAM/VRAM offload splitting** (deciding which layers live where when the whole quantized model still doesn't fit on the GPU alone).

**A. GGUF quantization (the primary lever).** GGUF is llama.cpp's model-file format, supporting per-tensor quantization at multiple bit-depths (2-bit through 8-bit, plus native BF16). Going from BF16 (~55.5GB for 27.78B params at 2 bytes/param) down to 4-bit cuts the footprint to roughly 17GB — about a 3.2x reduction — and down to 2-bit cuts it further to roughly 9-10GB, an ~5.5x reduction from full precision. Unlike Kimi K3, which trained with quantization-aware training from the SFT stage specifically to tolerate its shipped 4-bit MXFP4 format, Qwen3.8-27B's GGUF quants are **post-training quantization** — the base model is trained at higher precision, then quantized afterward by third parties (Unsloth, bartowski) using calibration data (an "imatrix," importance matrix) to decide how aggressively each individual tensor can be compressed without a large quality loss.

**B. Unsloth's Dynamic quantization — the mechanism behind the good scores at low bit-depths.** Rather than applying one uniform bit-depth across the entire model, Unsloth's Dynamic v3.0 method selectively adjusts the quantization level per layer — some layers (typically more quality-sensitive ones like output/embedding layers) keep more bits, while less sensitive layers get compressed harder — and the specific per-layer combination is tuned per model rather than a fixed rule. This is analogous in spirit (not mechanism) to Kimi K3's engine keeping its "trunk" resident while treating experts differently — both are non-uniform treatment of different parts of the same model — but where Kimi K3's non-uniformity is about *which weights get loaded at all* (routing-driven), Unsloth's is about *how many bits each weight gets* (precision-driven). Qwen3.8-27B was in fact the flagship model used to demonstrate Dynamic v3.0, with over 5.1 million downloads of its quants in the first 5 days after release.

**C. RAM/VRAM offload — the fallback when the quant file still doesn't fit on the GPU.** llama.cpp's `-ngl` (number of GPU layers) flag controls how many of the model's transformer layers get placed on GPU vs left on CPU/RAM. When a quant is small enough to fit entirely in VRAM, every layer runs on GPU at full speed. When it isn't, some layers spill to system RAM and run on CPU instead — and unlike an MoE model's expert-streaming (which only ever moves a *small selected subset* of weights per token), a dense model's CPU-resident layers process **every single token through every single one of those layers**, every time, with no way to skip work for a token that "doesn't need" a given layer. This is the fundamental reason dense-model offloading degrades so sharply: there's no sparsity for the offloaded portion to hide behind.

**The real cost, matching the article's own numbers:** at the 2-bit floor on a 16GB unified-memory Mac, generation speed drops from ~7 tok/s on short prompts to under 3 tok/s once the context grows past ~7K tokens — a real, felt slowdown, not a rounding error. The article's core practical warning — RAM+VRAM must be at least the size of the quant file, or the OS starts paging the model to disk mid-inference and performance falls off a cliff — is the dense-model equivalent of Kimi K3's "memory as a dial" framing, except for a dense model that dial has a much steeper cliff: there's no cache-hit path that avoids touching most of the model, because *all* of the model is needed for *every* token.

## 4. How this compares to Kimi K3's MoE-based minimization

This is the direct answer to "what's actually different between these two techniques":

| | Qwen3.8-27B (dense, this doc) | Kimi K3 (MoE, see `kimi k3 hw mini.md`) |
|---|---|---|
| Params touched per token | All 27.78B, every time | ~104B of 2.8T (~3.7%) |
| Minimization lever | Bit-depth reduction (quantization) | Which weights load at all (routing + streaming) |
| Offload cost when memory is tight | Every offloaded layer still processes every token — offload cost scales with *how much* is offloaded, linearly, no way around it | Offloaded experts are read *only when that token's router selects them* — offload cost scales with *how sparse* the model already is, largely independent of total size |
| Theoretical floor | Bounded by quantization's accuracy/size tradeoff — can't go much below ~2-bit without severe quality loss | Bounded by disk I/O speed for expert fetches — a much larger model can still hit a comparable per-token floor if the active fraction is small enough |
| Why the two use different techniques at all | No sparsity to exploit — there's nothing "sleeping" to skip loading | 93%+ of the model IS sleeping for any given token — the entire technique exists to avoid touching that sleeping majority |

**One data point worth flagging on the "which approach is actually more energy-efficient" question:** a 2026 energy-cost study on SSD-offloaded MoE inference (arXiv:2508.06978, also cited in `kimi k3 hw mini.md`) found that Flash/SSD read energy is roughly 26x higher per bit than HBM read energy, and that for MoE models specifically, SSD-offloaded expert access can account for up to ~80% of total per-token inference energy — meaning MoE expert-streaming, while it dramatically cuts *peak memory*, can cost *more energy per token* than keeping everything resident would, if disk reads are frequent enough. This doesn't directly compare to Qwen3.8-27B's RAM/VRAM offload (a different memory tier than SSD), but it's a useful caution against assuming "smaller footprint" automatically means "more efficient" for either architecture — the tradeoff is real in both directions, just shaped differently by whether the model is sparse or dense.

## 5. Sources

- Source article — https://ofox.ai/blog/qwen-3-8-27b-run-locally-vram-gguf-2026/
- bartowski's Qwen3.8-27B GGUF quants (file sizes cross-checked) — https://huggingface.co/bartowski/Qwen3.8-27B-GGUF
- Unsloth's official Qwen3.8-27B hardware guidance — https://unsloth.ai/docs/models/qwen3.8
- Unsloth Dynamic v3.0 GGUF quantization method — https://unsloth.ai/docs/basics/dynamic-3.0-ggufs
- SSD/Flash offloading energy-cost study (shared reference with the Kimi K3 doc) — arXiv:2508.06978 — https://arxiv.org/html/2508.06978v1
- Sibling doc for the MoE-side comparison — `kimi k3 hw mini.md` (this folder)

## 6. Methodology note

Built from a direct fetch of the source article plus a deep-research workflow pass. The workflow hit the session's rate limit mid-verification and its synthesis step failed (recurring failure mode this session — see `3.5T local LLM hardware workflow.md` and `cloud call.md` for earlier instances). This file was hand-assembled from the claims that survived 2-3 vote adversarial verification, cross-checked directly against the primary GGUF repo pages (bartowski, Unsloth) rather than relying only on the workflow's unverified claims. A handful of secondary claims (an offload-speed "cliff" benchmark from a third-party blog, some Kimi K2-specific architecture numbers) never finished verification before the rate limit hit — they're omitted here rather than reported as fact.

## 7. Change log

- 2026-08-23 — Created. Sourced from the ofox.ai article (direct fetch) + a deep-research pass that hit the session rate limit and failed synthesis; hand-assembled from verified claims, cross-checked against bartowski's and Unsloth's actual GGUF repo pages.
