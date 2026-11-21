# Fit models — Mac mini M4 24 GB, 2+ tok/s at all times

**2026-11-21 · Claude · Phase R step R2 (first sample4 file).** User rule: *"just use models fit on this machine — by
fit I mean 2 tok/s+ at all time"*, then *"Remove the giants and flash next and /last30days research and replace it
with the new rules."*

**Answer first:** every text model on the drive passes 2 tok/s on a short prompt **except Qwen3.8-Flash-Next
(1.08–1.24 tok/s) and GLM-5.3-Flash IQ1_S (0.65–0.70 tok/s)** — both SSD-streamed. No Lane C giant was ever on disk;
by arithmetic they run 2.2–17.9 s per token here. **Worst-case speed (long context, 600 s soak) is not yet measured
for any model except Lane A.**

---

## 1. Measured on this Mac

Source: `/Volumes/ES2TB/AI-Models/speed-test-2026-11-05/results_{chat,more}.jsonl` (two 96-token rounds, short
prompt, cold load, llama.cpp unless noted) and the Kildall gates for Lane A.

| Model | File | tok/s | Verdict |
|---|---|---|---|
| Gemma 4 26B-A4B UD-IQ3_S (Lane A) | 11.3 GB | **26.67** (gate 2026-11-06) · 29.33 (2026-09-08) | ✅ |
| gpt-oss-20b UD-Q4_K_XL | 11.9 GB | 35.98 / 35.89 | ✅ |
| North Mini Code 1.0 (30B-A3B) UD-IQ4_XS | 15.2 GB | 31.19 / 31.48 | ✅ |
| Qwen3.6-35B-A3B UD-IQ4_NL_XL | 19.5 GB | 28.22 / 29.56 | ✅ ⚠ at the RAM ceiling |
| Nemotron 3.5 Lightning 30B-A3B UD-IQ4_NL | 21.2 GB | 27.80 / 27.58 | ✅ ⚠ at the RAM ceiling |
| Nemotron 3.5 Bolt E4B UD-Q4_K_XL (vision) | 5.1 GB | 24.22 / 24.34 | ✅ |
| Qwen3 8B (Ollama) | 5.2 GB | 18.19 / 19.07 | ✅ |
| Muse-Glimmer-30B UD-Q4_K_XL (vision) | 15.9 GB | 6.32 / 6.40 | ✅ |
| Nanbeige4.3-33B IQ4_XS | 18.6 GB | 5.51 / 5.53 | ✅ |
| Swift-1.5-Qwen3.8-27B Q4_K_M (dense) | 17.4 GB | 5.46 / 5.43 | ✅ |
| Qwen3.8-27B UD-Q4_K_M (dense, 2026-11-01 llama-bench) | 16.5 GB | 5.48 ± 0.45 | ✅ |
| LFM3-1.7B QAD-Q4_0 | 1.0 GB | 72.85 / 72.52 | ✅ |
| Ternary-Bonsai-2-2B Q2_0 | 0.5 GB | 86.72 / 84.22 | ✅ |
| **Qwen3.8-Flash-Next MLX 4-bit (slotstream, from ES2TB)** | 105 GB | **1.08 / 1.24** | ❌ **removed** |
| **GLM-5.3-Flash-Maya-XS IQ1_S** | 73.4 GB | **0.70 / 0.65** | ❌ **removed** |
| K2-Horizon-32B IQ4_XS · K2-Horizon-MoVA-36B-A4B IQ4_XS · Nemotron-Labs-Dory1.0-4B Q5_K_M | 19.4 / 20.4 / 3.7 GB | not measured | ⚠ not usable until measured |
| Flint UD-Q3_K_XL | 18.5 GB | did not start in the speed test; ran in the code_1.24 bench (13/18 hard jobs, invented `shell_job` calls) | ⚠ |

**Margins.** The dense 27–33B models have ~2.7× headroom over 2 tok/s on compute. The 19.5–21.2 GB MoE models have
14× headroom on compute but sit at the RAM ceiling: their risk is swap, not speed. On 2026-11-06 Qwen3.6 pushed swap
to 9.1 GB in the code_1.24 bench. Both groups need the worst-case gate.

