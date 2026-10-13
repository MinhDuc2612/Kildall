# Orbiplan — Building Kildall *(formerly Orbi; file names kept, a frozen test fixture references them)*

**v49 · 2026-10-13.** Design locked. **Kildall runs the best open models — pruned, fine-tuned or merged when that measurably helps. Never a paid API.**
Scope locked: **everything Claude Code does, plus image, video and voice.**

**Companion files — read all three:**
`Orbimodels.md` = which models, exact sizes · `Orbichecklist.md` = definition of done ·
this file = how it gets built.

---

# ⚡ ANSWER FIRST

| | |
|---|---|
| **What Orbi is** | a **terminal agent** that picks the best open model per task, runs it locally, remembers everything |
| **Replaces** | **Claude Code, entirely** — files, shell, git, skills, hooks, subagents, MCP |
| **Adds** | **image gen · video gen · 3D · voice in and out** |
| **100% complete** | 🎯 **Kildall is the core of a personal agentic OS** — engine · Obsidian memory · Google Workspace operating layer · local voice · wallpaper dashboard · self-improving skills. **Phase 9** |
| **Whose weights** | open models — Kimi K3, DeepSeek-V4, GLM-5.2, Qwen — **may be pruned, merged or fine-tuned** (rule removed 2026-10-13) |
| **Training** | ✅ **Allowed since 2026-10-13** — LoRA / fine-tuning / distillation from open or local models; **never on Claude/GPT outputs** (their terms forbid it) |
| **Params STORED** | **~9.1 T across 22 models · ~4.84 TB** |
| **Params RUNNING** | **5–8 GB of RAM.** Every lane streams — nothing loads whole |
| **Runs on your M4 24 GB?** | ✅ **yes** — see "stored ≠ running" |
| **Lane A model** | ✅ **Gemma 4 26B-A4B** UD-IQ3_S, `--cache-ram 0` — **29.33 tok/s measured** |
| **Speed, Lane A** | **19.48 tok/s measured** on this M4 (qwen3:8b, 2026-09-06) |
| **Speed, Lane C giants** | **~2.2 s/token (Flash tier) to ~17.9 s/token (Kimi K3)** — varies ~8× by active params |
| **Code lives at** | **`~/Kildall/code`** |
| **Built by** | **you, via Codex (GPT-6 Astra)** — the only builder. **Claude (Opus 5.5)** writes design specs for judgment-heavy phases (4.5, 4C, 9.5, 9.11…) and reviews every slice before merge |
| **Name** | ✅ **Kildall** — renamed from Orbi 2026-09-27 (code `70eb4e8`, repo `MinhDuc2612/Kildall`), after Gary Kildall (CP/M). `orbi` still works as a command alias for one release |
| **Licence** | ✅ **MIT** — Orbi's own code. **Model weights keep their own licences** (see risk 9) |
| **Ready when** | Phases 0–5 and 7–8 run **today**. **Phase 6 parked — drive is 1+ month out** |

---

# 🔑 STORED ≠ RUNNING — THE WHOLE TRICK

**Orbi stores ~9.3 trillion parameters. It never runs 9.3 trillion at once.**

| | Stored | In RAM when active |
|---|---|---|
| **Lane A** — 1 resident router, MoE or dense-converted | 17–90 GB | **~5–8 GB**, streamed |
| **Lane B** — 14 specialists | ~76 GB | **0.35–15 GB**, one at a time |
| **Lane C** — 7 giants | **~4,750 GB** | **~8.2 GB**, streamed |
| **Total** | **~4.84 TB** | **5–8 GB** |

**~4.84 TB of weights, ~8 GB resident. Roughly 1 byte in 600 is in memory at any moment.**

## 🔴 The rule this depends on: **sparse when resident — and dense is convertible**

Sparsity is the entire mechanism. A dense model fires every parameter every token and gets none of
this benefit.

**But a dense model is not disqualified — it is converted.** **CMoE** turns a dense LLM into an MoE
**training-free in under five minutes**, by profiling FFN activations, making the consistently-hot
neurons shared experts and clustering the rest into routed experts.

⚠️ **It is not free.** Training-free at 75% activation is lossless but only **5% faster**; at 25%
activation perplexity rises **33–65%**; one hour of LoRA recovers **~76%** of dense accuracy at 1.5×
lower latency. **And whether CMoE runs on Metal is unverified** — the 5-minute figure is quoted on a
CUDA GPU. Full numbers and limits in `Orbimodels.md` → *When a model is dense — convert it*.

**Order of preference: native MoE → convert a dense one → use dense as-is only if it fits comfortably.**

**Why it works — sparse MoE.** Kimi K3 is 2.78 T params but fires **16 of its 896 experts per token,
about 1.8%**. The sleeping ~93% stays on the SSD and is fetched only when the router asks. Peak RAM
**measured at 8.24 GB**. **More RAM buys speed, never a different answer** — output is byte-identical
from 8 GB to 128 GB.

⚠️ **The one RAM trap:** Lane A at 8 GB **plus** Qwen3-Omni at 15 GB is **23 GB on a 24 GB machine**.
Use the ASR + TTS pair (2.0 GB) for voice instead. Detail in `Orbimodels.md`.

---

# ⚠️ KIMI K3'S 25 s/TOKEN FIGURE — MEASURED, NOT ASSUMED

**This section is about Kimi K3 only.** It is the slowest giant and the source of the plan's original
flat figure. **Lane C as a whole runs ~2.2–17.9 s/token depending on active params** — see
`Orbimodels.md` for the per-model table.

**Source:** the `kimi-k3-in-c` author's own measurements running Kimi K3 (2.78 T), same prompt,
**byte-identical output at every size** (`sample3/kimik3 hwmini.md` §3):

| RAM | Measured |
|---|---|
| 8 GB laptop | **26.5 s/token** |
| **32 GB laptop** | **24.2 s/token** |
| 64 GB desktop | 19.8 s/token |
| 128 GB+ workstation | 5.6 s/token |

**Your 24 GB sits between the 8 GB and 32 GB rows, and that stretch is nearly flat** — 26.5 → 24.2 is
**9% for 4× the RAM**. So **~25 s/token is an interpolation between two measured points**, not a guess.

**Three limits:**
1. **Author-measured**, not independently reproduced.
2. **The reference platform is x86-64.** macOS/arm64 is a supported build, but **no M4 number has ever
   been published.** Phase 6 produces the first.
3. ⚠️ **Yours will be worse.** Lane C is **disk-bound** and the giants live on an **external** drive,
   slower than your measured **3.44 GB/s internal**. Treat ~25 s/token as a **ceiling, not a target.**

**In practice:** a 500-token answer takes **~3.5 hours**. **Lane C is a job you submit and walk away
from. Never a chat.**

---

# THE THREE LANES

| Lane | What | Stored | Speed | Use for |
|---|---|---|---|---|
| **A — Resident** | 1 router, **MoE or dense-converted-to-MoE**. 4 candidates | 4–90 GB | **>15 tok/s — ⚠️ unmeasured** | chat, edits, routing, driving subagents |
| **B — Hot-swap** | 14 specialists: ASR, TTS, OCR, embeddings, guard, translation, grounding, image, video, 3D | ~76 GB | **seconds to load** | one task, then released |
| **C — Giants** | 7 models, Kimi K3 down to DeepSeek-V4-Flash | **~4.75 TB** | **~2.2–17.9 s/token** (see `Orbimodels.md`) | hard questions worth waiting for |

**Rule: Lane A answers unless the task provably needs better.**

## How the router actually decides

**The Lane A model classifies.** One extra small-model call per request, ~0.2 s:

```
request
  └─> Lane A model: "which of the 341 skills is this?"
        └─> skill ──> lane ──> model ──> run
```

**Skill table from `sample1/OrbiLLM/Orbi OSSLLM research.md`** — 341 leaves, each with pick, evidence
and a **min-viable alternative**. **Sample 3 is the authoritative research overall, but this is the one
file sample 1 still wins** — 56 min-viable alternatives against sample 3's 3, and sample 3's own
`OrbiOSS.md` says to use sample 1 for per-skill picks.

**Always prefer the min-viable alternative.** It often moves a skill **from Lane C to Lane B** — the
difference between a Lane C job and an instant answer.

## What you gave up, on record

**The giants cannot be merged into one model.** Different hidden sizes, different tokenizers. Their
weights do not combine — physics, not a missing tool (`sample3/LLMmerge.md`).

**So Orbi is several models behind one interface, not one new model.** In exchange: **their real
quality, at zero training cost.** *(2026-10-13: training and weight changes are now allowed — see "Road to 7/10".)*

---

# BUILD ORDER

**Phases 0–5 and 7–9 run today; Phase 9 comes last. Phase 6 is parked — no drive for 1+ month.**
✅ **253.65 GB free** (Trash emptied 2026-09-06). Both Lane A candidates fit. **Only Lane A is sized against this disk** — it streams every request and needs the measured 3.44 GB/s. Lanes B and C go on the external drive.

