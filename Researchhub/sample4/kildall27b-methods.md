# Kildall-27b methods: Qwen3.8-27B (Swift-1.5) on the 24 GB Mac mini M4

**Built:** 2026-11-22 for the Kildall-27b sub-project. /last30days run + web search. Community evidence was thin
(Reddit 0 items, X not configured); most facts come from blogs, model cards and release notes. Single-source and
vendor numbers are marked.

## Answer first

| Method | Works on this Mac? | Best number found | Status |
|---|---|---|---|
| Plain llama.cpp, Q4 | Yes | 5.46 tok/s write (measured here 2026-11-01); others 5.8-6.0 | baseline |
| **DFlash 2 on MLX** | Yes | **11.7-12.2 tok/s, 1.8-1.9x, peak 19.4 GB** on a 24 GB M4 mini (single blog) | best known speedup here |
| DFlash 2 on llama.cpp | Unknown | M3 Ultra, b11404 Metal few-row MMA: code 30.2 -> ~110, prose 16.8 -> 62.6 tok/s | measure on b12359 |
| Native MTP (llama.cpp) | Yes, but slower | 24 GB M4: prose -24%, code -4% (old build b96806d, before few-row MMA) | re-measure on b12359 |
| Splash (Inco) | **No** | 74 tok/s on M5 Pro 48 GB (vendor) | needs 36 GB+ (48 GB recommended) |
| Metal sparse FA (#28098) | No | gains only on DeepSeek-V4 style models | Qwen path disabled; n_kv <= 4096 only |
| Training-free sparse prefill (papers) | Not in llama.cpp | 2.3-2.4x prefill at 512K (arXiv 2611.04313) | research only |

## The model file on disk

- `/Volumes/ES2TB/AI-Models/Swift-1.5-Qwen3.8-27B-Q4_K_M/Swift-1.5-Qwen3.8-27B-Q4_K_M.gguf`, 17,442,399,936 bytes.
  The plain unsloth Qwen3.8-27B GGUF folder is empty.
- The GGUF keeps the MTP head: tensors `blk.64.nextn.*`, key `qwen35.nextn_predict_layers` (checked 2026-11-22).
- `qwen35`: 64 layers; 16 full attention, 48 Gated DeltaNet linear. Only 16 layers keep a growing KV cache,
  so sparse attention can help at most those layers.
- No vision projector on disk. Swift card is tagged image-text-to-text. Base projector 0.6-0.93 GB; fit with
  the fine-tuned weights not tested.
- Licence: **Swift Open License v1.0**, free under US$1M gross yearly revenue; above that a Swift Enterprise
  Licence is needed. Base Qwen3.8-27B is Apache-2.0. Matters for paid clients (Phase 9.10).
- Vendor claim: ~24.5% fewer reasoning tokens than base, similar or higher LiveCodeBench v6. Fewer thinking tokens
  is real speed at 5 tok/s.
- Smaller Swift quants: Q4_K_S 16.4 GB, IQ4_XS 15.5 GB, IQ3_M 14.9 GB (free memory for context or helpers).

## Splash

- Mac-only (MLX/Metal), two supported models (Qwen3.8-27B, Qwen3.8-Flash-Next), no settings.
- Package: ~15 GiB 4-bit weights + 1.2 GiB DFlash 2 draft + 0.93 GB vision; cannot start below ~18 GiB for weights
  and one request. M3+ and macOS 26.4+. This Mac: M4, macOS 26.7.3, 24 GB with a 20 GB GPU limit.
- Uses its own Qwen3.8-27B weights, not Swift-1.5. One GitHub issue: one unsigned commit, no tie to published source.
- **Verdict:** record for a Mac with 48 GB+. Not this Mac; not the Linux reward server.

## Sparse attention

- llama.cpp b10785 `metal : add sparse FA (#28098)`: needs a model trained for sparse attention, gated to
  n_kv_max <= 4096; "qwen4: enable sparse attention" disabled in the same release.
- Training-free block-sparse prefill (FlashPrefill V2, Coarse Semantic Blocks): gains at 64K-512K only, no llama.cpp
  kernel. Kildall-27b on 24 GB runs 4K-32K.
- **Verdict:** measured experiment in the long-context slice only; no gain expected at today's context sizes.

## Computer use

- Qwen3.8-27B OSWorld-Verified 84.3 (vendor-reported). No ScreenSpot-Pro score found. System score with Qwen's own
  harness, not what Kildall will get.

## Sources

cooconsbit (24 GB Mac mini: MTP vs DFlash 2; DFlash 2 1.8x), sudoingX/qwen38-mtp, rohitai.com (b11404 Metal few-row
MMA), inco.ai + jundot/omlx Splash docs, Anbeeld/Qwen3.8-27B-DFlash2-GGUF, z-lab/Qwen3.8-27B-DFlash2,
ukisai/Swift-1.5-Qwen3.8-27B-GGUF, newreleases.io (llama.cpp b10785), arXiv 2611.04313, qubrid.com.
Raw: `~/Documents/Last30Days/best-ways-to-run-qwen3-8-27b-fast-with-long-context-on-a-24gb-mac-raw-v3.md`.
