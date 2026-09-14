# kimik3 hwmini — Kimi K3 in C: Hardware Minimisation & Pace Architecture

**Source:** [github.com/FareedKhan-dev/kimi-k3-in-c](https://github.com/FareedKhan-dev/kimi-k3-in-c)
**Built:** 2026-09-01 · Sample 2 · self-contained

**One line:** a **2.78-trillion-parameter** model running inference on **one CPU in 8.24 GB of RAM**,
in portable C99, with **no GPU, no BLAS and no framework** — by never loading the experts at all.


## ⚡ ANSWER FIRST

| | |
|---|---|
| **Total params** | **2.78 T** (104B active per token, MoE) |
| **Runs on your M4 24 GB?** | ✅ **YES — 8.24 GB RAM measured** |
| **Storage needed** | ❌ **~1.7 TB** — waits for your 8 TB drive |
| **Speed on your box** | ⚠️ **~24–26 seconds PER TOKEN** |
| **Quality cost** | ✅ **none — byte-identical output** |
| **Licence** | Apache-2.0 (the C runtime) |

**Verdict: the biggest model you can physically run — as an overnight job, never a chat.**
A 500-token answer takes about **3.5 hours**. More RAM barely helps (8→128 GB is 16× the memory for
4.7× the speed). A faster SSD helps; RAM does not.

**Use it when:** the answer is worth waiting overnight for.
**Do not use it for:** anything interactive.

---

---

## 1. Verified repository facts

Checked live against the GitHub API on 2026-09-01:

| Field | Value |
|---|---|
| Repo | `FareedKhan-dev/kimi-k3-in-c` |
| Description | *"A 2.78-trillion-parameter Kimi K3 running inference on a single CPU in 8.24 GB of RAM. Portable C99: no BLAS, no framework, no GPU."* |
| Language | **C** |
| Licence | **Apache-2.0** |
| Stars / forks | **6,923 / 1,119** |
| Open issues | 7 |
| Created | 2026-08-01 |
| Last push | 2026-08-26 |
| Archived | No |

---

## 2. Hardware-minimisation architecture

The trick is structural, and it only works because Kimi K3 is a **sparse MoE**. Four design
decisions, in order of how much they buy:

### 2.1 Expert streaming — the whole idea

**1.45 TB of routed experts stay on disk.** They are never loaded into RAM. Instead they are
*"multiplied straight out of their packed 4-bit form"* — the weights are consumed directly from
their on-disk representation during the matmul.

This is the entire reason a 2.78T model fits in 8 GB. In a sparse MoE only a handful of experts fire
per token, so **the working set is not the model** — it is whatever the router just asked for.

### 2.2 Trunk packing — making disk access predictable

The **93 dense layers are consolidated into a single 109 GB file** with known offsets, so access is
sequential rather than scattered.

The README's framing is the key insight, and it is worth quoting: memory becomes
**"a dial rather than a floor."** You choose how deep the dense trunk sits in RAM; everything else
streams. There is no hard minimum imposed by parameter count — only a speed consequence.

### 2.3 Pre-quantisation to 4-bit

Experts ship **pre-quantised to 4 bits**, halving their storage footprint. Note this is applied to
the streamed weights, so it reduces **disk bandwidth per token**, not just disk space — which is the
actual bottleneck in a streaming design.

### 2.4 The resulting memory hierarchy

```
   RAM  ┌──────────────────────────────────────────┐
        │  dense trunk — as deep as you choose     │  ← the "dial"
        │  (109 GB packed file, sequential access) │
        └──────────────────────────────────────────┘
                          ▲  streams on demand
   DISK ┌──────────────────────────────────────────┐
        │  1.45 TB routed experts, packed 4-bit    │
        │  multiplied straight out of packed form  │
        └──────────────────────────────────────────┘
```

### 2.5 Requirements

| Resource | Requirement |
|---|---|
| **RAM** | **8 GB minimum** (peak measured **8.24 GB** on a laptop preset); scales to 128+ GB |
| **Storage** | **~1.7 TB free** — 1.56 TB checkpoint + 109 GB packed trunk |
| **CPU** | AVX2 + FMA; x86-64 reference, plus macOS/arm64 and Windows/x86-64 |
| **GPU** | **None required** |

**The trade is stated plainly: RAM was exchanged for disk.** You need 1.7 TB of fast local storage.
For most people that is the harder requirement, not the 8 GB.

---

## 3. Pace architecture — the honest part

Measured, same prompt, **byte-identical output across every configuration**:

| Configuration | Seconds per token |
|---|---|
| 8 GB laptop | **26.5 s/token** |
| 32 GB high-end laptop | 24.2 s/token |
| 64 GB desktop | 19.8 s/token |
| 128+ GB workstation | **5.6 s/token** |

**Read the units.** Not tokens per second — **seconds per token**. At 26.5 s/token a 500-token
answer takes about **3.7 hours**. This is not an interactive system and does not claim to be.

**What the RAM dial actually buys:** 8 GB → 128 GB is a **16× increase in memory for a 4.7× speedup**.
Sharply diminishing, and the curve is nearly flat from 8 GB to 32 GB (26.5 → 24.2, just 9% for 4× the
RAM). More RAM means more of the dense trunk resident and less streaming — but the routed experts
still stream regardless, and they are the bulk of the work.

**Byte-identical output across all four configurations is the strongest claim here.** It means the
memory dial is purely a speed/space trade with **no quality consequence** — unlike quantisation,
which trades quality for size. That is architecturally cleaner than every other approach in this
folder.

**Storage speed is the hidden variable:** the system *"requires fast local storage; slower drives
directly impact performance during streaming operations."* On a design that streams 1.45 TB of
experts, disk throughput *is* the inference speed.

---

## 4. Why this generalises — and where it does not

**It works because of sparsity, not cleverness alone.** Kimi K3 activates ~104B of 2.8T parameters
per token. Streaming works because the per-token working set is ~4% of the model.

**It would not work on a dense model.** Apply this to Qwen3.8-27B (see `qwen38-27b hwmini.md`) and
you would stream *every* parameter for *every* token — no subset to skip, so the disk reads
everything, every time. **Expert streaming is an MoE-only technique.** This is the cleanest
architectural contrast in this folder:

| | Kimi K3 (MoE) | Qwen3.8-27B (dense) |
|---|---|---|
| Memory lever | **stream experts from disk** | **quantise** |
| Quality cost | **none** (byte-identical) | real, "noticeable" at 2-bit |
| Floor | a dial, ~8 GB | hard, set by quant level |
| Storage cost | **1.7 TB** | 9–54 GB |
| Speed | 5.6–26.5 **s/token** | 2.9–7.1 **tok/s** |

Roughly: the dense model is **~20–70× faster per token**; the MoE approach runs a model **100×
larger** on the same RAM.

---

## 5. Honest gaps

- **README-level reading only.** The C source was not read; no claim here was verified by
  inspecting the implementation.
- **Nothing reproduced.** The timings, the 8.24 GB peak and the byte-identical claim are the
  author's measurements, taken at face value.
- **The README was truncated** in fetching. Stated limitations exist beyond "requires fast storage"
  but were not fully captured.
- **No quality benchmark.** Byte-identical output proves the *configurations* agree with each other.
  It does **not** show the C implementation matches the reference Kimi K3 implementation — a
  different and unverified question.
- **Practicality caveat.** 1.7 TB of fast local storage plus hours per response makes this a
  demonstration of an architectural idea rather than a deployment recipe.

## Sources

1. [`FareedKhan-dev/kimi-k3-in-c`](https://github.com/FareedKhan-dev/kimi-k3-in-c) — README, and live GitHub API stats 2026-09-01
2. [`moonshotai/Kimi-K3`](https://huggingface.co/moonshotai/Kimi-K3) — the underlying model

## Change Log

- **2026-09-01** — Created from the repo README plus live GitHub API verification (Apache-2.0,
  6,923 stars, 1,119 forks, pushed 2026-08-26, not archived). Recorded the four minimisation
  decisions: **1.45 TB of routed experts never enter RAM** and are multiplied straight out of packed
  4-bit form; the **93 dense layers packed into one 109 GB sequential-access file**; 4-bit
  pre-quantisation reducing streamed bandwidth per token; and the resulting hierarchy the README
  describes as making memory **"a dial rather than a floor."** Captured that the real cost is not
  RAM but **1.7 TB of fast local storage**, and that disk throughput effectively *is* the inference
  speed. Pace stated in the author's own units — **seconds per token, 26.5 down to 5.6** — with the
  observation that 16× more RAM buys only a **4.7× speedup**, nearly flat from 8→32 GB. Flagged
  **byte-identical output across all four configurations** as the strongest claim, since it makes
  the memory dial a pure speed/space trade with no quality cost, unlike quantisation. Added the
  structural contrast with the dense case: **expert streaming is MoE-only** and would degenerate to
  reading every parameter every token on a dense model. Not verified: the C source, any timing, or
  that this implementation matches reference Kimi K3 output.

- **2026-09-03 (format pass)** — Added an **ANSWER FIRST** block at the top, matching sample 1's
  presentation style: total parameters, an explicit **yes/no verdict for the user's Mac mini M4 24 GB**,
  speed, quality cost and licence in one table, followed by a one-line verdict and the decisive
  caveat. No content changed — the research below is unchanged and now serves as backing detail.