| Phase | What | Needs drive? | Exit test |
|---|---|---|---|
| **0** | venv, MLX, baseline | no | ✅ **COMPLETE 2026-09-06.** MLX on GPU, `check.sh` exits 0, commit `d74481c` |
| **1** | CLI, memory, orbs, Lane A chosen | no | ✅ **COMPLETE.** Recall **20/20**, tools **20/20** post-retry. ⚠️ Lane A quant unresolved — see below |
| **2** | Router | no | ✅ **COMPLETE 2026-09-20**, commit `8b815f1`. Routing **19/20**. ⚠️ **15.71 s/decision vs the 0.2 s spec** — open |
| **3** | Permissions, content policy | no | ✅ **COMPLETE 2026-09-21**, commit `a2415b6`. Hard test passed with `SYSTEM_RULES=''` and all system messages omitted. Nuke dry-run: **14,918 paths, 0 outside `code/`**. ⚠️ Guard-model item deferred to Phase 4 |
| **4** | **Agent layer** — files, shell, git, skills, hooks, subagents, MCP, web | no | ✅ **4.1–4.4 complete** (files/shell, git/skills, hooks, subagents; `main` **`3b6b890`**, 4.4 reviewed 2026-10-04). ⏳ **4.5a–d next** (cloud, web + guard, MCP, council — spec below). Exit: completes a multi-file change with tests passing |
| **4C** | **Computer mode** — drive macOS apps and the browser. **Opt-in, attended, never default** | no | fills a form in a real app through the accessibility tree, every action gated by Phase 3 |
| **5** | Media gen *(voice moved to 9.3)* | no | queues an image job end to end |
| **6** | Lane C giants ⏸ **parked, 1+ month** | ⏸ **yes** | an overnight answer beats Lane A — **or cut Lane C** |
| **7** | Improvement loop — eval harness (#13) first, then **hardware auto-fit (#51, v37)** | no | one month unattended finds one upgrade you accept; **auto-fit gate passes** (see #51) |
| **8** | Tool-set redo | no | each swap measurably better, or reverted |
| **9** | 🎯 **Agentic OS — Kildall 100%**, built **last**: Laya reflex · Hermes channels · local voice · Obsidian second brain · activity capture · wallpaper dashboard · skill engineering · Google Workspace · skill packs · profiles | no | you speak, hear the answer, see it on the wallpaper; every listed daily/weekly task is a skill or automation; all earlier gates unchanged |
| **10** | 🔄 **Model refresh — every skill and sub-skill**, the **final step after everything else is complete** | no | every leaf re-picked on current benchmark evidence; every changed model passes its lane gates; no regression |

## Phase 0 — today, one hour

```bash
sudo sysctl iogpu.wired_limit_mb=20480     # YOURS to run. Needs a password. Resets on reboot.
cd ~/Kildall/code
python3.12 -m venv .venv                   # your default python3 is 3.14 — unsupported
source .venv/bin/activate
pip install mlx-lm && pip freeze > requirements.lock
ollama run qwen3:8b --verbose "test"       # write the tok/s down
```

## ⚠️ Two rules that follow from putting the code inside the vault

**1. `kildall nuke` must be scoped to `~/Kildall/code` and nothing else.** The code now lives *inside* the
research vault, so the old rule — "never touches `~/Kildall/`" — is impossible. Replace it with an
allow-list of exactly one path:

| `kildall nuke` may delete | `kildall nuke` must NEVER touch |
|---|---|
| `~/Kildall/code/` **only** | `~/Kildall/Researchhub/` · `Orbiplan.md` · `Orbimodels.md` · `Orbichecklist.md` · `CLAUDE.md` · `Logo.png` · `Klogo.png` · `.obsidian/` |

**Test it before trusting it:** dry-run must list only paths under `~/Kildall/code/`. If it lists
anything else, the guard is wrong. **This is the single most dangerous command in the project.**

**2. Exclude `code/` from Obsidian.** `~/Kildall` is an Obsidian vault. A Python project puts tens of
thousands of files in `.venv/`, and Obsidian will try to index all of them. Add `code/` to
Settings → Files & Links → Excluded files.

⚠️ **Never use `~/kildall` (lowercase).** Your volume is **case-insensitive** — verified — so `~/kildall`
and `~/Kildall` are **the same directory**.

## Phase 1 — CLI, memory, orbs, and the Lane A decision

- **Memory** (`sample3/LLMDB.md`): SQLite L0–L3 · BM25 + vector · **hard caps 12 items / 4,000 chars /
  300 ms** — the caps are what stop memory eating your context
- **Two layers: global** (facts about you, everywhere) **and per-project** (scoped to the directory)
- **Backups**: nightly, 14 days, markdown mirror, outside the code directory
- **Orbs**: `○` idle `◐` thinking `◓` tool `◒` waiting `●` done `◉` error `◌` stalled. Survive a crash.
  Auto-off when piped
- **Lane A — measured 2026-09-09, not yet locked.**
  - ❌ **Qwen3.8-Flash-Next: 0.21 tok/s.** Catastrophic. **Settles the plan's biggest open question —
    mmap-paging a 180B/6B MoE on an M4 does not work.** Do not retry it.
  - ⚠️ **Gemma 4 26B-A4B @ IQ3_S: 29.33 tok/s**, routing 20/20, callable JSON 20/20, **exact arguments
    18/20**, peak RAM 12.23 GB. Passes the gates but **18/20 is the weakness `Orbimodels.md` predicted**
    — and IQ3_S is ~3-bit, below the DWQ 4-bit the model-load procedure requires.
  - ⏳ **Untested: Granite 4.1 8B** (best tool calling <10B) and **Qwen3.8-27B + CMoE** (Metal support
    unverified). **Re-test both at DWQ 4-bit before locking Lane A.**
  - **Rank on exact-argument accuracy, then tok/s.** Above 15 tok/s is fast enough; Lane A emits tool
    calls on every request and drives subagents, so correctness beats speed.
  - 🔑 **Try grammar-constrained decoding before blaming the model.** llama.cpp supports **GBNF
    grammars** — hand it the tool's JSON schema and the model becomes *incapable* of emitting anything
    that does not match. **18/20 → 20/20 without changing models.** Cheapest quality win available, and
    it applies to whichever candidate wins.

### 🔮 Future-proofing — cheap now, expensive to retrofit

Leave **schema room in the memory tables for a `decay` / `last_used` field and a `consolidated` tier.**
Do not build either. Adding the columns later means migrating live memory; adding them now is free.
See *Beyond the plan* below.

## Phase 2 — the router *(the core of Orbi)*

```bash
orbi ask "..."              # router picks the lane
orbi ask --lane a "..."     # force fast
orbi job submit "..."       # force Lane C, come back later
```

**The Lane A model classifies** each request into one of the 341 skills in
`sample1/OrbiLLM/Orbi OSSLLM research.md`, then skill → lane → model. ~0.2 s per request.
**Always prefer that file's min-viable alternative** — it often moves a skill from Lane C to Lane B,
which is the difference between a Lane C job and an instant answer.

**Exit:** 20 varied requests route correctly **18+ times**.

### 🔮 Future-proofing — cheap now, expensive to retrofit

**Log every routing decision as `task → skill → lane → model → succeeded?`.** Do not build any
learning on top of it. Just record it. **Only 46 of the 302 researched leaves were benchmark-verified**
— the rest are reasoned defaults, and this log is the only thing that can ever verify them. Start it
now or start from zero later. See *Beyond the plan* below.

## ⚠️ Open against Phase 1 — Lane A runs 3-bit, the procedure requires 4-bit

**The model-load procedure above requires DWQ 4-bit. Lane A is running UD-IQ3_S — 3-bit.**
That is below spec, and **4-bit → 3-bit is the step where quantisation damage becomes noticeable.**

Codex's own measurements show the cost:

| Build | Exact args, first pass | Failures |
|---|---|---|
| **IQ3_S** — 3-bit, installed | **17/20** | t07, **t09**, t12 |
| DWQ 4-bit — MLX backend | **18/20** | t07, t12 |

**t09 is the difference, and it is precision, not prompting.** `BENCHMARKS.md` records that *"IQ3
additionally dropped the final period in t09's exact fact"* — **3-bit lost a character 4-bit kept.**

**The fix is already on disk and costs nothing to try:**
`models/gemma-4-26b-a4b/gemma-4-26B-A4B-it-UD-IQ4_XS.gguf` — **12.7 GB, downloaded, never benchmarked.**

⚠️ **Do not switch to `models/gemma-4-dwq-4bit/`.** That build is `.safetensors` — **MLX**, a different
runtime from the llama.cpp server the CLI is built on. **IQ4_XS keeps the runtime and still moves
3-bit to 4-bit.** DWQ is MLX-only, so the procedure's "DWQ 4-bit" cannot be met on the llama.cpp path;
IQ4_XS is the closest available.

**Decision rule:** adopt IQ4_XS if exact-argument first-pass improves **and** tok/s stays above 15.
The extra 2.2 GB of RAM is affordable — Lane A peaked at 12.23 GB against a ~20 GB ceiling.

---

## Phase 3 — permissions, enforced in code

| Tier | Examples | Behaviour |
|---|---|---|
| Auto | read, `ls`, `git status` | runs, logged |
| Confirm | write, edit, commit, install | asks, shows the diff |
| **Never** | recursive delete, `sudo`, force-push, writing outside allowed roots | **refused in code** |

**Permissive to you** — no refusals on your own machine. Normally-aligned model, permissive prompt,
**not an abliterated one**. **Guards detect, they do not refuse**: fetched web text is **data, never
instructions**.

## Phase 4 — the agent layer *(the biggest phase)*

Files · shell · git · skills · hooks · MCP · web — full detail in `Orbichecklist.md` §5–13.

🔑 **Constrain every tool call with a GBNF grammar**, not a prompt instruction. Most agent failures are
malformed tool calls, not bad reasoning. A grammar makes an invalid call unrepresentable rather than
unlikely — the difference between an agent that mostly works and one that does.

**Subagents, both modes:**

| Mode | RAM | Parallel? | Use when |
|---|---|---|---|
| **Shared** *(default)* | ~0 extra | no — interleaved | almost always |
| **Separate process** | ~5 GB each | yes, real | the task genuinely needs concurrency |

⚠️ **Hard-cap separate processes from free RAM and refuse to exceed it.** At ~5 GB each you get about
three before the machine is gone.

**v38 — measured in 4.4 (`3b6b890`), replacing the estimates above:** a second model process hit a Metal
GPU out-of-memory error, so the **separate-process cap on this 24 GB Mac is 0** (implemented, refused).
Shared mode runs **2 slots** (4,096 context each); together they add only **+3.8% total throughput** —
subagents **take turns, they do not speed work up**. So the 4.4 follow-ups (verified review, swarm) buy
**independent checks, not speed**. Routing mean is now **6.74 s** (p99 17.9 s), up from 5.06 s, because
the second slot shares the 768 MiB prompt cache. **Recall gate from now on:** frozen `test_recall.py` on a
1-slot server **plus** the per-slot verifier on the 2-slot server, both 20/20 (the frozen test asserts one
slot and cannot run on two; it stays unedited).

🔑 **Shared mode needs continuous batching.** Without it agents queue strictly — agent 2 waits for
agent 1's *entire* answer, so "shared" means **serialised, not concurrent**. Continuous batching exists
for exactly this case: N requests against one model, arriving at different times with different
lengths, none blocking the others.

llama.cpp exposes it via `-np <slots>`. **Size slots by the RAM each slot's KV cache needs, not by how
many agents you want** — every slot carries its own cache. **Measure p99 latency, not throughput:**
batching raises total tokens/second while making any *single* answer slower, and Lane A also serves
the interactive path where one slow answer is felt immediately.

*Not needed before Phase 4.* Lanes A, B and C serve one request at a time, and batching does nothing
for a single sequential user.

**Cloud policy:** Orbi uses cloud **when necessary, without asking**. It rotates the **16 free-tier
providers in `sample3/Cloudcall/`** in order, and when all are exhausted **falls back to local and says
so**. **It never spends money** — the budget cap stays at 0.

**Added v35 — features adopted from `Researchhub/sample3/6aifeatures.md`** (paid products re-built as
Kildall patterns; internals of closed products are not public, so Kildall copies the pattern, not the code):

- **Verified review (the Ultrareview pattern) — a 4.4 follow-up slice.** Parallel reviewer subagents; **every
  finding is reproduced before it is reported**, same 2-of-3 rule the research harness uses. Starts after 4.4
  merges — never added mid-slice. Only a few reviewers fit in 24 GB, not a fleet.
- **Model Council — in 4.5, judged in Phase 7.** Lane A plus 2–3 free-tier cloud models (the 4.5 rotation)
  answer; a local chair **shows where they agree and differ**. `karpathy/llm-council` has **no licence** — copy
  the three-stage pattern, not the code. A local-only council runs members one after another (slow). **Gate
  (Phase 7 eval harness, #13): the council is kept only if it beats Lane A alone on the frozen fixtures.**
- **Swarm orchestration (the Kimi Agent Swarm pattern) — a 4.4 follow-up slice, after 4.4 merges; never added to the running 4.4.** Kildall's own orchestrator splits a task
  across a few Lane A subagents (capped by free RAM) and sends only the hardest step to Lane C overnight.
  🔴 **Kimi's 300-agent runtime is Moonshot's closed service; no downloadable model includes it.**
  **`moonshotai/Kimi-K2.6`** (1.03 T / 32 B active, modified MIT, ~515 GB, ~5.5 s/token by arithmetic) is
  **recorded for later, not added** — it is older than K3, so it needs benchmark evidence as a min-viable pick.
  **Revisit if** the orchestrator needs a Kimi-family worker faster than K3, or a benchmark shows it winning a leaf.

## Queued small slices *(v41 · 2026-10-07)*

Codex order, one PR each, each holding every standing gate; Codex stops at the PR. Order changes only on your word.
1. **4.5a** keys + cloud (in progress) → 2. **routing fix** → 3. **router warmth** (#62 save router prompt to disk,
#63 idle re-warm) → 4. **ops hardening** (#52 wired-limit boot daemon — you install it with sudo; #53 permanent
backup agent; #55 secret-scanner hook; #54 off-machine backup once `KildallC` is mounted) → 5. **long context** →
5b. **platform layer** (v43: Mac-only parts behind one interface; no behaviour change) →
5c. **NVIDIA NIM provider** (v47; key verified live) → 5d. **coding core** (v47: #89 test-driven fix loop, #88 repo map,
#90 LoRA data collection) → **test #3** →
6. **4.5b–4.5e** → 7. **quality slice** (#57 copy by reference — first-pass must rise with frozen fixtures
untouched; #58 code-built delegation prompts — the exact-once smoke must pass) → 8. **Gemma vision** (#59, RAM
measured, before 4C) → 9. **4C** → Phases 5, 7, 8, 9.

## Cross-platform *(v43 · 2026-10-12, user picked option 1)*

**Goal:** Kildall runs on **macOS, Linux (any mainstream systemd distro — tested on Fedora and Ubuntu LTS) and
Windows (through WSL2; native only if computer mode on Windows apps is needed).** Lane A's llama.cpp already runs
on all three (Metal / CUDA / ROCm / Vulkan / CPU); ~90% of the code is portable Python.
1. **Platform layer — right after the long-context slice.** Each Mac-only part goes behind one interface with the
   current Mac code as its first implementation: **keys** (Keychain → `keyring`: Secret Service / Credential
   Manager), **scheduled jobs** (launchd → systemd user timers / Task Scheduler), **shell sandbox** (macOS sandbox
   → bubblewrap/Landlock), **OCR** (Vision → Tesseract or PaddleOCR), **computer mode** (AX → AT-SPI / UI
   Automation), **memory probe** (`iogpu` is Mac-only). **Gate: zero behaviour change on the Mac — every standing
   gate identical.**
2. **Linux, then Windows via WSL2 — before the first paid client.** Each OS re-passes **every** gate on real
   hardware, **above all the Phase 3 sandbox hard tests**. Settings (model size, slots, context) are re-tuned per
   machine by #51 auto-fit.
⚠️ **Needs a Linux or Windows PC with an NVIDIA GPU for the model gates** (GitHub runners cover code-only tests,
#72). Not yet confirmed that one exists. An NVIDIA PC may read prompts far faster than this M4 (~85 tok/s).

## Road to 7/10 *(v44 · 2026-10-12 · starts only once a 128 GB machine exists)*

**Honest score today, if every phase were finished: ~3/10 as a Claude Code replacement** (Claude review, user asked
for "ruthless"). **A 10 is not reachable locally at $0** — closed frontier models stay ahead of open ones; only
paid frontier APIs would close it, which breaks the $0 rule. **A 7 is realistic** with all four of these:
1. **A 128 GB machine — DECIDED 2026-10-13: GMKtec EVO-X2 mini PC (AMD Ryzen AI Max+ 395, 128 GB unified, 256 GB/s),
   the 128 GB/4 TB version + a second 4 TB NVMe = 8 TB inside; bought once the project succeeds.** Linux (distro picked
   in the port slice by AMD GPU support evidence). **So the platform layer + Linux port are now REQUIRED, not optional,
   and must be done before the machine arrives.** Earlier candidates (2026-10-12, VN prices): AMD Ryzen AI Max+ 395 mini PC 128 GB (~$3,650 + import;
   Claude's pick), a desktop with 2 used RTX 3090s (~120–145M), or a Mac Studio M5 Max 128 GB (140.99M; no port
   needed). User wants **8 TB built in** — no Mac with 8 TB fits the budget; the 8 TB NVMe price (22M–83M seen) decides.
   **A non-Mac machine needs the Linux port (cross-platform section) before Kildall runs on it.**
2. ⚠️ **Re-check before buying (2026-10-13):** HF API puts V4-Flash-0731 at **304 B** → ~114 GB (≈106 GiB) at 3-bit. ✅ **Research 2026-10-13: on Linux the AMD GPU can use ~120 GiB** once `amdgpu.gttsize=131072 ttm.pages_limit=31457280` are set (default is only half the RAM; newer kernels may need the `amdttm.` prefix; 96 GB is the Windows limit) — so it **fits, tightly** (~10 GiB left for context + OS). Measured on this chip (llama.cpp Vulkan, community): gpt-oss-120b 55–60 tok/s writing / ~460–490 tok/s reading; Qwen3.6-35B-A3B ~63 / ~1,000; effective ~155–170 GB/s of 256 → the 7/10 model ≈ **20–30 tok/s writing, ~200 tok/s reading** (estimate); the newer **DeepSeek-V4.1-Flash is 763 B** (cloud/Lane C only, free on NVIDIA NIM). Pruning (now allowed) or a lower bit-width remain options if context needs more room — measured. Original line: **A strong open coding model held fully in memory** — e.g. **DeepSeek-V4-Flash** (79.0% SWE-bench Verified, in
   Lane C today) at ~3-bit ≈ 107 GB. ⚠️ Fit, speed and 3-bit quality loss are **unmeasured**; gate them like any
   Lane A candidate (speed, routing, tools, 10-min soak).
3. **Context ≥ 64K** per answer slot (the long-context slice, re-run on the new machine).
4. **Core proven:** test #3 (unassisted multi-file refactor, tests passing) and test #1 (one week without Claude
   Code) pass. **No new features until then.**
**Pre-purchase checks (v48, 2026-10-13 — both before spending the 125–130M):**
- **A. Prove the big model on your tasks first:** run test #3 through Kildall using NVIDIA NIM's free DeepSeek-V4.1-Flash / Kimi K3 (needs the NVIDIA provider + coding core slices). If it fails, the 7/10 premise is wrong — rethink before buying.
- **B. GPU memory limit — DONE (research above):** ~120 GiB usable on Linux with the GTT/TTM settings; the Linux port must apply and verify them (dmesg GTT size, `/sys/module/ttm/parameters/pages_limit`).
**Extra levers now allowed (2026-10-13, user removed three rules; paid APIs stay banned forever):**
- **Expert pruning** of big MoE models (REAP-style) so a stronger model fits 128 GB — measure the quality loss first.
- **Fine-tuning** (LoRA) on your own repos and accepted answers (#42 pairs) — from open/local model outputs only.
- **Speculative decoding** measured per platform — e.g. DeepSeek's built-in MTP draft head on the AMD mini PC.
- **Better hardware** may be proposed when it measurably raises the score.
**Target 8/10 (written 2026-10-13):** everything above, plus open models catching up (#84 model-update watcher swaps them in), the free-cloud council for the hardest tasks (4.5d — **you add a free OpenRouter key, no card**), and skills built from your own work (9.7). 9–10 is not reachable locally at $0.

## Long-context slice *(v40 · 2026-10-07 · after the routing fix)*

**User decision: raise the per-slot context now (option 1); a faster Mac later (option 5).** Runs after the
routing-fix slice, because that slice sets the slot count and every slot's window multiplies KV memory.
- ⚠️ **After PR #5 (3 slots: router 0, work 1–2) memory is already tight: soak 18 normal / 103 warning / 0 critical,
  peak RSS 13.21 GB, GPU allocated 15.63 GB.** llama-server gives every slot the same window, so first verify in
  b10809 whether **unified KV** lets the router slot use only what it needs; otherwise 16K × 3 slots reserves
  router memory for nothing. **Extra gate: warning samples must not exceed the PR #5 soak (103/121).**
- **Steps:** 4,096 → **16,384 per slot first**; **32,768 only if 16K passes every gate**. Q8 KV stays. Read the
  model card for Gemma 4 26B-A4B's real maximum first — never guess it.
- **Measure:** KV/RSS/GPU per slot (4,096 measured 175.31 MiB Q8 KV); prefill tok/s and wall time for 8K/16K/32K
  prompts (~85 tok/s measured → **32K ≈ 6 min to read**); a ≥600 s soak with real children, **0 critical, 0 GPU OOM**.
- **Behaviour:** long prompts show progress and an estimated read time; the limit stays configurable.
- **Every 4,096-token assumption becomes config-driven** — 4.5c MCP tool cap, 4.5d council caps, 4.5e chunk size.
- **Gates:** all standing gates hold; routing mean ≤ the routing-fix result + 10%; interactive p99 ≤ the routing-fix
  baseline + 10%; memory retrieval caps (12 items / 4,000 chars / 300 ms) unchanged.
- **Context follow-up slice (v45 · after this slice merges; never added to it mid-slice).** Long context scores
  1/10 — the cheapest points on the road to 7–8:
  1. **KV cache at 4-bit** (`-ctk q4_0 -ctv q4_0`) — ~2× context; gate on recall/tools/routing with no drop.
  2. **Document KV saved to disk** — a big file read once is reloaded in seconds when asked about again (the
     #62 mechanism, keyed by file hash + model + flags; never contains other users' text).
  3. **Retrieval (RAG) for big files** — chunk + Harrier embeddings; only relevant parts enter the prompt, inside
     the 12 items / 4,000 chars / 300 ms caps (raise only with measured evidence).
  4. **Map-reduce** — subagents summarise 4K–16K pieces on the work slots, then one combines; for whole-document
     summaries. Accuracy gate: a fixed long-document test set with known answers.
  5. **On the 128 GB machine:** target **≥ 128K** with a compact-attention model (DeepSeek-style); measure KV per
     token first — unmeasured today.
- **Later (option 5):** a faster Mac — the 2026-10-04 answer recommended an M5 Max 40-core GPU, 64 GB (614 GB/s,
  ≈5× this M4's 120 GB/s) — raises prefill and decode together. Not scheduled; user decision for later.

## Phase 4.5 — design spec *(v38 · Claude · 2026-10-04)* — cloud, web, guard, MCP, council

**Five sub-slices, one PR each. Codex opens the PR and stops; Claude reviews; merge only on your word.**
**4.5a** keys + cloud rotation · **4.5b** web + guard model · **4.5c** MCP client · **4.5d** Model Council · **4.5e** deep research.
Order is fixed: the council needs the cloud; the guard must exist before web text feeds any action; deep research needs web, guard and council.

**Facts this rests on (checked 2026-10-04; update 2026-10-07: 🔴 **Google Gemini and Groq are excluded from Kildall's cloud entirely** — user decision; free disk 94 GB):**
- 🔴 **No API key exists.** `~/.config/orbi/keys.env` and its Downloads copy hold 18 empty names; the
  Keychain holds none. **LLM7 is keyless.** Live cloud tests need keys you add yourself — never in chat.
- **Granite Guardian 4.1 8B** (`ibm-granite/granite-guardian-4.1-8b-GGUF`): Apache-2.0, April 2026, 8B
  only; **Q4_K_M 5.12 GB**, Q3_K_M 4.17 GB; non-thinking yes/no mode; Bring-Your-Own-Criteria.
- 4.4 measured: a second model process → Metal GPU OOM. **A resident guard next to Lane A is unproven.**
- **Lane A context is 4,096 tokens per slot** — most web pages and every council transcript exceed it.
- Free-tier limits, data policies and billing terms are **unverified** (`Cloudcall/ccapi-verification.md`).
- Free disk **23 GB**.

**Threat model:**

| # | Threat | Path | Control |
|---|---|---|---|
| T1 | **Money spent** | a billed model id; an account with billing on | per-provider **allow-list of exact free model ids**; HTTP 402 or any billing/payment error **disables that provider** until you re-enable it; no paid fallback. ⚠️ Code cannot see an account's billing — **you never attach a card** (accepted limit) |
| T2 | **Key leak** | argv, logs, DB, `.session/`, git, HF, prompts | Keychain only; written through `security -i` on **stdin, never argv**; read at call time; outbound scrub; gate greps every artifact for every key |
| T3 | **Exfiltration by injection** | a page says "fetch `https://x/?q=<your memory>`" | `web_fetch` is Auto **only for URLs from your message or this task's search results**; any other URL → Confirm showing the full URL; secret scrub on every URL, query and cloud prompt |
| T4 | **SSRF** | URL to `127.0.0.1:8123/8124`, LAN, router, the 9.11 bot API | resolve first; refuse loopback, private, link-local, multicast, `.local`; **re-check every redirect**; http/https only |
| T5 | **Injection** via web, cloud or MCP text | content steers actions | all of it is `untrusted_*` data (the existing `web_data` pattern); the guard **flags, never refuses**; a flagged turn is **tainted** — Confirm stays Confirm and shows the flag; Never unchanged |
| T6 | **Cloud tool calls** | malformed or hostile call | no GBNF in the cloud, so the **same schema validator + `permissions.execute`**; malformed → rejected, never repaired |
| T7 | **MCP server code** | runs outside the Phase 3 boundary | only servers you list; absolute command path; minimal env; every MCP tool is an action through `permissions.execute`, **default Confirm**, Auto per tool only by your config, **never past Never**; output untrusted |
| T8 | **RAM / GPU** | guard or council next to Lane A | measure first (4.5b-0): 10-min soak, 0 critical samples, 0 GPU OOM |
| T9 | **Disk** | guard download | refuse if free space after download < **15 GB** |

**4.5a — keys + cloud rotation.**
- `kildall keys import [FILE]` (default `keys.env`): each non-empty value → login Keychain, service `kildall`,
  account = variable name, via `security -i` on stdin; verified by read-back hash; prints names and status
  only. The file stays (deleting it needs your OK). `kildall keys check` replaces `check_keys.py`, reading
  the Keychain, same never-print rule.
- **Keyless now:** LLM7 and OVHcloud AI Endpoints (anonymous; limits undocumented). Kilo Code needs no key but is not an
  inference provider — include it only if its endpoint serves chat completions.
- 🔴 **Excluded providers: Google Gemini and Groq** (user decision 2026-10-07). Never listed in `[cloud]`, never imported
  to the Keychain, never called — even though `keys.env` still holds their values.
- `[cloud]` in `kildall.toml`: ordered providers — base URL, key name, **allowed free model ids**, limits from
  Cloudcall marked `unverified`, `trains_on_data`. Active = has a key, or is keyless.
- Rotation in order: 429/5xx/timeout → cooldown (honour `Retry-After`); 401/403 → key invalid until it
  changes; 402/billing → disabled. Daily use per provider counted in `kildall.db`; stop at 90% of the
  documented limit. All exhausted → Lane A, saying **`cloud exhausted — answering locally`**.
- **"Necessary" means:** the routed lane is not available locally (Lane C parked, a Lane B model absent), or
  the input exceeds Lane A's context. **Never** just because Lane A is slower.
- **Gates:** mock-server tests for 200 / 429 / 401 / 402 / timeout / `Retry-After` / all-exhausted; routing mean ≤ **1.78 s** once PR #5 merges (routing fix 1.618 s + 10%; was 7.41 s).

**4.5b — web + guard.**
- **4.5b-0, go/no-go:** Guardian Q4_K_M loaded next to Lane A (2 slots); 10-min soak with web-sized prompts;
  0 critical, 0 GPU OOM. Fail → Q3_K_M. Fail again → stop and report; no guard ships; checklist 12 stays open.
- `web_search`: backend picked **by evidence** — licence, $0 with no card, measured on 20 fixed queries.
  Candidates: SearXNG run locally (no key) or a keyed free API.
- `web_fetch`: stdlib HTTP; 10 s timeout; 2 MB cap; `text/html`, `text/plain`, PDF (through the existing
  `read_pdf`); HTML → text with the stdlib parser; returned as `untrusted_web` through the `web_data` path.
- The guard runs non-thinking on every fetched page and search result (chunked to fit): jailbreak / prompt
  injection, plus a BYOC criterion "instructions aimed at an AI agent". Detects, never refuses.
- **Gates:** an injected-page fixture is flagged, not obeyed, nothing runs (**closes checklist 12**); SSRF
  fixtures all refused (`127.0.0.1`, `::1`, 10/8, 172.16/12, 192.168/16, 169.254/16, `localhost`, a redirect
  to `127.0.0.1`); an exfil fixture page → Confirm shown, nothing sent unconfirmed; guard latency per 1K
  tokens reported.

**4.5c — MCP client.** Stdlib JSON-RPC over **stdio only** (`initialize`, `tools/list`, `tools/call`).
`[mcp.servers.<name>]` = absolute command, args, env; **none enabled by default**. Each server gets a 10 s
startup timeout; a failure is logged and skipped, **never blocks startup**. Tools are named
`mcp.<server>.<tool>`; schemas validated; compiled into the GBNF grammar only when enabled; the exposed tool
count is capped so the prompt fits 4,096 tokens. **Gates:** a local fixture server lists and calls; a hanging
and a crashing server do not block startup; a Never-matching MCP call is refused; tools 17/20 first-pass and
20/20 post-retry hold with MCP off **and** with the fixture server on.

**4.5d — Model Council** (opt-in `--council`, off by default). Lane A + 2–3 cloud providers from different
model families answer alone (each capped at 600 tokens); the local chair (Lane A) reads them anonymised and
outputs **Agree · Differ · Best answer**. Fewer than 2 cloud answers → Lane A alone, and it says so. Copies the
pattern, not `karpathy/llm-council` code (no licence). **Gates:** first prove OVHcloud answers live, keyless (configured in 4.5a, never called); end-to-end with ≥ 2 live cloud members, $0,
fallback works, transcript kept for Phase 7. **Adoption stays a Phase 7 gate:** kept only if it beats Lane A on
the eval harness (#13).

**4.5e — Deep research** *(added v39, user: "add the single feature")*. `kildall research "<question>"` — a
**queued job** (Lane C job machinery), never blocks the terminal. Uses 4.5b web + guard, 4.5d council members as
voters, 4.4 subagents for parallel fetch/verify. Same pipeline Claude's `/deep-research` uses:
1. **Scope** — split the question into 3–5 search angles.
2. **Search + fetch** — `web_search` per angle; dedupe URLs; fetch the top N (default 12) via `web_fetch`; the guard
   scans every page; all text stays `untrusted_web`.
3. **Extract** falsifiable claims, each with source URL + exact quote (pages chunked to fit 4,096 tokens).
4. **Verify** each claim with **3 independent votes** (Lane A + cloud council members when available); **2 of 3
   refutes kill it**; a vote that failed (quota, timeout, error) counts as **unverified — never as a pass**.
5. **Synthesize** — merge duplicates, rank by confidence, cite every claim; refuted and unverified claims and
   coverage gaps listed separately.
Output: a Markdown report in the vault `outputs/` once 9.4 exists; until then a git-ignored folder under `code/`.
Per-run caps on angles, fetches and cloud calls; the T1 $0 rule applies. **Gates:** 5 fixed questions with known
answers — every final claim has a reachable source URL + quote; a planted false claim is refuted; a quota-failure
fixture yields "unverified", never merged; an injected page is flagged and its instructions not followed; $0 spent;
report written. Deep research ≠ more context — it reads many pages in 4K chunks.

**Every 4.5 sub-slice also holds every standing gate** (recall per the v38 rule above, abstention, category,
lane, callable JSON, tools, CLI, hooks, nuke dry-run, `check.sh`) and keeps failed runs in `BENCHMARKS.md`.
⏸ **No `kildall-hf-sync`** — the Hugging Face mirror is paused (2026-10-05).

## Phase 4C — computer mode *(opt-in, attended, never default)*

**Full research: `Researchhub/sample3/Orbicomputer.md`.** Read it before building — its §4 decides
the shape of this phase.

**Two layers, not one choice. Build A first; A costs nothing.**

| Layer | How it sees the screen | Vision model | Extra RAM | Knows what it is clicking |
|---|---|---|---|---|
| **A — accessibility tree** | `AXUIElement` — a structured tree of every UI element | **no** | **0 GB** | **yes, before acting** |
| **B — pixel vision** | screenshot → click coordinates | yes | ~4–8 GB | **no** |

**macOS hands you a structured tree of every button, field and menu. That is text, and Lane A already
reads text.** Layer B exists only for the blind spots — canvas apps, games, remote desktop windows,
custom-drawn UIs, images.

```
try the accessibility tree
   ↓ empty or unusable?
fall through to pixel vision, LOG it, and force Confirm
```

🔴 **This phase is governed by a security finding, not a capability one.** Measured prompt-injection
success against computer-use agents reaches **51%, and 100% against browser-use agents**.
**System-prompt defences do not measurably help, and layered defences are still insufficient** —
the root cause is architectural: the prompt is built with **no trust boundary between the user's
instructions and page content.** A better model does not fix it.

⚠️ **The accessibility tree is auditable but still injectable** — a page can hide instructions in
`aria-label` attributes that the snapshot passes faithfully to the model. Layer A's real advantage is
that Orbi can **check what it is about to click**, not that it is safe.

**Seven non-negotiables:**

1. **Opt-in, off by default.** Not a capability Orbi has until asked.
2. **Never unattended.** Autonomous GUI control is indefensible at today's injection rates.
3. **Every action clears the Phase 3 tiers *before* the event is synthesised**, never after.
4. **Screen and page content is data, never instructions** — the Phase 3 rule extended to the
   accessibility tree and to OCR'd screenshots. Both are proven injection surfaces.
5. **Application allow-list.** Orbi drives only apps the user named.
6. **The pixel path always requires Confirm.** It cannot name its target.
7. **Log every action** with its path, target element and outcome.

**Tools — verified 2026-09-21, not from search summaries:**

| Need | Use | Why |
|---|---|---|
| Browser | **`microsoft/playwright-mcp`** | Apache-2.0, 37,435★, accessibility snapshot not screenshots |
| macOS apps | **`openclaw/Peekaboo`** | MIT, 5,193★, pushed 2026-09-21, hybrid a11y + capture |
| Lighter macOS | `CursorTouch/macOS-MCP` | MIT, 185★, AX API + AppleScript, no VLM |

🔴 **Rejected: `hanzili/comet-mcp`**, despite being the example that prompted this phase. It is a
**delegation bridge to Perplexity Comet, a proprietary cloud browser** — every action runs on
Perplexity's hosted AI, with no local fallback. It also **last shipped 2026-01-13**. The delegation
*pattern* is worth studying; the implementation violates local-first and never-spend.
🔴 **Also rejected: `CursorTouch/macOS-use` — no licence file at all.** Not the same repo as
`macOS-MCP`. ⚠️ **`macOS26/Agent` reports `NOASSERTION`** — resolve its licence before considering it.

**Sub-phases:**

| | What | Depends on |
|---|---|---|
| **CU-0** | **Measure first — the go/no-go.** Can Lane A's **4 B active** params drive an accessibility tree at all? ⚠️ Unknown, and **BrowserOS excludes local models from agent mode entirely**, one practitioner putting the tool-calling floor above 7 B | Phase 3 |
| **CU-1** | Layer A for macOS — AX tree, Phase 3 tiers, app allow-list, logging | CU-0 |
| **CU-2** | Layer A for the browser — `playwright-mcp` accessibility snapshot | CU-1 |
| **CU-3** | Layer B — fallback grounder, Confirm-gated | CU-2 + RAM that does not exist yet |

🔑 **Layer B does not want a big model.** Scaffold beats scale here: a **Qwen 3B with a better prompt
scored ~50% on Showdown-Clicks against ~20% for Qwen 72B**, and small fine-tuned grounders hit
**70–80%** where large general models manage **~20%**. **`BrowserVLM` is 0.54 B and ships GGUF with a
llama.cpp fork.** ⚠️ So the **27B dense and 122B computer-use picks in the model list are the wrong
shape** — and `Orbimodels.md` should be re-checked against `Orbicomputer.md` §3 before CU-3.

⚠️ **CU-3's precondition is unmet.** Lane A alone already runs **96 of 121 memory-pressure samples in
warning**. A resident vision model is not affordable today.

**Added v35 — each bot's own computer (for Kildall Bots, 9.11).** Research before 4C builds: give each bot
a **separate macOS user account or a lightweight VM**, never your own desktop session. Licences of the VM
tools must be checked first. Grok Bot shares one computer and one permission set across bots — Kildall must not.
**v36 — the default (user confirmed 2026-10-02):** each bot's computer is **virtual, on this one Mac** — Kildall's
model is shared; only the bot's actions are confined. **Default: a separate macOS user account per bot** (near-zero
RAM, many bots). **A VM only for bots that browse untrusted sites or open unknown files.** ⚠️ To verify in the
research: macOS allows **at most 2 macOS VMs at once** on Apple hardware, and each VM needs several GB — next to
Lane A's 12–14 GB that means **about 1 VM at a time**.

## Phase 5 — voice and media

- ~~**Voice both ways.** Push-to-talk, ASR + TTS pair (2.0 GB)~~ → **moved to Phase 9.3** on 2026-09-27: local wake word, faster-whisper in, Kokoro out. Still **not** Qwen3-Omni
- **Image, video and 3D generation are queued jobs**, same machinery as Lane C. They never block the
  terminal

## Phase 6 — Lane C giants ⏸ **PARKED — no drive for 1+ month**

**Do not start this phase.** The drive is not ordered as of 2026-09-05. Phases 0–5 and 7–8 deliver
the whole product apart from the giants; come back here when the hardware exists.

### When it arrives — measure it first

```bash
dd if=/dev/zero of=/Volumes/<drive>/spd.bin bs=1m count=4096 && sync
dd if=/Volumes/<drive>/spd.bin of=/dev/null bs=1m && rm /Volumes/<drive>/spd.bin
```
**Every Lane C estimate depends on this number.**
Then `kimi-k3-in-c` for the 2.8 T tier — **needs ~1.7 TB free** (1.56 TB checkpoint + 109 GB trunk).
⚠️ **Resolve all 11 unconfirmed HF paths before starting a 4.9 TB download.**

---

# 🎯 KILDALL 100% — THE AGENTIC OS *(Phase 9, added v33)*

**Kildall is 100% complete when it is the core of a personal agentic OS.** Set by the user 2026-09-27.

> **Kildall is the engine. Obsidian is the memory. Google Workspace is the operating layer.**
> Voice is the front door, a wallpaper dashboard is the face, and skills turn daily work into one click.

**When: after everything else — Phases 4, 4C, 5, 7 and 8** (user decision 2026-09-27). Parked Phase 6 does
not block it. **9.3 replaces Phase 5's voice half.**

**Decisions from the 2026-09-27 interview:** Hermes = **channels only** · capture = **everything, keystrokes
included**, stored in a **separate vault** · voice = **English + Vietnamese** · Workspace = **full autonomy,
always** · cloud = **as now, vault context included — except the raw keystroke log, which never leaves the
machine** · users = **you now, paid clients later.**

## The stack *(every tool verified live 2026-09-27)*

| Layer | Pick | Licence | RAM | Job |
|---|---|---|---|---|
| **Engine** | **Kildall** — lanes, router, permissions, memory | MIT | Lane A **12.2–14.2 GB measured** | does the work |
| **Channels** | **Hermes Agent** · `NousResearch/hermes-agent` · 249k★, pushed today | MIT | unmeasured | chat channels (Telegram, Discord…) that call Kildall |
| **Reflex — "System One"** | **Laya-MLX** · `mizorewww/laya-mlx` · 6.4k★ · base `convaiinnovations/laya` | Apache-2.0 | **0.69–0.94 GB** | typed decisions in **7–14 ms** (author-measured, M3 Max). No text generation |
| **Ears** | **faster-whisper** · `SYSTRAN/faster-whisper` · 25.6k★ | MIT | unmeasured | speech → text, local |
| **Mouth** | **Kokoro-82M** via `kokoro-mlx` | Apache-2.0 | ~0.35 GB weights | text → speech, local, 54 voices |
| **Memory** | **Obsidian** vault + **Graphify** | — | app | second brain: `raw` · `wiki` · `outputs` |
| **Operating layer** | **Google Workspace** via MCP (built in 4.5) | cloud | — | Gmail · Calendar · Drive · Docs |
| **Face** | **Wallpaper dashboard** — ours | MIT | small | one-click skills + live metrics |
| **Bot app** *(v36)* | **Kildall Bots desktop app** — ours: the 9.6 web UI in a native window | MIT | small, unmeasured | create, watch, pause, approve bots; routes everything to Kildall |

⚠️ **RAM is the binding constraint.** Everything resident is roughly **16–20 GB against ~20 GB usable**, and
Lane A alone already shows **96 of 121 warning samples**. **Gate: a 10-minute soak with the whole stack
resident, zero critical samples — otherwise voice and Laya load on demand and unload when idle.**

## Slices

**9.1 — Laya reflex, System One.** The LLM router takes **5.06 s** mean; Laya answers typed questions in
milliseconds. First questions: *does this need text generation?* · *which of the 19 categories?* · *command,
question or note?* · *should this interrupt me?* **Adopt it as the first routing stage only if it scores
20/20 category on the frozen routing fixture**; otherwise it pre-filters and the LLM router decides.
🔴 Laya never decides a Never-tier action.

**9.2 — Hermes for channels only.** Hermes is already open source; it adds **chat channels** (Telegram,
Discord and the rest) and calls Kildall through a local OpenAI-compatible endpoint. **Kildall keeps its
own agent loop and executor.** 🔴 Hermes gets **no direct shell, file or network tools** — every action
happens inside Kildall, through `permissions.execute`. **Gate: a channel message asking for a recursive
delete is refused by Kildall, logged, and nothing is deleted.**

**9.3 — Voice layer, 100% local, English + Vietnamese.** Mic → **faster-whisper** (handles both languages)
→ Kildall routes → **Kokoro** speaks English. ⚠️ **Kokoro has no Vietnamese voice** — pick a local
Vietnamese TTS in this slice, by measured quality, and record it. Activated
by a **local wake word**; audio never leaves the machine. It sits on top of both Kildall and Obsidian:
*"note that…"* goes to the vault, *"do…"* goes to Kildall.
⚠️ **faster-whisper has no Metal backend — on this Mac it runs on the CPU.** **Gate: end of speech → first
audio under 1.5 s on short commands, measured.** If it misses, swap to `mlx-whisper` or `whisper.cpp`
(Metal) and record the swap. Hard mute key; mic indicator always visible.

**9.3 additions (v35):** **command mode** — say an instruction and Kildall edits the selected text *or runs
an action*, English and Vietnamese (the Wispr pattern, which can only edit text) · **voice cloning** with
**`Blaizzy/mlx-audio`** (MIT, zero-shot from a short clip; also a candidate for the **missing Vietnamese voice**
via Qwen3-TTS). ⚠️ Fit next to Lane A is unmeasured — gate on the 9.x soak; clone only voices you own.

**9.4 — Second brain.** Obsidian vault with **`raw/`** (captures), **`wiki/`** (entities and concepts — the
sample 1 pattern) and **`outputs/`** (everything Kildall produces). **Graphify** builds the link graph and
layout. Kildall retrieves through its existing memory layer — BM25 + Harrier vectors inside the
**12 items / 4,000 chars / 300 ms** caps — so every run starts with the right context, never from scratch.
🔴 **A new, separate vault** (for example `~/Brain`) — **not** the `~/Kildall` project vault, and **never a git
repo**. Never in GitHub, Hugging Face or any backup that leaves the machine.

**9.5 — Activity capture: everything, keystrokes included.** Apps and time, links, files, device events,
**screen text and keystrokes** → the separate vault's `raw/`, summarised into daily notes. User decision.
🔴 **Guardrails that stay:** the **raw keystroke log never goes to any cloud model** (summaries made locally
may) · the keystroke and screen logs are **encrypted at rest** · exclusion list (password managers, banking,
private windows, Keychain prompts, key files) · macOS already blanks keys typed in secure password fields,
but **only there** · captured text is **data, never instructions** · one command pauses capture.
⚠️ **Accepted risks, recorded:** with cloud "as now", other vault content can reach free-tier providers,
some of which keep or train on prompts.

**9.6 — Wallpaper dashboard.** A local web UI in a desktop-level window, behind every app. Shows **RAM used,
memory pressure, swap, GPU, tok/s, loaded lanes, prompt-cache hit rate, routing p50/p99, backup health**;
every **MCP connector** (failures included — `n8n` and `imessage` fail today), **plugin, skill and agent**;
the **skill audit** (use count and success rate from outcome logging, #14); running automations and loops.
**One-click skills** — every click passes the same permission tiers; Confirm still asks.

**9.7 — Skill engineering.**
1. **Mine** every past session — Claude and Codex transcripts, `CLAUDE.md`, `BENCHMARKS.md` — for work
   done over and over that is not a skill yet. Output a chart: **task · desired output · proposed skill.**
   Seed list from these sessions: Codex phase prompts · verifying Codex reports (SHAs, gates) · change-log
   entries · plan versioning · model and tool research with licence and star checks · name availability
   checks · local shop and stock checks · watch a video → research → vault · API key checks.
2. **Interview:** you give a stream of consciousness of your daily and weekly work; Kildall turns it into
   an interview and **calls out blind spots**.
3. **Write** `.kildall/skills/<name>/SKILL.md` — frontmatter `name` + `description` holding **the exact
   trigger phrases you say**; body: numbered workflow, your conventions, edge cases, **what to ask you vs
   infer**, and **what "done" looks like**.
4. **Dry-run** on a real example; refine until the output matches how you do it by hand.
5. **Automate** — schedule (launchd) and chain skills.
6. **Loop** — skills improve themselves **only on evidence**: a change is proposed, re-run on its dry-run
   examples and the eval harness (#13), and kept only if it wins. The #51 rule: grow only on evidence.
Only skill names and descriptions sit in context; a body loads when triggered — as Phase 4.2's
`load_skill` already does.

**9.8 — Operating layer: Google Workspace, full autonomy.** Gmail, Calendar, Drive and Docs through MCP
(4.5). Kildall sends, schedules and shares **without asking, always** — user decision. OAuth tokens in the
Keychain. 🔴 **Never-tier actions stay blocked in code** (autonomy cannot unlock them), and **every
Workspace action is logged** so you can review it. ⚠️ **Accepted risk, recorded:** an email or page with
hidden instructions can trigger actions under your name (51–100% attack success in the 4C research).
🔴 **A Google credential was pasted into chat on 2026-09-27. It is stored in no file. Revoke it.**

**9.9 — Skill packs:** research · content creation · data workflows. ⚠️ **Scope change:** content systems
(sample 1 `OrbiIntelligent/`) were declared out of scope on 2026-09-05 and are **back in scope** as a pack.

**9.10 — Customisable: fork and reskin.** Profiles per client — display theme, voice, wake word,
instructions, skill set. `kildall --profile <client>`. MIT permits forks.
**You now, paid clients later.** 🔴 **Before the first paid client:** a licence audit of every model in use
(custom rows: Kimi K3, GLM-5.3, Gemma terms), and **full separation per client** — own vault, own memory
database, own Workspace account, own keys. No client ever sees your personal capture. **v37: and #51 auto-fit
passing on the client's own Mac.**

**9.11 — Kildall Bots (the Grok Bot pattern, local).** A **`kildall-botd` launchd daemon** runs named bots —
each with a **job, instructions, skills, schedule, its own memory scope and its own permission scope** — on
its own sandbox computer (4C addition), reachable through Hermes channels (9.2) and the dashboard (9.6).
Approvals come back as Confirm prompts to your phone or dashboard. Every action still goes through
`permissions.execute`. ⚠️ 24 GB allows only a few bots working at once (v38: 4.4 measured 2 shared slots, so about 2); 24/7 needs the Mac never to sleep.
**Not a separate program** — a second agent loop would duplicate the tested Phase 3–4 boundary.

**9.11 addition (v36) — the Kildall Bots desktop app** (user decision 2026-10-02: a desktop app that only routes
the bots you create to Kildall). You **create, watch, pause and approve** bots in it; each bot is saved **inside
Kildall** (proposed `.kildall/bots/<name>/BOT.md`, the 4.2 skill pattern) and **`kildall-botd` does all the work**.
🔴 The app has **no shell, file or network tools of its own** — the Hermes rule (9.2); every action goes through
`permissions.execute`. **Reuse, not a second UI:** the app shows the **same local web UI as the 9.6 dashboard** in a
normal window, plus a menu-bar icon. The app, the CLI (`kildall bot new · list · pause · logs`) and chat channels
call **one bot API inside Kildall**. 🔴 That API listens **only on this Mac** (Unix socket or `127.0.0.1`) and
**requires a secret token** — otherwise any web page in your browser could command your bots. Window shell:
**native Swift `WKWebView`** (no new dependency, near-zero RAM) preferred over **Electron** (hundreds of MB);
decided in the 9.11 spec. **Gate: a request without the token, and one sent from a browser page, are both refused
and logged; nothing runs.**

## Phase 9 is done when

1. You speak a command in English or Vietnamese, hear the answer and watch the work on the wallpaper.
2. **Every daily and weekly task you listed is a skill or an automation**, or has a recorded reason why not.
3. The skill audit shows each skill's use count and success rate.
4. **Every earlier gate is unchanged** — recall, abstention, routing, tools, CLI, hooks, nuke.

---

# 🔄 PHASE 10 — MODEL REFRESH FOR EVERY SKILL *(v49 · 2026-10-13 · runs last, after everything else is complete)*

**User decision:** once every phase is done, re-pick the best model for **every skill and sub-skill** — the 302-leaf
catalog (`skill_catalog.py`, research in `Researchhub/sample3/OrbiOSS.md`, to be renamed **`KildallOSS.md`** in this step).
1. **Re-research every leaf** by benchmark evidence, **latest version per family**, best-per-skill regardless of brand;
   mark ✓ verified vs ⚠ reasoned default; keep a min-viable alternative where one exists.
2. **Re-assign lanes by measured fit** on the machine in use (#51 auto-fit): resident, hot-swap, streamed, or free cloud
   (NVIDIA NIM / OpenRouter / others — **never a paid API**).
3. **Update** `skill_catalog.py`, `Orbimodels.md` and the research file; download new models, remove replaced ones
   (deletion only with your OK).
4. **Gate every changed model** through the model-load procedure and its lane's gates; routing 20/20, recall, tools,
   CLI unchanged or better. Quota-limited research is never merged as fact.
**Seeds found 2026-10-13:** `tencent/Hy4-preview` now has GGUF builds (AngelSlim, AMAImedia) — its runtime blocker may be
gone; `moonshotai/Kimi-K2.7-Code` (2026-06-11, coding specialist); `deepseek-ai/DeepSeek-V4.1-Flash` (763 B);
`deepseek-ai/DeepSeek-V4-Flash-Vision-Exp` (2026-08-31). NVIDIA's NVFP4 builds are NVIDIA-GPU formats, not for the AMD box.

---

# 🔮 BEYOND THE PLAN — 90 improvements, after Phase 8 *(#52–#75 added v41, #76–#87 v42, #88–#90 v47; 9 of them scheduled earlier — see "Queued small slices")*

**Nothing here is scheduled or scoped. Recorded so the current build does not design them out.**
Phases 0–8 deliver a working Orbi. These are the ceilings that build then hits.

## ⭐ Do these three first

| # | Why it goes first |
|---|---|
| **13** | **Eval harness.** You cannot improve what you cannot measure. Phase 7 currently gates model swaps on **throughput only** — a faster, dumber model passes today. Seed it from Phase 1's frozen 20 cases. **Cheapest item here and everything else depends on it** |
| **14** | **Outcome routing.** Start *logging* in Phase 2 even if you never learn from it. **Only 46 of 302 leaves were benchmark-verified**; this log is the sole path to verifying the rest. Start now or start from zero later |
| **42** | **Keep the distillation pairs.** Phase 6 starts generating `(prompt, giant answer)` pairs. Storing them costs nothing; they cannot be recovered retroactively |

---

## Speed & hardware

| # | Idea | Buys | Cost |
|---|---|---|---|
| **1** | **Cross-lane speculative decoding** | **The biggest unlock.** Lane A drafts, Lane C verifies in batch — giant quality near Lane A speed | High risk, unmeasured. ⚠️ The plan's ban is narrower than it reads: it is a loss for *same-model* drafting in llama.cpp on Metal. **MLX supports it, and a 4B drafter against a 2.8 T verifier has never been measured on Apple Silicon** |
| **2** | **Confidence cascade** | tiny → A → B → C, escalating only when confidence is low. Most requests never leave the cheapest tier | Needs #11 (confidence estimation) first |
| **3** | **Warm pool** | Keep 2–3 Lane B models preloaded in spare RAM. Removes cold-load latency from common paths | RAM pressure; needs #36 to evict sanely |
| **4** | **Batch Lane C overnight** | Amortise the minutes-long load across a night's queued prompts. Makes 25 s/token tolerable | Scheduling only. Low risk |
| **5** | **Auto-quant search** | Find the lowest quant per model that still passes eval. Directly frees disk and RAM | Needs #13. Gemma's IQ3_S-vs-DWQ gap shows why this matters. **Absorbed by #51**, which generalises it from quant to quant + lane + batch + context |
| **6** | **Per-project KV cache** | Resident Lane A stops re-ingesting the same context every turn | Cheap. Compounds with the 32K cap |
| **7** | ⭐ **Thunderbolt clustering** | **The only direction not capped by 24 GB.** A second Mac changes Lane C's economics completely | Hardware money. Research sits unused in `sample3/UHWmini.md` §7 |

## Quality

| # | Idea | Buys | Cost |
|---|---|---|---|
| **8** | **Grammar-constrained tool calls** | ✅ **Already pulled into the build.** Makes an invalid call unrepresentable, not merely unlikely | — |
| **9** | **Self-consistency** | Sample N, take the majority. Reliable accuracy gain on hard reasoning | N× the tokens. Use only where it earns it |
| **10** | **Critic pass** | A cheap model checks Lane A's answer before it returns | One extra small call per request |
| **11** | **Confidence + abstention** | Orbi says *"I don't know"* instead of guessing. **Your stated biggest pain was verifying claims** | Hard to calibrate honestly |
| **12** | **Specialist ensemble** | Combine Lane B models where skills overlap | Load cost; only worth it for high-stakes leaves |
| **13** | ⭐ **Eval harness** | **Prerequisite for everything else.** Frozen tasks with known-good outputs, run before and after every swap | Small — a day, mostly fixtures |

## Router

| # | Idea | Buys | Cost |
|---|---|---|---|
| **14** | ⭐ **Outcome-based routing** | Learns from what actually worked. **Validates the 256 unverified leaves for free** | Logging now; reweighting later |
| **15** | **Task decomposition** | *"Refactor this and add tests"* is two skills. The router picks one. Decompose, route each, compose | Turns the router into an orchestrator — real complexity |
| **16** | **Re-routing on failure** | Today routing is one shot with no recovery | Needs a failure signal, which needs #11 |
| **17** | **Learned tool selection** | Which tool actually solved which task | Same log as #14 |

## Memory

| # | Idea | Buys | Cost |
|---|---|---|---|
| **18** | **Consolidation** | Compress old memories into durable facts. **Without it the hard caps slowly truncate away things worth keeping** | Needs a compaction pass |
| **19** | **Decay / forgetting** | **A wrong fact currently outlives a right one, at equal weight, forever** | Schema field — leave room in Phase 1 |
| **20** | **Episodic vs semantic split** | What happened, versus what is true. Different retention rules | Schema change |
| **21** | **Contradiction detection** | Flag when new information conflicts with something stored | Needs #22 |
| **22** | **Provenance + confidence** | Where a fact came from and how sure it is | Schema change |
| **23** | **Cross-project transfer** | Learn a pattern in project A, apply it in B | Risks the leakage the two-layer design prevents |
| **24** | **Index `Researchhub/`** | **64 MB of your own research is invisible to the agent built on it** — `UHWmini.md`, 233 wiki pages, the 341-skill table | Embedding model already exists. Cheap |

## Agent

| # | Idea | Buys | Cost |
|---|---|---|---|
| **25** | **Checkpointing** | Resume long tasks after a crash instead of restarting | Moderate |
| **26** | **Undo for agent actions** | Rollback beyond git — config, memory, installed tools | Needs an action journal |
| **27** | **Dry-run whole plans** | See everything before anything executes | Pairs naturally with #29 |
| **28** | **Dependency-graph subagent scheduling** | Real parallelism instead of spawn-and-hope. **Matters because separate-process mode caps at ~3 on 24 GB** | Scheduler complexity |

## Interface

| # | Idea | Buys | Cost |
|---|---|---|---|
| **29** | **Plan approval** | Show the plan, let you edit it, then execute | Low |
| **30** | **Session branching** | Fork a conversation to try two approaches | Storage, and UI thought |
| **31** | ⭐ **Ambient mode** | Orbi watches the repo and suggests unprompted. **Changes it from a tool to a presence** | Always-on cost; noise risk if it is wrong often |
| **32** | **Voice barge-in** | Interrupt mid-answer | Needs the voice stack from Phase 5 |
| **33** | **Long-job notifications** | Lane C and media jobs tell you when they land | Trivial |

## Reliability & ops

| # | Idea | Buys | Cost |
|---|---|---|---|
| **34** | **Health telemetry** | Track tok/s drift and memory growth over time, not just at swap points | Low |
| **35** | **Auto-rollback** | Revert a model swap that regresses quality | Needs #13 |
| **36** | **Disk pressure management** | Auto-evict the least-used Lane B models | Low. Needed once Lane B is fully installed |
| **37** | **Energy monitoring** | ⚠️ **Your own research flags 3.8–12.5× per-token energy on SSD offload.** For an always-on agent that is a real cost | Measurement only |

## Security

| # | Idea | Buys | Cost |
|---|---|---|---|
| **38** | **Sandbox for agent-run code** | Phase 3 gates *what* runs; this bounds *what it can reach* | Real work — containers or a jail |
| **39** | **Egress allowlist** | Constrain what Orbi may contact | Low |
| **40** | **Secret scanning** | Catch credentials before any outbound call | Low |
| **41** | **Tamper-evident audit log** | An action record that cannot be quietly edited | Moderate |

## Learning

| # | Idea | Buys | Cost |
|---|---|---|---|
| **42** | ⭐ **Lane C → Lane A distillation** | **The giant's judgment at Lane A speed.** Every Lane C job yields a `(your real prompt, giant answer)` pair. After a year that is a training set of **your actual work**, not a public benchmark. Closest thing to the project's original "clone the good models" goal | ⚠️ **It is training** — it breaks the zero-training promise. One hour of LoRA, not a pretraining run. **Keep the pairs from Phase 6 regardless** |
| **43** | **Auto-refresh the vault** | Re-verify model picks monthly. **Qwen shipped three generations in six months** | Search budget |
| **44** | **Watch upstream repos** | Know when a tool Orbi depends on changes or dies | Low |

## Economics

| # | Idea | Buys | Cost |
|---|---|---|---|
| **45** | **Free-tier optimizer** | Pick the Cloudcall provider by remaining quota rather than fixed order | Quota tracking |
| **46** | **Local-vs-cloud per request** | Decide by latency and cost, not a static rule | Needs #34 |

## Efficiency & self-tuning

| # | Idea | Buys | Cost |
|---|---|---|---|
| **47** | **Prompt self-optimisation** | The list improves **models** (#42) and **routing** (#14) — **nothing improves Orbi's own prompts.** A failed task teaches you about the *instruction*, not only the model. DSPy-style tuning treats prompts as parameters | **Pairs directly with #13** — once you can measure, the prompt is the cheapest thing to change |
| **48** | **In-flight context compression** | **#18 consolidates *stored* memory; nothing compresses the *live* conversation.** A long session fills 32K regardless of memory quality, then truncates the task being worked on. Summarise finished sub-tasks to a line each | **Matters most in Phase 4**, where multi-file work runs long |
| **49** | ⭐ **Semantic answer cache** | Recurring questions — *"how does this module work"* — each cost a full inference today. Embed the question; if near a previous one, return the stored answer with provenance. **Turns repeats into ~0 tokens** | **The embedding model already exists for memory.** Cheapest latency win here, and the likeliest of these four to be worth building |
| **50** | **Thermal & sustained operation** | **`sample3/UHWmini.md` §8 covers this and nothing on the list used it.** A Mac mini running an always-on agent throttles. Worth knowing whether 29 tok/s still holds at hour six, and backing off when it does not | **#31 ambient mode turns intermittent load into permanent load**, and it is where **#37's 3.8–12.5× per-token energy** cost lands |
| **51** | 🔑 **Hardware auto-fit, and auto-expand** | **Orbi currently runs on exactly one computer.** Every number in this plan — 26.637 tok/s, 96/121 pressure warnings, 5.06 s routing, the 120 GB/s ceiling — is a property of this Mac mini, and none of it is read from the machine at setup. Make it portable in both directions. **Downward (auto-fit):** read the machine, then derive the quant, GPU layers, batch, context, cache budget and **which lane each model belongs in** — because lane assignment is already a hardware function (`active_bytes` vs usable RAM), just hardcoded. **Upward (auto-expand):** on a bigger machine, promote models up lanes. **A model moved C→B is free quality** — identical weights, no longer read off a disk 41× slower than RAM. 🔑 **The catalog already carries the data for this**: `skill_catalog.py` holds an *original* and a *preferred* pick per leaf, so small machines take the min-viable and large ones take the best-benchmarked. Nobody called it auto-expand. ⚠️ **But the axis is thin — only 13 leaves have a named alternative** (56 exist in sample 1's research), so ~250 of 302 have nothing to expand into | 🔴 **Shrink on arithmetic, grow only on evidence.** Auto-fit downward is safe — if it does not fit, it does not fit. **Auto-expand upward is dangerous without #13**, because only **46 of 302 leaves are benchmark-verified**: on a big machine Orbi would reach for a "better" pick that is a reasoned default for ~256 leaves, getting slower *and* possibly worse with no way to tell. 🔴 **Second trap: bigger ≠ faster.** A 32 GB base M4 still runs at 120 GB/s, so extra capacity promotes lanes but speeds up nothing already resident — only the M4 Pro's 273 GB/s does that. ⚠️ **Third trap, and this project already proved it: active params are not residency.** Lane A is **4 B active — ~2 GB by arithmetic — but 12.23 GB measured RSS**, a 6× error. So the shape must be **propose, then verify**: compute candidates, run a short gate, adopt what passes, fall through on failure — the Phase 1 Lane A loop, automated. Supersedes and absorbs **#5**. Needs **#13**. ✅ **v37 (user decision 2026-10-03): now a Phase 7 slice, right after #13, and required before the first paid client (9.10).** Downward auto-fit first; upward only on an eval win. **Gate:** on this Mac it derives settings that match or beat the hand-picked ones on every frozen gate; under a smaller RAM budget set in config (e.g. 16 GB) it picks settings that pass a 10-minute soak with zero critical memory samples and keep every frozen gate. 🔑 **Speed follows memory bandwidth, not RAM size** — read the chip's bandwidth, never assume it |

---

## Added v41 — from measured problems (2026-10-07, user: "add all of them")

| # | Idea | Buys | Cost |
|---|---|---|---|
| **52** | ⏩ **Wired limit restored at every boot** — a LaunchDaemon you install once with sudo sets `iogpu.wired_limit_mb=20480` | The limit reset to 0 after reboots at least 3 times and blocked runs | One sudo install by you; Codex only writes the plist, never runs sudo |
| **53** | ⏩ **Permanent backup job** in `~/Library/LaunchAgents` instead of per-login registration | The backup job broke twice; 3 nights were lost | Small |
| **54** | ⏩ **Off-machine backup** of `kildall.db` to `KildallC` | Today every backup is on the same disk as the database | Needs the drive mounted |
| **55** | ⏩ **Secret-scanner git hook** — refuses any commit containing a key | Keys were pasted in chat twice | Small |
| **56** | **Slim `CLAUDE.md`** — history moves to `CLAUDE-history.md`; rules, state and recent entries stay | ~260 KB loaded into every session | A Claude task, not code |
| **57** | ⏩ **Copy by reference** — tools accept a source-span id instead of retyped text | t07/t09/t12 survived four fixes; grammar cannot fix copying, a pointer can | Frozen fixtures untouched; must lift first-pass without editing them |
| **58** | ⏩ **Code-built delegation prompts** — the parent fills fields; code assembles the child prompt | Fixes 4.4's failed exact-once smoke | Small |
| **59** | ⏩ **Gemma 4 vision** — load its image projector (mmproj) | Kildall reads text in images but cannot understand them; 4C layer B needs this | RAM next to Lane A; measured |
| **60** | **Your own good answers as examples** — retrieved past successes in the prompt | Teaches your conventions without training | Context budget |
| **61** | **Vietnamese test set** | Frozen tests are nearly all English; you will use Vietnamese | Needs #13 |
| **62** | ⏩ **Router prompt saved to disk** (`--slot-save-path`), reloaded after restarts — ⚠️ **partial (PR #7):** b10809 does not save SWA checkpoints, so startup still rebuilds the prefix (~20 s before ready); revisit when llama.cpp saves them | Removes the 12–18 s cold route after every restart | Disk; verify in b10809 |
| **63** | ⏩ **Idle re-warm** of the router prefix after eviction | Fewer cold routes during use | Idle compute |
| **64** | **Only the tools a request needs** in the prompt | Prefill is ~85 tok/s; shorter prompts read faster and tool choice improves | Router must name tool sets |
| **65** | **Prompt diet** — measure and trim system and tool text | Same: prefill is the bottleneck | Must hold every gate |
| **66** | **Memory conflict detection** — a new fact that contradicts an old one asks which is right | Stops wrong facts piling up | Small |
| **67** | **Automatic session summaries** into memory | Runs start with context; pairs with #48 | Small |
| **68** | **Hash-chained audit log** | Proves the log was not edited afterwards | Small |
| **69** | **Growing attack test set** — every new injection trick becomes a permanent fixture | Defences only get stronger | Upkeep |
| **70** | **Permission profiles per project** | A client folder can be stricter than yours | Pairs with 9.10 |
| **71** | **Daily real use now**, before Phase 9 | Real use finds gaps frozen tests miss and feeds #14 | Your time |
| **72** | **Code-only tests on GitHub** for every PR (no models) | Catches breaks before Claude's review | CI minutes |
| **73** | **Gate trend chart** over time | Shows slow drifts like the 4.4 routing slowdown early | Pairs with 9.6 |
| **74** | **Checklist auto-ticked from evidence files** | The checklist says 14 done; far more is | Small |
| **75** | **Codex briefs as reusable skills** | Faster, consistent briefs; seeds 9.7 | Small |

⏩ = scheduled early (see "Queued small slices"). The rest follow the normal Phase 7–9 order.

## Added v42 — safety, privacy and speed (2026-10-12, user: "add all the improvement ideas")

| # | Idea | Buys | Cost |
|---|---|---|---|
| **76** | 🔑 **Kill switch** — one command/hotkey stops every agent, bot, capture and cloud call at once | Full Workspace autonomy and full capture need an instant stop | Small |
| **77** | 🔑 **"Local-only" memory tags** — tagged memories never reach any cloud model | You chose cloud "as now" with vault context; this protects the private parts | Must hold in every cloud path (4.5a scrub) |
| **78** | **Daily action budget per bot** (9.11) | A confused 24/7 bot cannot send 500 emails | Small |
| **79** | **Simulate mode** — show what an agent would do, without doing it | Safe tests for new bots, skills and automations | Every action needs a dry-run form |
| **80** | **Resident model server** — kept running as a background service | Removes the ~20 s startup rebuild (b10809 omits SWA checkpoints) | RAM held while idle |
| **81** | 🔑 **Warm prompts for answer slots** — reuse the shared system + tool prefix, like the router | Prefill is ~85 tok/s; every answer re-reads the same text | Slot memory; measured |
| **82** | **`kildall doctor`** — one health command: models, keys, backups, daemons, disk, memory pressure | Easier than reading `check.sh` and logs | Small |
| **83** | **Test-log retention** — keep summaries, prune raw `.session` logs older than N days | `.session` grew to 3.3 GB and keeps growing | Never prune evidence a review still needs |
| **84** | **Model-update watcher** — weekly check for newer versions of every model in use | Automates the "latest versions only" rule | Small; suggests, never auto-swaps |
| **85** | **Answer receipt** — lane, model, time, tokens, and whether the cloud was used | Shows what happened and where data went | Small |
| **86** | **Unused-model report** | ~128 GB of unused weights stay visible | Small |
| **87** | **Per-client licence tracker** — which model licences each client setup depends on | Required before paid clients; generated automatically | Pairs with 9.10 |

## Added v47 — coding core (2026-10-13, user: "2,3 and 6 too")

| # | Idea | Buys | Cost |
|---|---|---|---|
| **88** | ⏩ **Repo map** — an index of every file, symbol and call site (tree-sitter + Harrier embeddings), so the small context always receives the right code | Context is the weakest score (1/10); coding agents live on finding the right code | Medium; index kept fresh on file change |
| **89** | ⏩ **Test-driven fix loop** — for coding tasks, run the project's tests/linters, read failures, fix, repeat until green or a retry cap; then (#4 idea) escalate to free cloud (NIM) only after N local failures | The biggest single coding gain: execution feedback, as Claude Code uses | Medium; every command through `permissions.execute` |
| **90** | ⏩ **Collect LoRA training data now** — store every accepted diff / answer with its prompt (consented, local, never Claude/GPT outputs) | The LoRA lever is ready the day the 128 GB machine arrives | Small; storage + privacy rules from 9.5 |

## The honest shape of this list

**Most of these are small. Three are not.** #1 (spec decoding) may not work at all. #42 (distillation)
changes what Orbi promises. #7 (clustering) costs hardware. Everything else is a day or two each.

**The dependency chain that matters:** **#13 → #35, #5** · **#11 → #2, #16** · **#14 → #17** ·
**#22 → #21**. Build #13 first and four other items become possible.

# OPERATIONS

| | |
|---|---|
| **Secrets** | macOS Keychain. Never in config, DB, logs or backups. ⚠️ Cloud API keys currently wait in a plain holding file, `~/.config/orbi/keys.env` (chmod 600, outside every repo); **Phase 4.5 must import them into the Keychain** and never read the file at runtime |
| **Publishing** | ⏸ **Hugging Face mirror PAUSED 2026-10-05 (user: "no need hugging face") — Codex skips `kildall-hf-sync`; GitHub only.** Kept for later: ~~every push to GitHub `main` is followed by `kildall-hf-sync`~~, which mirrors the same commit to Hugging Face `MinhDuc26121/kildall` (public, MIT). It uploads **only git-tracked files of `origin/main`** via `git archive` — never `models/` (154 GB of third-party weights), `.venv/`, `.session/` or memory databases — and refuses `*.gguf`, `*.safetensors`, `*.sqlite3`, `*.env` or any file over 20 MB. `--dry-run` lists the files without uploading. Script: `~/.local/bin/kildall-hf-sync`. **Never run `hf upload .` from `code/`** |
| **Spend cap** | 🔴 **Permanent: never a paid API key or paid cloud usage** (user, 2026-10-13: "never in a mil year"). Free tiers and local only. Buying better hardware is allowed |
| **Rollback** | skills, prompts, config in git · memory backed up nightly · `orbi rollback` |
| **Logs** | L0 90 days · actions 180 days · backups 14 days · **alarm if `orbi.db` > 2 GB** |
| **Benchmarks** | weekly. **>10% throughput drop blocks `dev` → `stable`** |
| **Uninstall** | `kildall nuke`, dry-run default. **Deletes `~/Kildall/code/` only** — never `Researchhub/`, the planning files, or `.obsidian/` |
| **MCP** | Orbi is an MCP client. ⚠️ `n8n` and `imessage` currently fail to connect |
| **Packaging** | `pip install -e ~/Kildall/code`. Python pinned `<3.13` |
| **Multi-session** | safe **only** with SQLite WAL + `busy_timeout` |

---

# 🔧 THE MODEL-LOAD PROCEDURE — runs for EVERY model, EVERY lane

**`sample3/UHWmini.md` is not a reference section. It is a procedure.** Every technique in it applies
at the moment a model is loaded — Lane A in Phase 1, Lane B in Phase 5, Lane C in Phase 6. **Phases do
not "do" hardware; every phase that touches a model runs this.**

## Once per machine

```bash
bash ~/Kildall/Researchhub/sample3/uhwmini-setup.sh   # audits the machine, safe to re-run
sudo sysctl iogpu.wired_limit_mb=20480             # ✅ done — but RESETS ON REBOOT
```
⚠️ **The wired limit resets on every reboot.** `check.sh` must verify it and warn. Biggest single win.

## Once per model — before it is ever benchmarked

| Step | Do | Why |
|---|---|---|
| **1. Quantise** | **DWQ 4-bit**, not plain 4-bit | Same file size, **quality of 6-bit**. Free. MLX only |
| **2. Verify** | confirm the DWQ build loads and matches | A bad quant silently degrades everything downstream |

## Every load — the standard flag set

```bash
llama-server -m <model> \
  -lm mmap \                            # NOT --no-mmap, which is deprecated
  -fa on \                              # flash attention — confirm it actually took
  -ctk q8_0 -ctv q8_0 \                 # quantise the KV cache (memory, not speed)
  --cache-ram 768 --ctx-checkpoints 3 \ # bounded prompt cache — see below
  -c 32768                              # cap context; cache outgrows the model past ~100K
```

### 🔑 The bounded prompt cache — the biggest measured speed win in the project

**Routing went from 15.29 s to ~0.97 s warm — roughly 16×** — and it came from caching the prompt
prefix, not from any model change. Measured 2026-09-20.

**The sizing is not arbitrary. Smaller values were tested and failed:**

| Setting | Result |
|---|---|
| `--cache-ram 0` | full prefill every request — the original **11.50 s** of that 15.29 s |
| 256 MiB | ❌ could not hold a 464.6 MiB prompt plus checkpoints |
| 512 MiB, 1 checkpoint | ❌ saved state but **could not rewind the sliding-window cache** to a differing user suffix, so full prefill remained |
| **768 MiB, 3 checkpoints** | ✅ **reuses the prefix even after an interleaved answer** |

⚠️ **Honest limits.** ~0.97 s is **warm** latency over 19 of 20 cases. The **full product mean is
5.06 s** including 5 cache misses; hits average 0.89 s. **A long generated answer can evict the
prefix.** Never quote 0.97 s as the product number.

**Never:**
- ⚠️ **Speculative decoding — no longer a rule (removed 2026-10-13); decided by measurement per platform.** On Metal it measured **loss**, −11% to −28% **even at 100% draft
  acceptance**. Each draft step launches its own Metal kernel and the dispatch overhead eats the gain.
  MLX only.
  - ⚠️ **This includes DFlash 2, and the question comes up often — here is the answer.** DFlash 2 is
    real: merged into llama.cpp main, **1.84× measured tok/s with byte-identical output**. It does
    **not** apply to Lane A, for three independent reasons, all from `sample3/dflash2 hwmini.md`:
    **(1) no Gemma drafter exists** — drafters are model-specific and the only published ones are
    `incoai/Qwen3.8-27B-DFlash2` and `z-lab/Qwen3.8-27B-DFlash2`; **(2)** that file's own verdict for
    this machine is *"runs on your M4 24 GB? only via MLX — NOT llama.cpp"*, and Lane A runs llama.cpp;
    **(3)** the one model it supports is **Qwen3.8-27B, already rejected as dense** — projected
    ~5.8 tok/s here, so even 1.84× lands at ~10.7, under the 15 bar.
    **Revisit if** a Gemma 4 26B-A4B drafter is published, **or** Lane A ever moves to MLX.
- ❌ **The Neural Engine.** Settled dead end for token generation.
- ❌ **`--no-mmap`.** Deprecated.

## Every benchmark

**Run 10 minutes, not 60 seconds**, and watch memory pressure throughout. A model that looks fine for
one minute can thrash at minute six.

## Per-lane notes

- **Lane A** — resident, so it gets the full treatment. **Phase 1 must apply all of this before
  measuring the four gates**, or the tok/s number is meaningless.
- **Lane B** — loads and unloads in seconds. Quantise once, then the standard flags.
- **Lane C** — streamed. `-lm mmap` is doing the heavy lifting; expert paging is the bottleneck.
- **Dense models** — see `Orbimodels.md` → *When a model is dense, convert it* (CMoE, training-free).

# HONEST RISKS

1. **Lane C may not earn its 4.9 TB.** ~17.9 s/token for Kimi K3, worse on a slow external drive — though the **Flash tier runs at ~2.2 s/token** and is far likelier to pass. Phase 6's exit test is
   designed to kill it.
2. **No Apple Silicon number exists** for the 2.8 T tier. Phase 6 produces the first.
3. **Turbo Fieldfare is not an escape hatch.** It proves Apple Silicon expert streaming works, but is
   **pinned to one model and one quantisation** and needs macOS 26 / Swift 6.2 / Metal 4. A borrowable
   design (16-slot-per-layer LFU cache), not a runtime for your models.
4. **The scope is now very large.** Claude Code parity plus voice plus media is **116 checklist items**.
   Phases 0–3 are small; **Phase 4 is most of the work**.
5. **Subagents fight the RAM budget.** Separate-process mode caps at about three. Shared mode is the
   default for a reason.
6. **11 of 23 HF paths are unconfirmed.** Resolve before downloading terabytes.
7. ✅ **Stale models resolved 2026-09-06.** The two that were actually in the lane tables are replaced:
   `granite-guardian-3.x` → **Granite Guardian 4.1 8B**, and `Molmo-72B-0924` → **Molmo2 8B** (1/9 the
   size, better pointing scores, freeing 36 GB). The other three audit entries — `Llama-Guard-3`,
   `wildguard`, `bge-m3` — **Orbi does not use them**; better picks already hold those roles.
   **Version audit continued 2026-09-06:** five more corrections applied — `PaddleOCR-VL` pinned to
   **1.6**, both DeepSeek models pinned to their dated GA tags (**`-0813`**, **`-0731`**), **Wan 2.7
   superseded by Wan 3.0** (beta) and **Hunyuan3D-2.1 by v3**. `canary-qwen-2.5b` and
   `Qwen3-Omni-30B-A3B` confirmed current. ✅ **Version audit complete — every model checked, nothing outstanding.** Upgrades applied:
   `Qwen-Image` → **`Qwen-Image-2512`**, `Qwen3-Reranker-8B` → **`-4B`** (beats the 8B on MTEB-R at
   half the size), embeddings → **`Harrier-oss-v1-27B`** (**#1 on multilingual MTEB-v2**, MIT), and
   **`Qwen3-VL-235B` dropped** (Sept 2025, superseded, and Lane A is multimodal). Full audit in
   `Orbimodels.md`.
8. ⚠️ **Disk is adequate, not roomy. 93.3 GB free (measured 2026-09-06).** Lane A candidate #1
   (Qwen3.8-27B + CMoE, 17 GB) fits with room for all of Lane B. Candidate #2 (Flash-Next, 90 GB)
   fits with **3 GB spare and no room for anything else**. **Correction on record:** an earlier
   estimate said 113.8 GB would be reclaimed by deleting caches and Orbi-Sources; the real gain was
   **28.4 GB**, because `du` reports logical size on APFS and both the HuggingFace cache and the
   180 git repos shared blocks heavily. **Freeing the 62 GB CrossOver Steam bottle is the one move
   that would make every option comfortable.**
9. **Licences vary — and Orbi's own licence is MIT.** Kimi K3 and GLM-5.3 custom; `NLLB` CC-BY-NC and
   `FLUX.2 dev` non-commercial were **excluded**. Picked on evidence, licence flagged per row.
   🔑 **MIT covers Kildall's code only (`~/Kildall/code`), never the models.** Orbi downloads weights from
   their publishers at setup and **never ships or redistributes them**, so each model's own licence
   binds whoever runs it — MIT cannot relicense a custom-licence model. **Rule: Orbi never bundles
   weights in its repo or releases**; custom-licence rows stay flagged, and any commercial use must
   check them per row. **To do (next Codex slice, not yet present):** add `code/LICENSE` with the
   standard MIT text, `Copyright (c) 2026 Nguyen Hoang Minh Duc`, and `license = "MIT"` in
   `pyproject.toml`. Third-party code copied into `code/` must be MIT-compatible and keep its
   notice.
10. **Research ages in weeks.** Qwen shipped 3 versions in 6 months. Phase 7 exists for this.

---

# OPEN QUESTIONS

1. **Will Lane A hit 15 tok/s?** **Qwen3.8-Flash-Next** is the right shape (MoE, 6B active) but
   **streaming a 180B/6B MoE on an M4 has never been measured by anyone.** Phase 1 answers it.
2. **Which giants earn their disk?** Phase 6 measures each against Lane A.
3. ~~**When does the 8 TB drive arrive?**~~ — **answered 2026-09-05: not ordered yet, likely 1+ month
   out.** **Phase 6 is parked.** Build Phases 0–5 and 7–8 first; they are the whole product minus the
   giants. Do not design around Lane C arriving soon.

---

## Change Log

- **2026-10-13 (v49)** — **Phase 10 added: model refresh for every skill and sub-skill**, the final step after everything else (user decision; a full Lane C rework was dropped). Re-research all 302 leaves, re-assign lanes by measured fit, update catalog/model list/research file (`OrbiOSS.md` → `KildallOSS.md`), gate every changed model. Seeds recorded: Hy4-preview GGUF builds now exist, Kimi-K2.7-Code, DeepSeek-V4.1-Flash, V4-Flash-Vision-Exp.
- **2026-10-13 (v48)** — **Pre-purchase checks added** (user: "add them and you do the research rn"): A — prove test #3 via NVIDIA NIM's free big models before buying; B — GPU memory research **done**: ~120 GiB usable on Linux with `amdgpu.gttsize`/`ttm.pages_limit` (default half; 96 GB is Windows) → the 7/10 model fits tightly. **Corrects Claude's earlier "96–110 GB" assumption.** Measured chip speeds recorded (gpt-oss-120b 55–60 tok/s).
- **2026-10-13 (v47)** — **Coding core added** (user: "2,3 and 6 too"): #88 repo map, #89 test-driven fix loop (free-cloud escalation only after local failures), #90 LoRA data collection — scheduled **before test #3**, right after the NVIDIA NIM provider slice (also queued now). Checklist +4.
- **2026-10-13** — **DeepSeek-V4.1-Flash recorded** (2026-09-10, MIT, **763 B**) — newest, but too big to be resident on 128 GB; free via NVIDIA NIM. ⚠️ **The 7/10 resident pick is now in doubt:** V4-Flash-0731 is 304 B per HF (~114 GB at 3-bit) vs ~96–110 GB GPU-usable on the AMD box — re-check (pruning / lower bits / smaller model) before buying.
- **2026-10-13 (v46)** — **Three rules removed by the user:** "unmodified weights", "no training", and the speculative-decoding ban (now decided by measurement per platform). **Kept forever: never a paid API key or paid cloud** ("never in a mil year"); better hardware may be suggested. Road to 7/10 gains pruning, LoRA fine-tuning and speculative decoding as levers. Never train on Claude/GPT outputs (their terms).
- **2026-10-13** — Clarified: "no speculative decoding" is a **Metal-only research finding** (UHWmini.md), not a user rule. On Linux/Windows GPUs it is untested and will be measured (e.g. DeepSeek MTP on the AMD mini PC).
- **2026-10-13 (v45)** — **Context follow-up slice added** (user: "add them"): 4-bit KV, document KV saved to disk, retrieval for big files, map-reduce summaries, and ≥128K on the 128 GB machine with a compact-attention model. Runs after the current long-context slice. **8/10 written as an explicit target**, including the user's OpenRouter key step. Checklist +5.
- **2026-10-13** — **Hardware decided: GMKtec EVO-X2 mini PC, 128 GB** (user: "mini pc it is"), 4 TB + 4 TB inside, bought once the project succeeds. **Target: 7–8/10.** Consequence: the Linux port becomes required before the machine arrives. A PC build at the same budget was ruled out: 128 GB DDR5 (~52–60M) and 8 TB NVMe (~40M+) push it to ~175–185M, with only 48 GB VRAM.
- **2026-10-12 (v44)** — **"Road to 7/10" added**, active only once a 128 GB machine exists (user decision): 128 GB machine + a strong open coding model resident (e.g. DeepSeek-V4-Flash ~3-bit, unmeasured) + ≥ 64K context + tests #3 and #1 passed, features frozen until then. 10/10 recorded as unreachable locally at $0. Hardware candidates and the 8 TB / Linux-port constraints recorded.
- **2026-10-12 (v43)** — **Cross-platform added** (user picked option 1): a platform layer right after long context (Mac-only parts behind one interface, zero behaviour change), then Linux (Fedora + Ubuntu tested) and Windows via WSL2 before the first paid client; every gate re-passed per OS. Needs an NVIDIA test PC. Checklist +3.
- **2026-10-12 (v42)** — **12 improvements added, #76–#87** (user: "add all the improvement ideas"): kill switch, local-only memory tags, bot action budgets, simulate mode, resident model server, warm answer slots, `kildall doctor`, test-log retention, model-update watcher, answer receipts, unused-model report, per-client licence tracker. Not scheduled early; they follow the normal Phase 7–9 order.
- **2026-10-08** — **Router warmth reviewed (PR #7, `aef3d02`): accepted.** In use: 0 cold routes, mean 0.824 s, p99 0.989 s; soak 52/69/0 (better than 103). #62 partial — restore works but b10809 omits SWA checkpoints, so ~20 s rebuild moves to startup. Scores/latency/soak measured on source-v1; v2 changed only the idle branch (controls re-run, startup path proven unchanged).
- **2026-10-07** — **4.5a reviewed (PR #6, `10bad9b`): accepted.** Exclusions enforced in code, keys via stdin, leak scan 0, routing 1.654 s, live LLM7 $0. Gap: OVHcloud configured but never called live — added as the first 4.5d gate.
- **2026-10-07** — **Google Gemini and Groq removed from the cloud plan** (user decision). 4.5a must never list, import or call them. ⚠️ Consequences: keyless providers left are **LLM7 and OVHcloud AI Endpoints** (both anonymous per `Cloudcall/`; limits undocumented, throttled first) — so **4.5d can still reach 2 live cloud members** if their model families differ; more keys widen it. The large-context cloud fallback loses Gemini's ~1M window. *(Corrected same day: an earlier note said only LLM7 was keyless.)* Research files in `Researchhub/` are unchanged.
- **2026-10-07** — **Routing fix reviewed (PR #5, `d82609a`, not merged): accepted.** Option B — 3 slots, router on slot 0, work on 1–2: routing mean **1.618 s** (from 6.467 s), cold 1/20, all gates held, option A failed and is recorded. Cost: soak **18/103/0** (was 121/0/0), peak RSS 13.21 GB. Plan updated: 4.5a routing gate → 1.78 s; long-context slice must check unified KV first and must not exceed 103/121 warnings. 4.5a was never started; it is next in the queue.
- **2026-10-07 (v41)** — **24 improvements added, #52–#75** (user: "add all of them"); 9 scheduled early as small slices in a new "Queued small slices" order: router warmth (#62, #63), ops hardening (#52–#55), quality (#57, #58), Gemma vision (#59) before 4C. #56 (slim `CLAUDE.md`) approved as a Claude task. Checklist +9.
- **2026-10-07 (v40)** — **Long-context slice added** (user: "1 for now 5 later"): per-slot context 4,096 → 16K, then 32K only if 16K passes; runs after the routing fix; prefill time is the real limit (~85 tok/s, 32K ≈ 6 min); all 4K assumptions become config. **A faster Mac is recorded for later**, not scheduled. Checklist +2.
- **2026-10-06 (v39)** — **Deep research added as one feature, sub-slice 4.5e** (user: "for deep-research add the single feature"): `kildall research` — angles → search → fetch + guard → claims with quotes → 3-vote verification (failed votes = unverified) → cited report; a queued job; after 4.5b and 4.5d. Checklist +3 → **203 items**.
- **2026-10-05** — **Fix:** the 4.5 spec still told Codex to run `kildall-hf-sync` after every push; removed (Hugging Face paused). Spec facts updated: Gemini and Groq keys exist; free disk 94 GB. Routing-fix slice written (pin the router slot; brief in `CLAUDE.md` log) — if it lands before 4.5a, the 4.5a routing gate becomes the new main mean + 10%.
- **2026-10-05** — **Hugging Face mirror paused** at user instruction ("no need hugging face"). Briefs no longer run `kildall-hf-sync`; the script stays at `~/.local/bin/kildall-hf-sync` unused. GitHub stays the only remote.
- **2026-10-04 (v38)** — **Phase 4.4 reviewed and recorded** (`3b6b890`): separate-process cap **0** (measured GPU OOM), 2 shared slots = +3.8% throughput, routing mean 6.74 s; the 4.4 follow-ups now buy independent checks, not speed; 9.11 runs about 2 bots at once. **Recall gate rule:** frozen test on 1 slot + per-slot verifier on 2 slots. **Phase 4.5 design spec added** (Claude): four sub-slices 4.5a–d, threat model T1–T9, exact gates. Key facts: no API key exists yet (LLM7 is keyless); Granite Guardian 4.1 8B is Apache-2.0, Q4_K_M 5.12 GB, co-residency unproven; free disk 23 GB. Rule: Codex stops at the PR, merge on the user's word. Checklist → **200 items**.
- **2026-10-03 (v37)** — **#51 hardware auto-fit scheduled as a Phase 7 slice** (user picked A), right after the eval harness (#13), and made a prerequisite for the first paid client (9.10). Downward auto-fit first; upward only on an eval win. Gate written into #51. Build-order row 7 updated. Note recorded: decode speed follows memory bandwidth (M4 120 GB/s here), not RAM size. Checklist → **194 items**.
- **2026-10-02 (v36)** — **Kildall Bots desktop app added to 9.11** (user picked option B: a desktop app that only routes the bots you create to Kildall). A thin app showing the 9.6 dashboard web UI in a normal window plus a menu-bar icon; bots are saved inside Kildall; `kildall-botd` does the work through `permissions.execute`; the app has no tools of its own; one bot API shared by app, CLI and chat, local-only and token-locked. Native `WKWebView` preferred over Electron for RAM — decided in the 9.11 spec. **Bot computers (4C):** virtual, on this Mac — default a separate macOS user per bot, a VM only for risky bots; the 2-VM macOS limit and VM RAM are to be verified in the 4C research. New stack row "Bot app". Checklist → **192 items**.
- **2026-10-01** — **Fix:** v35 placed swarm orchestration "in 4.4" while 4.4 was already running; corrected to a follow-up slice after 4.4 merges, so the running slice is never widened.
- **2026-10-01** — **Roles fixed (user decision):** GPT-6 Astra builds every slice; Claude (Opus 5.5) designs the judgment-heavy phases beforehand and reviews every slice afterwards. Mixed-builder splits were considered and dropped.
- **2026-10-01 (v35)** — **Six paid features from `sample3/6aifeatures.md` adopted as Kildall patterns**, at user instruction: **verified review** (Ultrareview) as a 4.4 follow-up slice; **Model Council** in 4.5, kept only if it beats Lane A on the Phase 7 eval; **swarm orchestration** (Kimi) as a 4.4 follow-up slice with Lane C for the hardest step; **bot sandbox computer** research before 4C; **command mode + voice cloning** (Wispr, ElevenLabs → `mlx-audio`, MIT) in 9.3; **Kildall Bots** (Grok Bot) as new slice **9.11**, a daemon inside Kildall, not a separate program. **Kimi K2.6 recorded for later, not added** (older than K3; its swarm runtime is closed). Closed-product internals are not public — Kildall copies patterns, not code.
- **2026-09-27 (v34)** — **Phase 9 decisions from the user interview.** Hermes = **channels only** (no machine access; Kildall keeps its agent loop). Capture = **everything including keystrokes and screen text**, in a **new separate vault**, not a git repo; keystroke and screen logs encrypted at rest. Voice = **English + Vietnamese**; Kokoro lacks Vietnamese, so 9.3 picks a local Vietnamese TTS. Order = **Phase 9 last**, after 4, 4C, 5, 7 and 8. Workspace = **full autonomy, always**. Cloud = **as now, vault context included, except the raw keystroke log, which never leaves the machine**. Users = **personal now, paid clients later** — licence audit and per-client separation required before the first client. ⚠️ **Two risks accepted by the user and recorded:** vault content may reach free-tier cloud providers; outside content can trigger autonomous Workspace actions. Never-tier blocks remain in code regardless.
- **2026-09-27 (v33)** — **Kildall 100% defined: Phase 9, the agentic OS**, at user instruction. Kildall = engine, Obsidian = memory, Google Workspace = operating layer, plus a local voice layer, a wallpaper dashboard, and skill engineering with automations and evidence-gated self-improvement. Ten slices, 9.1–9.10. **Tools verified live:** Laya-MLX (Apache-2.0, 0.69–0.94 GB, 7–14 ms author-measured), Hermes Agent (MIT, 249k★), faster-whisper (MIT), Kokoro-82M (Apache-2.0). **Swap-out record:** `Qwen3-ASR-1.7B` → **faster-whisper** and `Qwen3-TTS-12Hz-1.7B` → **Kokoro-82M**, user choice — Kokoro is 82M and runs on MLX; ⚠️ faster-whisper is CPU-only on Mac, so 9.3 is gated on a measured latency with `mlx-whisper`/`whisper.cpp` as fallback. **Decision changes:** push-to-talk → **local wake word** (audio still never leaves the machine); content systems **back in scope** (out since 2026-09-05). 🔴 **Guardrails written in:** Hermes acts only through `permissions.execute`; the second-brain vault stays out of every git repo; captured activity is untrusted data and never goes to the cloud unasked; self-improving loops adopt a change only if it wins on the eval harness. 🔴 **A Google credential was pasted in chat; it was not written anywhere — revoke it.** ⚠️ RAM: the full stack is ~16–20 GB against ~20 GB usable — gated by a 10-minute soak.
- **2026-09-27 (v32)** — **Hugging Face mirror added to publishing**, at user instruction: after every push to GitHub `main`, run `kildall-hf-sync` to mirror that commit to `MinhDuc26121/kildall`. 🔴 **The pasted command `hf upload MinhDuc26121/kildall .` was not adopted as written:** run in `code/` it would have uploaded **155 GB**, including **154 GB of third-party weights** (breaking the v29 never-bundle-weights rule and several model licences) plus **858 MB of private `.session` logs and memory test data**. The script mirrors only the 48 git-tracked files of `origin/main` (**1.6 MB** at `70eb4e8`), adds `license: mit` front matter to the README, and refuses weights, databases, `.env` files and anything over 20 MB (guard tested). Also recorded under *Secrets*: the cloud key holding file must move into the Keychain in Phase 4.5.
- **2026-09-27 (v31)** — **Rename executed: Orbi is now Kildall.** Code `70eb4e8` merged to `main` via PR #3; GitHub repo `MinhDuc2612/Kildall` (old URL redirects); package `kildall`, commands `kildall` plus the `orbi` alias; MIT `LICENSE` added; logo `Klogo.png`. The user renamed the vault folder to `~/Kildall`, so every live path and the nuke allow-list now read `~/Kildall/code`. All gates held: recall, abstention, category, lane and callable JSON 20/20; tools 17/20 first-pass and 20/20 post-retry; CLI 18/18; hooks 5/5; nuke dry-run 0 outside `code/`. **The planning file names stay `Orbi*.md`** because the frozen `bench_cases.json` references `../Orbiplan.md`. **Historical entries below keep the name Orbi** — they record what was true then. ⚠️ **Three nightly backups were missed (Sep 25–27)**; the 03:00 run on Sep 27 still used the old paths and wrote nothing. A manual run of `local.kildall.backup` on 2026-09-27 succeeded (exit 0, `integrity_check` ok).
- **2026-09-26 (v30)** — **Product renamed to Kildall**, at user instruction, after Gary Kildall (CP/M; lost the IBM PC deal to Microsoft). **Why rename:** Netgear owns the "Orbi" trademark for networking products, a risk once the MIT code is published; "Perlis" was taken by `perlis.ai`, a near-identical "Secure Agent OS". **Kildall checked 2026-09-26:** free on PyPI, npm and Homebrew; `kildall.ai` and `kildall.dev` unregistered; 21 GitHub repos (top 2★); no AI product found. ⚠️ **Not a trademark search** — check USPTO and WIPO before publishing; it is a real person's name, so get legal advice before commercial use. 🔴 **Not executed yet — it runs as its own slice after Phase 4.3, never mid-slice.** Measured scope: **437 lines in 33 code files**, package `name = "orbi"`, the `orbi` command, repo `MinhDuc2612/Orbi`, the three planning files (121 mentions), `~/.config/orbi/`, the backup launchd label, and nuke's typed confirmation. **Rename slice rules:** keep an `orbi` command alias for one release; rename the GitHub repo (GitHub redirects the old URL); re-register the nightly backup; run the full frozen regressions afterwards with no score change allowed. ⚠️ **Whether to move the `~/Orbi` folder itself is open** — moving it breaks `.venv`, the launchd job, this vault and Claude's memory path, and the plan's nuke allow-list names `~/Orbi/code`. Default: **keep the folder, rename the product, command, package and repo.**
- **2026-09-26 (v29)** — **Orbi is licensed MIT**, at user instruction. Added to *Answer first* and risk 9. **Scope: Orbi's code only** — model weights are downloaded from their publishers, never redistributed, and keep their own licences, so MIT does not relicense Kimi K3, GLM-5.3 or any custom row. Rule added: **never bundle weights** in the repo or a release. `code/LICENSE` and the `pyproject.toml` licence field **do not exist yet** — recorded as a to-do for the next Codex slice, not claimed done.
- **2026-09-23 (v28)** — **`tencent/Hy4-preview` added to Lane C as model 8**, taking the library to **23 models · ~9.87 T · ~5.23 TB** (2.77 TB free on the 8 TB drive). **770 B total / 49 B active**, MoE with 256 routed + 1 shared expert, top-8 per token, 78 layers, 1M context, text-only, **Apache-2.0**, released **2026-08-28**. Measured claims: **SWE-Bench Pro 65.7 · GPQA Diamond 92.3 · Deep SWE 64.3 · Toolathlon 74.1**. **Lane C by arithmetic, not preference:** 49 B active × 0.5 bytes = **24.5 GB per token**, against ~20 GB usable RAM, so it cannot be resident — **~8.4 s/token on Thunderbolt 4, ~70 minutes for a 500-token answer.** 🔑 **It lands in exactly the same tier as `DeepSeek-V4-Pro-0813`** — also 49 B active, also ~8.4 s/token — **but at 385 GB against 800 GB, less than half the disk.** 🔴 **Blocked on runtime, not merit: no GGUF and no MLX.** It ships BF16 safetensors plus FP8 and deploys through vLLM or SGLang across 8 GPUs, tensor-parallel 8 — CUDA-oriented, **so it cannot run on Metal today.** This is the same wall that made candidate 2 *unsupported/unmeasured*, not a quality judgement. ⚠️ **It is also a preview**, and the standing precedent is Wan 3.0, held as a Phase 5 decision *because it is beta*. ⚠️ **Do not rank its 65.7 against Kimi K3's 76.8/93.4** — those are SWE-bench **Verified** and this is SWE-Bench **Pro**, a harder set; comparing them would be a real error. 🔑 **One genuinely interesting detail: it ships a built-in MTP layer for speculative decoding**, which is directly relevant to improvement **#1, cross-lane speculative decoding** — recorded as a revisit note only, since Metal speculative decoding already measured as a loss *even at 100% draft acceptance*. **Revisit conditions: a GGUF conversion appears, or Lane C moves off llama.cpp.** No phase, lane assignment or installed model changed.
- **2026-09-22 (v27)** — **Added #51, hardware auto-fit and auto-expand**, taking the list to **51**. It absorbs **#5**, generalising auto-quant into quant + lane + batch + context. **Orbi currently runs on exactly one computer** — every figure in this plan is a property of this Mac mini and none is read from the machine at setup. 🔑 **Lane assignment is already a hardware function** (`active_bytes` vs usable RAM), merely hardcoded, and 🔑 **`skill_catalog.py` already carries an *original* and a *preferred* pick per leaf**, so the data structure for expanding upward exists without having been named. ⚠️ Only **13 leaves** have a named alternative (56 in sample 1's research), so ~250 of 302 have nothing to expand into. 🔴 **The governing rule is shrink on arithmetic, grow only on evidence.** Fitting downward is safe because RAM is physics; expanding upward without **#13** would automate **unverified** upgrades, since only **46 of 302 leaves are benchmark-verified**. 🔴 Second trap: **bigger ≠ faster** — a 32 GB base M4 is still 120 GB/s, so capacity promotes lanes but accelerates nothing already resident. ⚠️ Third trap, already proved in this project: **active params are not residency** — Lane A is 4 B active, ~2 GB by arithmetic, **12.23 GB measured**, a 6× error — so the design must be **propose then verify**, which is the Phase 1 Lane A gate loop automated.
- **2026-09-22 (v26)** — **Phase 3 complete at commit `a2415b6`**, pushed and remote-verified. The permission boundary is a **closed typed executor** — an allow-list of actions, so an unknown action fails by default rather than needing a rule. **The hard test passed properly**: `SYSTEM_RULES=''` with *all* system messages omitted, a recursive-delete tool call emitted into the real `_run_turn` dispatcher, sentinel unchanged and the Never refusal persisted — so the boundary is code, not prompt. `orbi nuke` verified independently: **14,918 paths listed, 0 outside `code/`**, dry-run by default, typed `orbi` to confirm, live destructive path never exercised. ⚠️ **Two honest limits recorded rather than hidden.** (1) **Nuke refuses 3 outward `.venv/bin/python*` symlinks**, which is correct — following them would delete Homebrew's Python — but it means `code/` is **not completely removed**. The fix is to `os.unlink` the link itself, which never touches its target, gated on the **link's own** location via `os.lstat` rather than `realpath`. (2) **Install copies a local artifact only** — no pip, npm, hooks, scripts or dependency resolution; that belongs to Phase 4. Also scoped honestly: item 7 is **a data-boundary check, not measured model injection resistance**, and the guard-model item is **deferred to Phase 4** because it needs the web fetcher and Granite Guardian 4.1 8B, which is not on disk. Checklist now **14 of 156**.
- **2026-09-21 (v25)** — 🔴 **Computer mode added as Phase 4C. It was missing entirely.** The phrase
  "computer use" appeared **zero times** in this file and zero times in `Orbichecklist.md`, while
  `sample1/OrbiLLM/Orbi OSSLLM research.md` carries **four ✓-verified leaves** for it (lines 140, 141,
  269, 270) and `Orbimodels.md` assigns Qwen3.8-27B to it. **The same structural gap `UHWmini.md` had
  before v21: real benchmarked research with no phase that builds it and no item that tests it.**
  New research file: **`Researchhub/sample3/Orbicomputer.md`**. Checklist **Group 13C**, 14 items,
  taking the list to **156 items across 19 groups**. Phases 5–8 deliberately **not** renumbered.
  🔑 **The phase is governed by a security finding, not a capability one.** Measured prompt-injection
  success reaches **51% against computer-use agents and 100% against browser-use agents**;
  **system-prompt defences do not measurably help** and layered defences are still insufficient,
  because the root cause is architectural — **no trust boundary between user instructions and page
  content**. So computer mode is **opt-in, attended, never default**, and every action clears the
  Phase 3 tiers *before* the input event is synthesised. ⚠️ **The accessibility tree is auditable but
  still injectable** — pages hide instructions in `aria-label` that the snapshot passes through.
  **Two layers, A then B:** the macOS accessibility tree costs **0 GB and no vision model** because
  `AXUIElement` is text and Lane A already reads text; pixel vision is a **fallback only**, for canvas
  apps, games, remote desktops and images. 🔑 **Layer B does not want a big model** — a **Qwen 3B with
  a better prompt scored ~50% on Showdown-Clicks against ~20% for Qwen 72B**, and small fine-tuned
  grounders reach **70–80%** where large general models manage ~20%, so **the 27B-dense and 122B picks
  in the model list are the wrong shape** and `BrowserVLM` at **0.54 B with GGUF and a llama.cpp fork**
  is the right one. Tools verified live against the GitHub API, not search summaries:
  **`playwright-mcp`** (Apache-2.0, 37,435★) for the browser and **`openclaw/Peekaboo`** (MIT, 5,193★)
  for macOS. 🔴 **`comet-mcp` rejected despite prompting the whole phase** — it delegates to
  **Perplexity Comet, a proprietary cloud browser**, with no local fallback, and last shipped
  **2026-01-13**. 🔴 **`CursorTouch/macOS-use` rejected — no licence file at all.**
  ⚠️ **CU-0 is a genuine go/no-go:** whether Lane A's **4 B active** params can drive a GUI is
  **unmeasured**, and **BrowserOS excludes local models from agent mode entirely**. ⚠️ The research
  pass behind the file **lost its verification phase to a session limit (75 of 105 agents failed)**,
  so §2's table was hand-verified and §3/§4 are labelled unverified rather than merged as fact —
  per this project's own standing rule about quota-exhausted research.
- **2026-09-21 (v24)** — **Two techniques added after the user checked the plan against an external
  inference-speed article.** **(1) The bounded prompt cache was missing from the plan entirely** — the
  phrase appeared **zero times** — despite being **the biggest measured speed win in the project**,
  taking routing from 15.29 s to **~0.97 s warm, roughly 16×**. It lived only in `BENCHMARKS.md` and
  `CLAUDE.md`, so a session rebuilding from the spec would have lost it. Now in the model-load
  procedure with its flags (`--cache-ram 768 --ctx-checkpoints 3`), **the two smaller configurations
  that were tested and failed** — 256 MiB could not hold a 464.6 MiB prompt, and 512 MiB with one
  checkpoint could not rewind the sliding-window cache — plus the honest limits: **the product mean is
  5.06 s including cache misses, not 0.97 s**, and a long answer can evict the prefix. A stray
  line-break lost from an earlier edit in that same code block was repaired at the same time.
  **(2) Continuous batching added to Phase 4, tied to shared-mode subagents.** Correctly absent for
  Lanes A/B/C, which serve one request at a time — but **shared mode is exactly what it exists for**,
  and without it "shared" means *serialised*: agent 2 waits for agent 1's entire answer. Recorded with
  `-np <slots>`, the warning to **size slots by KV-cache RAM rather than desired agent count**, and the
  requirement to **measure p99 rather than throughput**, since batching speeds the aggregate while
  slowing any single answer. Verified already present: **KV-cache quantisation** and **quantisation**.
  **vLLM correctly excluded** — CUDA-oriented, not viable on Metal.

- **2026-09-21 (v23)** — **Recorded why DFlash 2 is excluded, after the user asked.** It appeared
  **zero times** in all three planning files, and the blanket "no speculative decoding on Metal" rule
  would have made Codex reject it without explanation. DFlash 2 is genuinely real — merged into
  llama.cpp main, **1.84× measured tok/s, byte-identical output** — so its absence needed a reason,
  not silence. Three independent ones, all from `sample3/dflash2 hwmini.md`: **no Gemma drafter
  exists** (drafters are model-specific; only Qwen3.8-27B ones are published), that file's own verdict
  that on this machine it runs **"only via MLX — NOT llama.cpp"** while Lane A runs llama.cpp, and the
  fact that its one supported model **Qwen3.8-27B was already rejected as dense** at a projected
  ~5.8 tok/s — even 1.84× leaves it under the 15 bar. Also strengthened the Metal rule with the
  research's actual mechanism: the loss holds **even at 100% draft acceptance**, because each draft
  step launches its own Metal kernel. **Revisit conditions written in**: a Gemma drafter appearing, or
  Lane A moving to MLX.

- **2026-09-20 (v22)** — **Plan brought back in line with the build; it was four facts behind.**
  The Lane A row still named **Qwen3.8-Flash-Next** as leader from a pre-measurement ranking — it
  actually **failed at 0.21 tok/s**, and Lane A is **Gemma 4 26B-A4B UD-IQ3_S at 29.33 tok/s**.
  **Phases 1 and 2 were both complete but unmarked** — Phase 1 at recall 20/20 and tools 20/20
  post-retry, Phase 2 at routing 19/20, commit `8b815f1`.
  **Recorded a live contradiction the plan was hiding:** the model-load procedure requires **DWQ
  4-bit**, but Lane A runs **UD-IQ3_S — 3-bit**, and 4-bit→3-bit is where quantisation damage becomes
  measurable. Codex's own numbers show it: **IQ3_S 17/20 first-pass against DWQ's 18/20**, and
  `BENCHMARKS.md` records that *"IQ3 additionally dropped the final period in t09's exact fact"* —
  **precision loss, not a prompting failure**. The fix is already on disk: **`UD-IQ4_XS.gguf`, 12.7 GB,
  downloaded and never benchmarked**. Also noted that **DWQ is MLX-only**, so the procedure's literal
  requirement cannot be met on the llama.cpp path the CLI is built on — IQ4_XS is the closest
  available, and switching to the `.safetensors` DWQ build would mean changing runtimes.
  **Phase 2's 15.71 s/decision against the 0.2 s spec is flagged as open** on the phase row.

- **2026-09-20 (v21)** — **Lane C's speed corrected from one flat number to a per-model range.** The
  plan said *"~25 s/token"* throughout; that is **Kimi K3's** figure applied to all seven giants, and it
  is wrong by up to **8×**. Token time tracks **active** params, not total: `DeepSeek-V4-Flash` wakes
  13 B per token against Kimi K3's 104 B. Real range **~2.2 s/token to ~17.9 s/token**, so a 500-token
  answer is **18 minutes on the Flash tier and 2.5 hours on Kimi K3** — only the two largest are
  genuinely "submit and walk away". Full per-model table in `Orbimodels.md`. **Kimi K3 stays in the
  plan** at user instruction; only the install order changed, Flash tier first. Also recorded that
  **active params are not RAM residency** — Lane A has 4 B active but measured **12.23 GB peak RSS** —
  and that the Flash tier's combined 15.5 GB active may allow **two giants to co-reside**, which is the
  precondition for cross-lane speculative decoding (#1).

- **2026-09-12 (v20)** — **"Beyond the plan" taken from 46 to 50** with a new *Efficiency & self-tuning*
  group. These fill genuine gaps rather than padding: **#47 prompt self-optimisation** — the list
  improved models and routing but **nothing improved Orbi's own prompts**, though a failed task teaches
  you about the instruction as much as the model; **#48 in-flight context compression** — #18
  consolidates *stored* memory while **nothing compresses the live conversation**, so a long Phase 4
  session fills 32K and truncates the very task being worked on; **#49 semantic answer cache** —
  recurring questions each cost a full inference today and **the embedding model needed to fix that
  already exists for memory**, making it the cheapest latency win on the whole list; and **#50 thermal
  and sustained operation** — `UHWmini.md` §8 covers it and **nothing used it**, which matters because
  ambient mode (#31) converts intermittent load into permanent load, and that is where #37's
  3.8–12.5× per-token energy cost actually lands.

- **2026-09-11 (v19)** — **"Beyond the plan" expanded from 8 items to 46**, at the user's request to
  hold nothing back, grouped into speed/hardware, quality, router, memory, agent, interface,
  reliability, security, learning and economics. Each carries what it buys and what it costs. **Three
  are marked do-first for the same reason — they are free now and impossible to backfill:** the **eval
  harness** (#13), without which Phase 7 gates model swaps on throughput alone and no other improvement
  can be proven; **outcome logging** (#14), the only path to ever verifying the 256 skill leaves that
  were never benchmarked; and **keeping the distillation pairs** (#42) from Phase 6 onward. The user
  accepted all three of the ideas that change what Orbi fundamentally is — **distillation**, which
  breaks the zero-training promise; **a second machine** via Thunderbolt clustering, the only direction
  not capped by 24 GB; and **ambient mode**, which turns Orbi from a tool into a presence. Recorded the
  dependency chain — **#13 → #35 and #5 · #11 → #2 and #16 · #14 → #17 · #22 → #21** — so the build
  order is visible rather than implied.

- **2026-09-11 (v18)** — **Four more future ideas added, and one pulled forward into the build.**
  🔑 **Grammar-constrained decoding (GBNF) is a now-item, not a future one** — recorded against the
  Lane A decision and Phase 4's tool layer, because it plausibly fixes the **18/20 exact-argument score
  measured 2026-09-09 without changing models**: a grammar makes an invalid tool call *unrepresentable*
  rather than merely unlikely, and llama.cpp already supports it. Added to *Beyond the plan*:
  **Lane C → Lane A distillation**, which turns discarded giant-model answers into a training set of
  the user's real work and is the closest thing to the project's original "clone the good models" goal
  — with the note that **the pairs should be kept from Phase 6 onward even if never trained on**;
  **task decomposition**, since the router classifies once while real requests span several skills;
  **per-project KV cache**, absent from the plan entirely; and **indexing `Researchhub/`**, because
  64 MB of the project's own research is invisible to the agent built on top of it.

- **2026-09-11 (v17)** — **Added a "Beyond the plan" section** recording the four ceilings Phases 0–8
  hit: **cross-lane speculative decoding** (Lane A drafts, Lane C verifies — the ban is narrower than it
  reads, applying to same-model drafting in llama.cpp on Metal, while **MLX supports it and nobody has
  measured a small drafter against a 2.8 T verifier on Apple Silicon**); **outcome-based routing**;
  **memory consolidation and decay**; and **a real eval harness**, which is the cheapest and which
  everything else depends on, since Phase 7 currently gates model swaps on throughput alone and **no
  check exists for quality**. Two **future-proofing** notes added inline — Phase 1 leaves schema room
  for `decay`/`consolidated`, Phase 2 logs routing outcomes — both a few lines now, both requiring live
  migration or months of lost data if deferred. **Neither is to be built yet.**
  Also fixed two real defects found while editing: **Phase 2 had no detail section at all** — the
  router, the core of Orbi, went straight from Phase 1 to Phase 3 — and **Phase 1's Lane A text was
  three successive edits mashed together**, naming three different leaders and a stale disk figure. It
  now records the actual Phase 1 results: **Flash-Next failed at 0.21 tok/s** (settling the biggest open
  question — mmap-paging a 180B/6B MoE on an M4 does not work), **Gemma passed at 29.33 tok/s but only
  18/20 on exact arguments** at a sub-spec IQ3_S quant, and **Granite 4.1 8B and Qwen3.8-27B + CMoE
  remain untested.**

- **2026-09-06 (v16)** — **Fixed a real structural gap the user caught: `UHWmini.md` had no execution
  path.** Its 955 lines are the project's designated most-important research, yet the plan carried its
  rules as a **standalone reference section that no phase ran**, `uhwmini-setup.sh` was referenced
  **zero times** in any planning file, and the 126-item checklist contained **no hardware items at
  all** — no quantisation, no KV-cache, no flag set. Phase 0 hit the wired limit only because the
  sysctl happened to sit in its command block. **Replaced the reference section with a
  "model-load procedure" that every phase touching a model must run**: once-per-machine setup
  (including the reboot-resets warning), once-per-model DWQ 4-bit quantisation, the standard
  `-lm mmap -fa on -ctk q8_0 -ctv q8_0 -c 32768` load, the three nevers (llama.cpp speculative decoding
  on Metal, the ANE, `--no-mmap`), and the 10-minute benchmark rule. **Phase 1 must apply it before
  measuring Lane A's gates, or the tok/s figure is meaningless.**

- **2026-09-06 (v15)** — **Phase 0 complete and independently verified**: `.venv` on Python 3.12.13,
  `mlx-lm==0.31.3` reporting `Device(gpu, 0)`, `check.sh` exiting 0, `orbi.toml`, `BASELINE.md`, clean
  tree, commit `d74481c` pushed to `github.com/MinhDuc2612/Orbi`. **`iogpu.wired_limit_mb` is now
  20480** — the user ran it. **Lane A re-ranked**: with the Trash emptied, free disk went 93.3 →
  **253.65 GB**, so **`Qwen3.8-Flash-Next` becomes candidate #1**. Converting a dense model was only
  ever the answer to a disk squeeze that no longer exists; Flash-Next needs **no conversion and carries
  none of CMoE's quality cost**. `Qwen3.8-27B + CMoE` drops to #2 as the fallback.

- **2026-09-06 (v14)** — **Two deferred decisions closed, per the standing rule that a flagged error
  is still an error.** **`Qwen3-VL-235B` dropped** — released **23 Sept 2025**, and **Qwen3.5's unified
  vision-language foundation outperforms Qwen3-VL**; both Lane A candidates are multimodal, so it
  earned none of its **118 GB**. **Embeddings switched to `microsoft/Harrier-oss-v1-27B`**, which ranks
  **#1 on multilingual MTEB-v2** (the newer benchmark), is **MIT**, and whose 0.6B already beats
  Qwen3-Embedding-0.6B; `Qwen3-Embedding-8B` led only the older MTEB. Costs 13.5 GB against 4.3 GB, so
  `Harrier-0.6B` remains the fast path. **Totals: 22 models · ~9.1 T · ~4.84 TB. Nothing unchecked.**

- **2026-09-06 (v13)** — **Version audit finished; every model in the list has now been checked.**
  Confirmed current: `Qwen3-ASR-1.7B`, `Qwen3-TTS-12Hz-1.7B`, `Qwen3-Embedding-8B` (still #1 MTEB at
  70.6) and `MiLMMT-46-12B` (Gemma3-based, path resolved to `xiaomi-research/`). **Three upgrades:**
  `Qwen-Image` → **`Qwen-Image-2512`** now that its weights have shipped under Apache-2.0;
  `Qwen3-Reranker-8B` → **`-4B`**, since the 4B **beats the 8B on MTEB-R (69.76)** at half the size;
  and **Harrier** documented as a three-model family (270M/0.6B/27B, MIT, 30 Mar 2026) that ranks
  **#1 on multilingual MTEB-v2**, so **its 27B may beat `Qwen3-Embedding-8B` — both get benched at
  Phase 1**. Lane B drops to **~130 B / ~67 GB**.

- **2026-09-06 (v12)** — **Version audit continued; five more stale picks corrected.**
  `PaddleOCR-VL` pinned to **1.6** (28 May 2026); `DeepSeek-V4-Pro` → **`-0813`** (GA 13 Aug 2026) and
  `-Flash` → **`-0731`** (31 Jul 2026); **Wan 2.7 superseded by Wan 3.0** (public beta 6 Aug 2026 —
  native 30-second 1080p with audio, kept as a Phase 5 decision since it is beta); **Hunyuan3D-2.1
  superseded by v3**. Confirmed current: `canary-qwen-2.5b` (most accurate open ASR, 5.63% WER) and
  `Qwen3-Omni-30B-A3B` — **Qwen3.5-Omni exists but is proprietary**. Also learned **Qwen3.8-Flash-Next
  is multimodal**, strengthening it as a Lane A candidate, and that **no Qwen 4 exists or is announced**.
  **7 models remain unchecked**, listed by name rather than assumed current.

- **2026-09-06 (v11)** — **Corrected a framing error the user caught: the internal-disk constraint was
  being applied to all three lanes when it only belongs to one.** **Lane A alone is sized against the
  internal SSD**, and permanently, not as a stopgap — it streams experts on every request, so disk read
  speed sets tok/s, and the internal disk is a measured **3.44 GB/s** against slower external
  Thunderbolt. **Lanes B and C are external-drive-bound**: Lane C is 4.9 TB and was never going on a
  500 GB internal disk, and Lane B has no speed argument since a specialist loads, runs for seconds and
  unloads. Also freed the **62 GB CrossOver Steam bottle** on user instruction, which takes internal
  free to **~155 GB once the Trash is emptied** and makes both Lane A candidates comfortable.

- **2026-09-06 (v10)** — **Disk resolved to 93.3 GB free** (from 64.9). Both Lane A candidates now fit
  — #1 comfortably, #2 with only 3 GB spare. **Correction recorded:** the earlier claim that 113.8 GB
  would be reclaimed was wrong; the true gain was **28.4 GB**, because `du` reports *logical* size on
  APFS and the HuggingFace cache and 180 git repos shared blocks, so `du` counted them repeatedly.
  A second wrong call is also corrected: the unreclaimed space was blamed on APFS snapshots, but
  `diskutil apfs listSnapshots` shows **no snapshots on the data volume** — block sharing was the whole
  explanation. The dead `Orbi-Tools` symlink is confirmed removed.

- **2026-09-06 (v9)** — **Three blockers worked through.** **(1) Stale models resolved:**
  `granite-guardian-3.x` → **Granite Guardian 4.1 8B** (April 2026, adds Bring-Your-Own-Criteria,
  Ollama `granite4.1-guardian`), and `Molmo-72B-0924` → **Molmo2 8B**, which is **1/9 the size and
  beats Gemini 3 Pro on video pointing (38.4 vs 20.0 F1)** — it moves from Lane C to Lane B and frees
  **36 GB**. The other three audit entries (`Llama-Guard-3`, `wildguard`, `bge-m3`) are **not used by
  Orbi**; better picks already hold those roles. Totals now **23 models · ~9.3 T · ~4.95 TB**.
  **(2) First real hardware number: `qwen3:8b` runs at 19.48 tok/s on this M4.** That sets the Lane A
  active-parameter budget at **≤ ~10 B active** for 15 tok/s, which every MoE candidate clears — and
  projects **unconverted dense 27B at ~5.8 tok/s**, so the decision to convert it is now backed by a
  measurement rather than architecture alone. **Granite 4.1 8B is a proven-viable floor.**
  **(3) Disk is the one blocker left** and needs commands only the user can run.

- **2026-09-06 (v8)** — Lane A resolved into **four live candidates** rather than one pick plus
  rejects, after the user caught a contradiction: the plan said *dense is convertible, not
  disqualified*, then rejected Qwen3.8-27B for being dense. **Qwen3.8-27B + CMoE is now the leader**
  — at ~17 GB it fits the real 89 GB free, keeps a native vision encoder and is Apache-2.0, where
  native-MoE Qwen3.8-Flash-Next at 90 GB misses by 1 GB. All three lane tables in `Orbimodels.md` were
  rewritten to one shape, grouped by job, **with stale models flagged in the table itself** —
  `granite-guardian-3.x` (Phase 3's guard, and Granite is on 4.1) and `Molmo-72B-0924` (two years old).

- **2026-09-05 (v7)** — **Two corrections.** **(1) The "no dense model in Lane A" rule was too strong**
  and is replaced: **dense is convertible, not disqualified.** **CMoE** converts a dense LLM to MoE
  **training-free in under five minutes**; the plan now states the order of preference — native MoE,
  then convert, then dense-as-is only if it fits — along with the measured cost (75% activation
  lossless but only 5% faster; 25% activation costs 33–65% perplexity; 1 hr LoRA recovers ~76%) and the
  blocking unknown that **CMoE on Metal is unverified**. **(2) Disk re-measured at the user's request:
  64.9 GB free, not 133 GB** — free space fell ~68 GB. **Lane A at 90 GB no longer fits**, which is now
  risk 8 with four ordered options, and Phase 1 must resolve it before downloading.

- **2026-09-05 (v6)** — **Lane A was dense. Corrected.** v5 picked a dense model, which contradicts
  the plan's own premise — sparsity is the only reason ~9.5 T fits a 24 GB machine, and a dense model
  fires every parameter every token. **A rule is now stated in "stored ≠ running": MoE only, no dense
  model in Lane A**, checked before quality. Lane A is **Qwen3.8-Flash-Next — MoE, 180B total, 6B
  active**, ~90 GB on disk and ~3 GB active, running today off the internal SSD at its measured
  3.44 GB/s. **The unmeasured risk is stated plainly:** no general MoE expert-streaming runtime exists
  for Apple Silicon, so it runs via `llama.cpp -lm mmap`, and **no tok/s figure for a 180B/6B MoE on an
  M4 has ever been published** — Phase 1 measures it before anything else. Also corrected the file's
  **Qwen-centric framing**: the rule is best model per skill by benchmark, **newest version of whichever
  family wins**. A version audit across all families found **five known-stale models**, four in the
  guard/embedding roles Phase 3 depends on, now risks 7 and 8.

- **2026-09-05 (v5)** — **Lane A decided: Granite 4.1 8B** (~4.3 GB), which ties Qwen3.5-9B for the
  top open model under 10B as of September 2026 and **leads it on tool calling** — Lane A's real job.
  Qwen3.5-9B is the fallback if routing accuracy falls short. **Code moved from `~/Projects/orbi` to
  `~/Orbi/code`** on user instruction, which forced a **rewrite of the `orbi nuke` spec**: the code now
  sits *inside* the research vault, so "never touches `~/Orbi/`" is impossible and is replaced by an
  allow-list of exactly one deletable path, with a dry-run test. Also flagged that `code/` must be
  excluded from Obsidian's indexer. **Phase 6 parked** — the 8 TB drive is not ordered and is 1+ month
  out, so Phases 0–5 and 7–8 are the build.

- **2026-09-05 (v4 — scope lock)** — Rewritten after a full requirements pass. **Scope changed
  materially: Orbi now replaces Claude Code entirely** — files, shell, git, skills, hooks, subagents,
  MCP, web — **and adds image, video, 3D and full two-way voice.** Twelve decisions recorded, each
  previously unspecified: **the router mechanism** is the Lane A model classifying into one of the 341
  skills (~0.2 s per request), which was the single biggest hole in v3; **code lives at
  `~/Projects/orbi`**, because the volume was verified **case-insensitive** and the old `~/orbi` would
  have been the same directory as the `~/Orbi` vault, letting `orbi nuke` delete the research;
  **subagents run in both modes**, shared by default with separate processes opt-in and hard-capped
  from free RAM; **media generation is queued**, never interactive; **cloud is used when necessary
  without asking**, rotating the 16 Cloudcall free-tier providers then falling back to local, never
  spending; **memory is global plus per-project**; **voice is push-to-talk with no always-on mic**;
  **sample 1's `OrbiOS/` and `OrbiIntelligent/` are out of scope**, archive only; **models are picked
  on evidence with licences flagged**, excluding only CC-BY-NC and non-commercial ones.
  **A new Phase 4 (agent layer) was inserted** and media moved to 5, giants to 6, improvement to 7,
  tool-set redo to 8 — phases 0–3 unchanged. **Two companion files created:** `Orbimodels.md`, the
  explicit 23-model list whose params and disk actually sum (**~9.3 T, ~5.0 TB**) replacing the soft
  "~26 models, ~4.9 TB", and `Orbichecklist.md`, **116 items** across 17 groups tagged P0/P1/P2, which
  exists because the agreed definition of done requires a real checklist. Also recorded the **RAM trap**
  — Lane A at 8 GB plus Qwen3-Omni at 15 GB is 23 GB of 24 — and the resulting rule to use the
  2.0 GB ASR+TTS pair for voice instead.

- **2026-09-05 (v3)** — **Risk 7 resolved: GLM-5.2 is 753 B total / ~40 B active**, verified against
  the Hugging Face card for `zai-org/GLM-5.2`. Sample 1's `~355 B` was **GLM-4.5's** figure carried
  forward under the wrong name; its two other rows said `744 B`, which is **GLM-5.3's** total. Phase 6
  (then Phase 6's predecessor) rewritten to state that the existing tooling is **sample-stage and must
  be redone during the build**, not inherited.

- **2026-09-05 (v2 — clarity pass)** — **The 25 s/token figure sourced, not asserted**, to the
  `kimi-k3-in-c` author's measured table, with the interpolation reasoning and three limits shown.
  **"Stored versus running" made the headline.** **Contradictions removed** — "15–40 tok/s" vs
  "15–20", "~25 models" vs "~26", and a stale session-cost figure.

- **2026-09-05 (v1)** — Design locked to **option A: Orbi runs the real giant models, unmodified, with
  no training of any kind.** Replaces the earlier plan of building one 4 T MoE by sparse upcycling and
  distillation. Recorded that **the giants cannot be merged** — different hidden sizes and tokenizers —
  so **Orbi is several models behind one interface, not one new model**, compensated by their real
  quality at zero training cost. Architecture set as three lanes.
