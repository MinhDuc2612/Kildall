# Kildall-27b — one model has it all

**v1 · 2026-11-22.** Sub-project of Kildall. Design approved by the user 2026-11-22 (12 questions, answers below).
Research: `Researchhub/sample4/kildall27b-methods.md`. Main plan: `Orbiplan.md` (section "Kildall-27b").

---

## ⚡ ANSWER FIRST

| | |
|---|---|
| **What** | Every Kildall feature (agentic OS, computer use, tools, memory, voice, media) driven by **one brain: Swift-1.5-Qwen3.8-27B**. No router, no "best model per task". |
| **Model** | `/Volumes/ES2TB/AI-Models/Swift-1.5-Qwen3.8-27B-Q4_K_M/Swift-1.5-Qwen3.8-27B-Q4_K_M.gguf` (17.4 GB, dense 27B, MTP head inside). The plain Qwen3.8-27B GGUF is gone from disk. |
| **Speed today** | 5.46 tok/s write (measured 2026-11-01, b10809). Passes the fit rule (2+ tok/s); long prompts not measured yet. |
| **Best known speedup** | DFlash 2 on MLX: 11.7-12.2 tok/s on a 24 GB M4 mini (one blog). llama.cpp drafting on build 12359: **not measured; slice 27b-1 measures it.** |
| **Not on this Mac** | **Splash** (needs 36 GB+, 48 GB recommended). **Sparse attention** gives no gain at 4K-32K on this model (test only). |
| **Code** | Branch `kildall-27b` of `MinhDuc2612/Kildall`, worktree folder `/Volumes/ES2TB/Kildall/code_27b`, started from main. **Never merged into main.** |
| **Priority** | Side track. Main Kildall goes first; Kildall-27b uses the Mac when main has no tests running. |
| **Done** | Every feature works on the 27B and passes its gates. The frozen 20-task test runs twice and the score is recorded. **No minimum score.** |
| **Licence** | Swift Open License v1.0: free under US$1M gross yearly revenue; above that a Swift Enterprise Licence is needed (paid clients, Phase 9.10). |

---

## The user's answers (2026-11-22)

1. **One brain.** The 27B is the only language model that thinks, plans, codes, uses tools and drives the computer.
   Helpers are allowed: each job always uses the same fixed helper. Nothing picks between models or helpers.
2. **Vision projector allowed** and counted as part of the 27B.
3. **Start from a copy of main `code`.**
4. **Cloud kept as one fixed backup** (not a per-task picker).
5. **Speed gate = the fit rule only:** 2+ tok/s at all times, longest allowed prompt, 600 s soak. Every other speed
   number is measured once on the 27B and becomes its baseline. Quality gates stay as they are.
6. **Research now only the 27B's own methods**; everything else stays in Phase R step R2.
7. **Swift-1.5** (the 27B on disk). If the projector or drafter does not work with it, ask the user again
   (option: download plain Qwen3.8-27B, ~16.5 GB).
8. **Small downloads allowed**, each 2 GB or less, belonging to the 27B (projector, drafter). Name and size are told
   to the user before each download.
9. **Branch `kildall-27b` in its own worktree folder `code_27b`.**
10. **Side track**: main Kildall first.
11. **Done = every feature passes its gates; score recorded, no minimum.**
12. **This file** + a pointer section in `Orbiplan.md` + Group 21 in `Orbichecklist.md`.

---

## Architecture

- **One llama-server (Homebrew build 12359 or newer)** runs Swift-1.5 + the vision projector + a drafter
  (the drafter only if slice 27b-1 measures a gain).
- **Own ports 8423 (model) and 8424 (Harrier).** Main uses 8123/8124, code_1.24 uses 8223-8225.
- **No router.** No classifier, no router slot, no router warmth. Every request goes straight to the 27B.
  Prompt reuse (`cache_prompt`, slice 5b2) stays.
- **Slots:** start with 1 (`--parallel 1`, needed for MTP). Shared subagents run one at a time unless a 2-slot
  setting passes the fit rule and the soak.
- **Fixed helpers (tools the 27B calls):**