**Quality measured here (code_1.24 hard round, 2026-11-06, 18 script-graded jobs):** Gemma plain 16/18 in 346 s
(best), gpt-oss-20b 15/18, Nemotron Lightning 15/18, Gemma thinking 14/18, Flint 13/18, North Mini lower. Qwen3.6
was not in the hard round.

## 2. /last30days run (2026-11-21)

Raw file: `~/Documents/Last30Days/best-local-llms-for-mac-mini-m4-24gb-raw-v3b.md`. Result: **nothing cleared the
relevance floor.** Reddit returned 0 items on every query (keyless path blocked), HN 21 and GitHub 22 items were all
below the floor, YouTube 1 item. The first run failed SSL (python.org Python 3.14 has no CA certificates — run with
`SSL_CERT_FILE=/etc/ssl/cert.pem`). Community evidence for this window: **insufficient**. Findings below are from web
supplements only.

## 3. Web supplements (2026-11-21)

All benchmark numbers here are **vendor-reported or blog-repeated, not independently verified**, and speeds are
mostly calculator estimates. None replaces a measurement on this Mac.

- **Qwen3.6-35B-A3B** is the most-cited 3B-active pick for 24 GB Macs: SWE-bench Verified **73.4**, GPQA Diamond
  **86.0**, AIME 2026 **92.7** (vendor figures repeated by labellerr.com and a Medium post). Qwen3.5-27B dense:
  GPQA 85.5, AIME26 92.6; Gemma4-31B: 84.3 / 89.2 (same table).
- **24 GB picks disagree** across guides (apxml.com, insiderllm.com, promptquorum.com, llmcheck.net, mlx.app,
  matterai.so): Qwen3.6-27B Q4_K_M (~16.8 GB), Devstral Small 2 (24B, ~15 GB), North Mini Code 1.0, Qwen3.8-27B.
  Several guides are machine-written; some model names could not be verified.
- **Qwen3-Coder-Next (80B-A3B)** needs ~53.7 GB at Q4_K_M. A calculator estimates ~3.8 tok/s on an M4 24 GB with
  offload (willitrunai.com) — **an estimate; must be measured before it can pass the rule.** Closest real data:
  Qwen3.6-35B-A3B at **15.0 tok/s** on a 16 GB M5 MacBook Air with routed experts on SSD (Hugging Face forum).
- **Base M4 bandwidth is 120 GB/s**; many published "M4 24 GB" numbers are M4 Pro (273 GB/s) — not comparable.

## 4. What replaces the giants' jobs

| Old giant job | Now | Evidence |
|---|---|---|
| Agentic coding, tool calling (Kimi K3, GLM-5.3, DeepSeek-V4-Flash) | Lane A Gemma; Lane C candidate Qwen3.6-35B-A3B | Gemma best on the 18 hard jobs here; Qwen3.6 73.4 SWE-bench Verified ⚠ vendor |
| Math, reasoning (GLM-5.2, GLM-5.3-Flash, Hy4-preview) | Lane A; Lane C candidate Qwen3.6-35B-A3B | GPQA 86.0 / AIME26 92.7 ⚠ vendor; Gemma solved the n = 40 proof job in 20 s |
| Backend code, long context (DeepSeek-V4-Pro, Qwen3.8-2.4T) | Lane A at 4K (production) / 2 × 32K (code_1.24) | **Real loss:** no 1M-token context here; 16K per slot failed the soak (2026-10-14) |
| Cheap coding (DeepSeek-V4-Flash) | gpt-oss-20b, North Mini Code (Lane B) | 36 / 31 tok/s here; gpt-oss 15/18 hard jobs |

## 5. Next measurements (in order)

1. Worst case for Lane C candidates: longest allowed context, 600 s soak, swap at start ≤ 3 GB, nothing else loaded.
2. K2-Horizon-32B, K2-Horizon-MoVA-36B-A4B, Dory 4B: first speed test.
3. Qwen3.6-35B-A3B on the 18 hard jobs.
