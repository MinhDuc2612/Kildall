# Unsloth-finetune&train — Unsloth

**Built:** 2026-09-02 · Sample 2 · self-contained
**Source:** [github.com/unslothai/unsloth](https://github.com/unslothai/unsloth) — README and live
GitHub API, both read 2026-09-02.
**Companion:** `Soup-finetune&train.md` (Soup). Both are fine-tuning stacks; they are **not** competitors —
see §7.

**One line:** the largest fine-tuning project in open source — **75,440 stars** — which has quietly
become something else: **a native desktop app that runs *and* trains models**, with first-class
**MLX and macOS** support.

---

## 1. Verified facts

| Field | Value |
|---|---|
| Repo | [`unslothai/unsloth`](https://github.com/unslothai/unsloth) |
| Description | *"Local UI to run and train LLMs and diffusion models. Supports GGUF, MLX, Qwen3.8, Kimi K3, MiniMax-H3, Gemma 4, FLUX and more."* |
| Licence | **Apache-2.0** |
| Stars / forks | **75,440 / 6,850** |
| Open issues | **1,385** |
| Language | Python |
| Created | 2023-11-29 |
| Last push | **2026-09-02** — the day this file was written |
| Archived | No |

**Note the description.** Unsloth began as a fine-tuning *library*. The repo now describes itself as
**"the first desktop app to run and train models."** Anything written about Unsloth as
"a Colab-notebook speedup trick" is describing an earlier product.

---

## 2. The headline claim

> **"Train LLMs, diffusion, TTS, and embedding models 2× faster with 70% less VRAM with no accuracy loss."**

Three parts, and the third is the one that matters. **2× faster with 70% less VRAM is worthless if the
resulting model is worse** — the claim is explicitly *no accuracy loss*. ⚠️ Vendor-stated; the linked
blog benchmarks were **not read for this file**.

**Scope is unusually broad for a fine-tuning stack:** LLMs, **diffusion**, **TTS**, and **embedding**
models — not just text.

---

## 3. Three products, one repo

This is the part most write-ups miss. Unsloth ships in three shapes:

| Product | What it is | Install |
|---|---|---|
| **Unsloth Desktop** | **native app** — recommended path | [`Unsloth-Desktop-MacOS.dmg`](https://github.com/unslothai/unsloth/releases/latest/download/Unsloth-Desktop-MacOS.dmg) |
| **Unsloth Studio** | web UI | `curl -fsSL https://unsloth.ai/install.sh \| sh` |
| **Unsloth Core** | the code-based library | `uv pip install unsloth --torch-backend=auto` |

**There is a signed native macOS `.dmg`.** For the Mac mini M4 in `../UHWmini.md`, that is the lowest-
friction entry point of anything in this vault.

**Other deployment surfaces:** Docker · headless start with password management · **a free Cloudflare
tunnel** that *"serves Unsloth — you can access the link globally (even on your phone!)"* · LAN/HTTPS
access · developer and nightly channels.

---

## 4. Hardware and backend support — the broadest here

> *"Unsloth works on **Windows, Linux, WSL** and **macOS**. We support **Multi GPU setups, NVIDIA, AMD,
> Intel GPUs, CPUs** and the **Vulkan** backend."*

**Compare that to everything else in this folder.** Soup is CUDA-first with Apple Silicon explicitly
under-validated. `KTransformers` is a GPU+RAM design. Unsloth covers **NVIDIA, AMD, Intel, CPU, Vulkan
and macOS**, and lists **MLX** as a supported runtime alongside GGUF.

**MLX support is the decisive fact for a Mac user**, because `../UHWmini.md` establishes MLX as the
correct Apple Silicon runtime.

### Training methods supported

**LoRA · QLoRA · full fine-tuning · pretraining · RL · GRPO · DPO · FP8**

That is a superset of Soup's SFT/DPO/GRPO/KTO on the RL side, and it adds **full fine-tuning and
pretraining** — not just adapter training.

### Export formats

**GGUF · NVFP4 · FP8** — so a model trained here drops straight into the llama.cpp path documented in
`../UHWmini.md`.

---

## 5. The Claude Code integration

From the README's quick-start:

```bash
unsloth start claude --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL
```

**Read that model string.** `unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL` is **exactly the model and quant
`../UHWmini.md` recommends** for a 32 GB-class machine (`UD-Q4_K_XL`, 17.92 GB), from **exactly the
publisher** that file names for dynamic quants.

**So Unsloth ships a one-command path to serve a local model into Claude Code**, using the same
artefacts this vault already settled on independently. That is the single most directly actionable
finding in this file.

⚠️ **Caveat for your 24 GB machine:** `UD-Q4_K_XL` at 17.92 GB against an ~18–19 GB Metal ceiling
leaves essentially **no room for KV cache**. Use `UD-Q3_K_XL` (13.44 GB) instead, or raise the ceiling
via `iogpu.wired_limit_mb` (`../UHWmini.md` §5b). **Do not copy the README's example verbatim on
24 GB.**

---

## 6. Model coverage

Named in the README with dedicated docs pages: **Qwen3.8 · GLM-5.3-Flash · Kimi K3 · MiniMax-H3 ·
DeepSeek-V4 · Gemma 4**, plus FLUX for diffusion.

**Cross-check against `../OrbiOSS.md`:** Qwen3.8, GLM-5.3-Flash, Kimi K3 and DeepSeek-V4 are all
models that document rates at or near the top of the open-weight field. Unsloth is current, not
trailing.

---

## 7. Unsloth vs Soup — different problems

`Soup-finetune&train.md` covers Soup. They are frequently framed as alternatives. They are not.

| | **Soup** | **Unsloth** |
|---|---|---|
| Scale | 4,577 ★ | **75,440 ★** |
| Age | 2026-02 | **2023-11** |
| Core trick | **layer streaming** — 8B in 3.32 GB | **kernel optimisation** — 2× faster, 70% less VRAM |
| Optimises for | **absolute minimum VRAM** | **speed and breadth** |
| Hardware | CUDA-first; Apple Silicon author-acknowledged unvalidated | **NVIDIA, AMD, Intel, CPU, Vulkan, macOS, MLX** |
| Shape | CLI + YAML | **desktop app**, web UI, and library |
| Methods | SFT, DPO, GRPO, KTO | **+ full fine-tuning, pretraining, FP8** |
| Verified floor | **3.32 GB for 8B** — extraordinary | 70% reduction — relative, not absolute |

**Choose Soup** when the constraint is a hard VRAM wall you cannot move — its 3.32 GB result is the
lower bound in this vault, and nothing else approaches it.

**Choose Unsloth** for everything else: it is broader, far more mature, natively supports your
platform, and — decisively for you — **has an MLX path and a macOS app** where Soup has an
acknowledged validation gap.

**For your Mac mini M4: use Unsloth.** Revisit Soup only if you hit a memory wall Unsloth cannot clear.

---

## 8. Honest gaps

- **Not installed, not run, nothing benchmarked.** Every figure is the project's own.
- **"2× faster, 70% less VRAM, no accuracy loss" is vendor-stated.** The linked benchmark blog was not
  read. No independent reproduction was sought — unlike Soup, which publishes its own adversarial
  findings, no equivalent self-critical section was found in Unsloth's README.
- **1,385 open issues** is a lot in absolute terms. It was not assessed whether that reflects scale
  (75K stars) or maintenance strain. Ratio alone does not settle it.
- **MLX support depth is unverified.** The README lists MLX; whether Apple Silicon *training* reaches
  parity with CUDA training was not established, and that is the question that matters for your machine.
- **The Cloudflare tunnel feature exposes a local service publicly.** Convenient, and a real exposure
  surface. Its auth model was not reviewed.
- **No licence complication found** — Apache-2.0, clean.

## 9. Sources

1. [`unslothai/unsloth`](https://github.com/unslothai/unsloth) — primary: README and live GitHub API metadata, 2026-09-02
2. [Unsloth documentation](https://unsloth.ai/docs)
3. [Unsloth training benchmarks](https://unsloth.ai/blog#training) — the 2×/70%/no-accuracy-loss claim; **cited, not read**
4. [Unsloth RL guide](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide)
5. [Unsloth Desktop for macOS (.dmg)](https://github.com/unslothai/unsloth/releases/latest/download/Unsloth-Desktop-MacOS.dmg)

## Change Log

- **2026-09-02** — Created from the repo's README and live GitHub API metadata: **Apache-2.0, 75,440
  stars, 6,850 forks, 1,385 open issues, Python, created 2023-11-29, pushed 2026-09-02**.
  **Principal framing correction recorded:** Unsloth is commonly described as a fine-tuning library,
  but the repo now calls itself **"the first desktop app to run and train models"** and ships a
  **native macOS `.dmg`**, a web UI, and the original code library as three separate products. Any
  description of it as a notebook speedup trick is describing an older product.
  Recorded the headline claim verbatim — **"2× faster with 70% less VRAM with no accuracy loss"** —
  and flagged it as vendor-stated with the linked benchmark blog **cited but not read**. Noted the
  breadth: LLMs, **diffusion, TTS and embedding** models, with **LoRA, QLoRA, full fine-tuning,
  pretraining, RL, GRPO, DPO and FP8**, exporting to **GGUF, NVFP4 and FP8**.
  Established the hardware finding that matters for this vault: Unsloth supports **Windows, Linux,
  WSL, macOS, NVIDIA, AMD, Intel, CPU and Vulkan**, and lists **MLX** alongside GGUF — where
  `Soup-finetune&train.md`'s Soup is CUDA-first with Apple Silicon acknowledged by its own author as
  unvalidated.
  **Most actionable finding:** the README's quick-start is
  `unsloth start claude --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL` — **exactly the model, quant and
  publisher `../UHWmini.md` independently settled on** — giving a one-command path to serve a local
  model into Claude Code. Added the caveat that **`UD-Q4_K_XL` at 17.92 GB leaves no KV-cache room
  against a ~18–19 GB Metal ceiling**, so a 24 GB machine should use `UD-Q3_K_XL` or first raise the
  ceiling per `../UHWmini.md` §5b — the README example should not be copied verbatim.
  Added a Soup comparison concluding they solve different problems: **Soup for a hard VRAM wall**
  (its 3.32 GB 8B result is the lower bound in this vault), **Unsloth for everything else** — and for
  this user's Mac specifically, because of the MLX path and macOS app.
  Gaps recorded: nothing installed or benchmarked; the headline claim is vendor-stated with no
  independent reproduction sought; **no self-critical section was found** in the README, unlike Soup,
  which publishes its own adversarial findings; **MLX *training* parity with CUDA was not
  established**, which is the open question for Apple Silicon; and the Cloudflare tunnel feature
  exposes a local service publicly with its auth model unreviewed.