| Job | Helper | Notes |
|---|---|---|
| Memory search | Harrier 0.6B (0.4 GB) | already in main |
| Read text in an image | macOS Vision (no model) | fast path; the 27B's own vision answers questions about images and screens |
| Hear | whisper (`ggml-base.en`) | English only today; a multilingual model needs the user's OK |
| Speak | Kokoro-82M | no Vietnamese voice |
| Images and video | SwarmUI (ComfyUI) | **the 27B is stopped while SwarmUI runs**; memory is freed after each job |
| Cloud backup | LLM7, then NVIDIA NIM Nemotron 3 Ultra (fixed order) | only when the 27B fails or the request does not fit |

- **Guard:** Granite Guardian cannot fit next to the 27B, so the 27B checks risky outside content itself
  (Phase 4.5 threat rules still apply; code-level Never tiers unchanged).
- **Council (4.5d) removed**: several models voting is "picking another model". The one-model form (the 27B answers 3 times and votes) was offered and **declined by the user 2026-11-22**.

## Memory budget (20 GB GPU limit)

| Part | Size |
|---|---|
| Swift-1.5 Q4_K_M | 17.4 GB |
| Vision projector | ~0.6-0.93 GB |
| Drafter (DFlash 2 at 4-bit / MTP head inside the model) | ~1 GB / 0 GB |
| Harrier | 0.4 GB |
| **Total before the prompt cache** | **~19.7 GB** |

Too tight. Slice 27b-1 measures the real peak. If it does not fit: drop the drafter first; then ask the user about a
smaller Swift file (Q4_K_S 16.4 GB, IQ4_XS 15.5 GB). That download is over 2 GB, so it needs the user's OK.
Only 16 of the 64 layers keep a growing KV cache, so the cache is small for a 27B.

---

## Build slices (each one draft PR into `kildall-27b`; gates run; Claude reviews and merges)

| Slice | What | Gate |
|---|---|---|
| **27b-0 Setup** | Worktree `code_27b` on branch `kildall-27b` from main. `CODE_ROOT`, nuke root, ports 8423/8424, DB and backup names for `code_27b`. `kildall.toml` model = Swift-1.5. Router, catalog dispatch and Lanes B/C removed. Tests adapted. | all controls pass, `check.sh` 0, nuke dry-run 0 outside |
| **27b-0b Qwen tool calls** (added 2026-11-22) | `tool_runtime.py` / `tool_grammar.py` build only Gemma 4 native tool calls; a live turn on the 27B stops with `Expected the pinned Gemma 4 native chat template`. Add a Qwen3.8 tool-call path (schema-constrained), keep the Gemma path's tests. | one live turn with a tool call works; controls pass |
| **27b-1 Speed + memory** | On build 12359: plain, MTP (`--spec-type draft-mtp --spec-draft-n-max 2`), DFlash 2 (`--spec-type draft-dflash`). Greedy output identical with and without the drafter. Longest context (8K/16K/32K) that passes the fit rule in a 600 s soak. Peak memory. | fit rule worst case; 0 critical pressure, 0 GPU OOM |
| **27b-1b MLX (only if 27b-1 drafting fails)** | Measure DFlash 2 on MLX with the memory it needs. **The user decides** before any MLX rebuild. | user decision |
| **27b-2 Vision** | Download the projector (name and size first). Test with Swift-1.5: image questions, text in images, screenshots. | fixed test images answered right; fit rule still holds |
| **27b-3 Quality gates** | Recall 20/20 (one slot), abstention 20/20, callable 20/20, tools, CLI 18/18, frozen 20-task test x2 (score recorded). Routing gate replaced by: every request reaches the 27B. | as main; score recorded |
| **27b-4 Phase 4.5** | Cloud backup (fixed order), 27B self-guard, deep research on the 27B. | 4.5 gates |
| **27b-5 Computer use (4C)** | Accessibility tree first, screenshots with the 27B's vision second. Opt-in, attended. | Group 13C items |
| **27b-6 Media + voice** | SwarmUI images and video (27B stopped during jobs), whisper + Kokoro. | media and voice items |
| **27b-7 Agentic OS (Phase 9)** | Every Phase 9 slice that does not need per-task model picking, on one brain. | Group 19 items |

Main fixes are merged into `kildall-27b` from time to time (normal merge, no force).

---

## Methods (from the 2026-11-22 research)

