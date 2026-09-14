# mach1 hwmini — Mach-1 by Syzygy: Hardware Minimisation & Pace Architecture

**Sources (two of the supplied links, same subject):**
- [withsyzygy.com/docs/mach](https://withsyzygy.com/docs/mach) — primary vendor documentation
- [threads.com/@theultronai/post/Db7mSv5G4z1](https://www.threads.com/@theultronai/post/Db7mSv5G4z1) — *"a 35-billion-parameter AI now runs fully in memory on the cheapest Mac Apple sells"*

**Built:** 2026-09-01 · Sample 2 · self-contained

> **Why one file for two links.** The Threads post **never names the model** — it says only "a
> 35-billion-parameter AI", "16GB M4 mac mini", "no hard drive streaming", "one copy-paste command".
> Every one of those matches Mach-1's published specification exactly. The identification is
> **inference, strongly supported but not stated by the poster.** If the post meant something else,
> this file's framing of it is wrong; its Mach-1 facts are not.

**One line:** a 35B MoE compressed to **~1.7 bits per weight** that runs **add/subtract-only** —
inference *without ever multiplying by a weight* — and fits a 16 GB Mac with room to spare.

---

## 1. What it is

| Field | Value |
|---|---|
| Name | **Mach-1-Additive-35B** (Mach-1 Small); multimodal variant exists |
| Base model | **Qwen3.6-35B-A3B** |
| Architecture | **MoE — 256 experts, top-8 routing**, 35B total / **3B active** |
| Quantisation | **~1.7 bits/weight** |
| Weight footprint | **~8.1 GB** text pack; **~9.0 GB** with vision tower |
| Hardware | **Apple Silicon Mac, M1 or later**; macOS with Metal |
| Dependencies | **MLX only**; Python 3.12+ |
| Licence | **Apache-2.0** |
| Repo | `SyzygyResearch/mach-engine` |

---

## 2. Hardware-minimisation architecture

Mach-1 stacks **two** levers that the other systems in this folder each use only one of.

### 2.1 Lever one — MoE sparsity

35B total, **3B active** per token (256 experts, top-8). Same family of saving as Kimi K3, but at
1/80th the scale.

### 2.2 Lever two — extreme sub-2-bit quantisation, done differently

**~1.7 bits per weight** is far below the 4-bit floor most GGUF pipelines treat as aggressive. The
mechanism is not ordinary quantisation:

> *"every weight matmul is add/subtract-only over integer codes"*

Weights are integer codes, and the matmul becomes addition and subtraction — hence
**"Mach-1 Additive"** and Syzygy's own framing: *"inference without ever multiplying by a weight."*

### 2.3 The implementation trick — fused decode-in-GEMV Metal kernels

This is the part that actually makes it fit, and it is the most transferable idea here.

> **"fused decode-in-GEMV Metal kernels"** — quantised weights are decoded *inside* the
> matrix-vector product, so **no dequantised copy of the model ever exists in memory.**

Normal quantised inference decompresses weights to a working precision before multiplying, so peak
memory exceeds the file size. Mach-1 fuses decode into the GEMV, meaning **~8.1 GB on disk is
~8.1 GB in use.** On a 16 GB machine, avoiding a transient dequantised copy is the difference
between fitting and swapping.

### 2.4 The contrast that makes the Threads post meaningful

The post's boast is *"no hard drive streaming"* — and that is a direct, if unwitting, contrast with
`kimik3 hwmini.md`, which achieves its result **by** streaming from disk:

| | Kimi K3 in C | Mach-1 |
|---|---|---|
| Where weights live at inference | **disk** (1.45 TB streamed) | **RAM** (~8.1 GB resident) |
| Storage needed | **~1.7 TB** | ~8–9 GB |
| Quality cost | none (byte-identical) | **~3.7% loss** vs BF16 teacher |
| Speed | 5.6–26.5 **s/token** | claimed **up to 120 tok/s** |
| Model size served | **2.78T** | 35B |

Two opposite answers to the same question. Kimi K3 keeps full quality and pays in time and 1.7 TB of
disk; Mach-1 keeps speed and a tiny footprint and pays ~3.7% of quality.

---

## 3. Pace architecture

| Claim | Value | Source |
|---|---|---|
| Throughput | **"up to 120 tokens per second"** | secondary coverage |
| Footprint at that speed | "at 7 GB… comfortably fits on consumer laptops" | secondary coverage |

**Why it is fast, structurally:** only 3B parameters are active per token, the weights are ~1.7-bit
integer codes, the operation is add/subtract rather than multiply, and decode is fused into the
GEMV so no extra memory traffic is spent materialising weights. Every one of those cuts memory
bandwidth, which is the binding constraint for single-stream generation on Apple Silicon.

**Unverified, and flagged as such:** the vendor docs page fetched for this file contains **no
tokens/sec figure at all**. The 120 tok/s number comes from secondary coverage, not from Syzygy's
own documentation as read here. Treat it as a marketing figure until measured.

---

## 4. Quality retention — two numbers, both recorded

| Claim | Figure | Where |
|---|---|---|
| Syzygy's launch post | *"recovers **95%** of the performance of the original full precision model, Qwen 3.6 35b, across 12 agentic and reasoning [benchmarks]"* | Syzygy on X |
| Hosted-GPU evaluation, Aug 2026 | **96.3%** — unweighted mean of twelve benchmark-level score-retention ratios vs its own BF16 teacher | secondary coverage |

Consistent with each other, and both describe the same 12-benchmark comparison. Note the framing in
both: retention is measured **against its own BF16 teacher**, not against a frontier model. The
claim is "this compression costs ~4%", not "this is as good as a big model."

---

## 5. Running it

```bash
pip install mach-engine

mach-generate SyzygyResearch/Mach-1-Additive-35B --prompt "..."
mach-serve    SyzygyResearch/Mach-1-Additive-35B --port 8080
```

`mach-serve` exposes **OpenAI-compatible** and **Anthropic Messages API** endpoints. This is the
"one copy-paste command" the Threads post refers to, and the reason it can say *"no admin password,
no API key"* — a `pip install` needs neither.

---

## 6. Honest gaps and unresolved conflicts

- **Footprint is quoted three different ways** across sources: **~8.1 GB** (vendor docs, text pack),
  *"about 8 GB"*, and *"at 7 GB"*. The vendor docs figure is the one to trust; the discrepancy is
  recorded rather than averaged away.
- **No tokens/sec in the primary docs.** The 120 tok/s figure is secondary-source only.
- **Not run.** Nothing here was installed or measured. No independent reproduction of either the
  speed or the retention numbers.
- **Apple Silicon only.** Metal kernels are the mechanism, so this does not transfer to NVIDIA or
  CPU as-is. The *idea* (fused decode-in-GEMV) transfers; this implementation does not.
- **The "no multiplication" claim was not verified at the kernel level** — the repo source was not
  read. It is Syzygy's description of their own method.
- **The Threads identification is inference.** See the note at the top of this file.
- **Retention is against its own teacher.** ~96% of Qwen3.6-35B-A3B is the claim. What that means
  against a current frontier model is a separate, unaddressed question.

## Sources

1. [Syzygy — Mach engine documentation](https://withsyzygy.com/docs/mach) — primary: model spec, MoE config, bits/weight, footprint, kernels, licence, install
2. [Syzygy Research on X — Mach-1 Additive launch](https://x.com/syzygyeng/status/2084350792841195992) — the 95% retention and "without ever multiplying by a weight" claims
3. [Mach-1 Small benchmarks — Syzygy](https://withsyzygy.com/docs/mach/benchmarks)
4. [threads.com/@theultronai/post/Db7mSv5G4z1](https://www.threads.com/@theultronai/post/Db7mSv5G4z1) — the unnamed 35B-on-16GB-M4 claim
5. [Running a 35B Coding Model on a 16GB Mac Mini — Medium](https://medium.com/@omprakash.work96/running-a-35b-coding-model-on-a-16gb-mac-mini-4ae7ffaf32c6) ⚠️ **blocks automated probes** — returns no response to `curl` even with browser headers, but the article was **confirmed live and its content retrieved via search on 2026-09-02**. The link is correct; only direct fetching is blocked.
6. [A 35-billion-parameter model now runs on a $599 Mac Mini — Ben Rees](https://www.bjrees.com/a-35-billion-parameter-model-on-a-mac-mini) — sceptical read

## Change Log

- **2026-09-01** — Created covering **two** of the supplied links, since the @theultronai Threads
  post ("a 35-billion-parameter AI… 16GB M4 mac mini… no hard drive streaming… one copy-paste
  command") **never names its subject** but matches Mach-1's published specification on every
  detail; the identification is recorded as strongly-supported inference, not fact.
  Verified from Syzygy's own docs: **Mach-1-Additive-35B**, based on **Qwen3.6-35B-A3B**, MoE with
  **256 experts / top-8** (3B active), **~1.7 bits per weight**, **~8.1 GB** text pack / ~9.0 GB
  with vision, **Apache-2.0**, MLX-only, Apple Silicon M1+.
  Key architectural finding: Mach-1 **stacks two levers** where the other systems in this folder use
  one each — MoE sparsity *and* extreme sub-2-bit quantisation — and the implementation trick is
  **fused decode-in-GEMV Metal kernels**, so **no dequantised copy of the model ever exists in
  memory**, making the on-disk size the in-use size. Its weight matmul is **add/subtract-only over
  integer codes**, which is where the "Additive" name and the "inference without ever multiplying by
  a weight" claim come from.
  Recorded the direct opposition to `kimik3 hwmini.md`: the Threads post's boast of **"no hard drive
  streaming"** is precisely the technique Kimi K3 relies on. Two opposite trades — Kimi K3 keeps
  full quality and pays 1.7 TB of disk plus seconds per token; Mach-1 keeps speed and an 8 GB
  footprint and pays ~3.7% quality.
  Conflicts left visible rather than smoothed: footprint quoted as **8.1 GB / "about 8 GB" / "at
  7 GB"** by three sources, and retention quoted as **95%** (Syzygy's launch post) vs **96.3%**
  (August 2026 hosted-GPU evaluation, unweighted mean over 12 benchmarks vs its own BF16 teacher).
  Flagged that the **primary docs contain no tokens/sec figure** — the widely-repeated **120 tok/s**
  is secondary-source only — and that retention is measured against its own teacher, not a frontier
  model. Nothing installed or measured; kernel-level "no multiplication" claim not verified.