| Method | Use in Kildall-27b |
|---|---|
| **MTP head (inside Swift-1.5)** | Measure in 27b-1. On an old build it was slower on this Mac (prose -24%, code -4%); the new Metal kernels may change that. |
| **DFlash 2** | Measure in 27b-1 with a GGUF drafter on llama.cpp; the known GGUF build targets a fork (BeeLlama.cpp). MLX gave 1.8-1.9x here. |
| **Metal few-row MMA kernels** (llama.cpp #29869, #30065, in b11404+) | The reason old "drafting loses on Metal" numbers must be measured again. |
| **Swift-1.5 short reasoning** | ~24.5% fewer thinking tokens (vendor). Real speed at 5 tok/s. |
| **Splash** | Not on this Mac. Revisit only on a Mac with 48 GB or more. |
| **Sparse attention** | llama.cpp Metal sparse FA needs a sparse-trained model and is off for Qwen. Training-free sparse prefill helps only at 64K+. Test once in a long-context slice; no gain expected now. |

---

## Change Log

- **2026-11-22 (v1)**: Created after 12 questions and one research pass (user: "1 model to have it all no feature of
  choose the best model per task"). Design approved by the user.
- **2026-11-22**: User confirmed: every Kildall feature except per-task model choice; council left out (also its one-model form).
- **2026-11-22 (27b-0 built)**: worktree `code_27b`, branch `kildall-27b` (= main `ff20e40`) + slice branch
  `kildall-27b-0-setup` `f7cbc5d`, draft PR #19. Gates: 27/27 controls, `check.sh` 0, nuke dry-run 13,864 / 0 outside /
  0 refused, history scan 0 findings. Kept on purpose: section name `lanes.a` (= the 27B), runtime b10809 (27b-1 tests
  12359), slot code unchanged (at 2 slots, slot 0 stays idle: review in 27b-1). Live smoke found the Gemma-only tool
  layer: new slice **27b-0b**.
- **2026-11-22 (27b-0 merged)**: independent review found 1 blocker (`setup_kildall.py` wrote through the `.tools` link into
  main's `code/.tools`); fixed in `0a111c3`, 34/34 gate steps, merged into `kildall-27b` (fast-forward). `main` untouched.
- **2026-11-22 (27b-0b built)**: Qwen XML tool calls, own GBNF (way b), draft PR #20 `a2df31a`. Live: one exact
  `read_file` call per tool turn, 5.3 tok/s; product tool turn 20.7 s. Open quirk: the first plain reply once added stray
  `</parameter></function></tool_call>`; not reproduced in 4 later turns.
- **2026-11-22 (27b-0b merged)**: review no blockers; fixes `6778224`; 39/39 gate steps; `kildall-27b` = `6778224`.
  Next: 27b-1 (handoff `HANDOFF-kildall-27b-round3-2026-11-22.md`).
- **2026-11-23 (27b-1 measured)**, build 12359, product Lane A flags, evidence `code_27b/.session/27b-1-20261122/`.
  Write tok/s code/prose at 8K: plain 5.88/5.83 · MTP n2 10.91/8.13 · MTP n3 13.25/8.22 · DFlash n7 20.93/9.02 ·
  DFlash n3 14.12/8.78. Code text identical to plain for all; prose splits at one near-tie word, and the plain server
  picks the drafters' word itself when it reads the same prefix in a batch (40.4% vs 37.8%): batch math, not a drafter
  error. Fit soak (600 s, >= 2 tok/s, 0 critical, 0 GPU OOM): plain 32K pass (5.20 tok/s, 17.52 GB), MTP n3 32K pass
  (8.08 tok/s, 18.07 GB, 6 warning samples), DFlash n7 32K **OOM**, DFlash n7 16K pass (18.38 GB, 101/120 warning
  samples). Render on 12359 identical to b10809; tool turn works. Recall gate wrapper `test_recall_27b.py` added.
  The written gate "greedy output identical" fails literally for every drafter; adoption waits for the user.
- **2026-11-23 (27b-1 adopted, draft PR #21)**: user chose **MTP n3 at 32K** on Homebrew build 12359 (`kildall-27b-1`
  `96926b7`). Gates: controls pass after review fixes; smoke clean; **recall 19/20** (18/20 on the old b10809 4K config).
  Not merged: recall 20/20 and review should-fix items first (see handoff round 4).
