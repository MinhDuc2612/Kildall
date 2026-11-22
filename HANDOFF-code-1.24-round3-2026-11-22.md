# Handoff — code_1.24 round 3 (written 2026-11-22 12:10 by Claude, job b6c50591)

Paste this to start the next session:

> Read `/Volumes/ES2TB/Kildall/HANDOFF-code-1.24-round3-2026-11-22.md` and follow it. Add the missing code_1.24 features, then raise the eval score.
> Work until this session reaches 800k context, then write the next handoff the same way and stop.

## 1. Read first
1. `/Volumes/ES2TB/Kildall/CLAUDE.md`: standing rules at the top, then the log from "2026-11-21T23:56" to the end.
2. `/Volumes/ES2TB/Kildall/code_1.24/README-1.24.md` (measured state at `c778bbe`).
3. Round 2 evidence: `code_1.24/.session/gates-20261122/`, `code_1.24/.session/eval-20261122/` (eval runs in `frozen/.session/run-1`, `run-2`: `results.json`, per-task `transcript.jsonl`).
4. Main's draft PR #18 ideas (not merged; read only): `git -C /Volumes/ES2TB/Kildall/code diff ff20e40 f07cbd3 -- kildall.py file_tools.py permissions.py`.

## 2. Rules
- **User words (2026-11-22 12:05):** "add missing features then raise eval score". Downloads for the three missing features are allowed. Still show the pick, licence and size before each download, and log them.
- **Pick by benchmark** for that exact skill, newest version, open licence; popularity does not count. Everything must pass the **fit rule** on this Mac (LLMs: ≥ 2 tok/s at the longest context, 600 s soak; media/3D/speech jobs: must finish, peak swap recorded). Models go to ES2TB (`/Volumes/ES2TB/AI-Models`, 1.2 TB free). Cloud stays off. Never paid.
- **Commit and push only on the user's word.** Ask once: "Commit and push when all gates pass?" Push goes to `kildall` branch `workspace` after `code/.venv/bin/python code/.session/workspace-freeze-20261107/vault_audit.py HEAD <new-label>` finds 0. Never stage the `code` link or `Researchhub/sample3/texthuman copy.md`.
- **Quiet Mac before live tests:** no other `llama-server`, Colima VM off, still wallpaper, swap ≤ 3 GB (eval admission refuses above 3e9 bytes), `iogpu.wired_limit_mb` = 20480 (it flipped to 22528 twice on 2026-11-21/22, setter unknown; gates refuse it). Never stop the user's processes and never run sudo: ask, with the exact command. Kildall-started SwarmUI/ComfyUI may be stopped with its `ShutdownServer` API (it held 1.2 GB of swap after a video job).
- **Run tests under launchd `ProcessType=Interactive`**, not from the Claude shell: a Claude background job leaves `._name` files beside every new file on exFAT (breaks `turn_completes`), and plain `launchctl submit` jobs get throttled timers. Scripts: `code_1.24/.session/round2-20261122/tools/` (`launch.sh <label> <plan.json>`, `run_list.py`; plans are JSON step lists; the old plans point at the job folder `~/.claude/jobs/b6c50591/tmp`, which may be gone — rewrite paths).
- **Eval** must run with `code_1.24/.session/<eval dir>/frozen/.venv/bin/python` (the verifier sandbox cannot load numpy from code_1.24's venv). Each attempt needs a fresh eval folder: `eval_run.py` refuses an existing `run-N` and `eval-N-started.json`. Build it like `tools/prep_eval.py` (copy `frozen/` without `.session`, collectors), then write `source.json` = current product hashes, `post-live-summary.json` after the gates pass, then run `eval_control.py`.
- Log every action in `CLAUDE.md` with the time from `date`. Output style ELIS.

## 3. State at handoff
- Vault `reroot-usb` = `kildall/workspace` = `c778bbe` (plus the last log lines, uncommitted unless the handoff push below happened).
- code_1.24 has main's PR #16 + #17 (tool-result fitting, step compaction). Lane A Gemma 4 26B-A4B, 2 × 32768, batch 32, ports 8223/8224.
- Gates 2026-11-22 all pass: live routing 20/20, recall 20/20 one slot + work slot, abstention 20/20, callable 20/20, tools 17 → 20 after retry, `test_cli` 18/18, 8 no-model tests + `test_tool_result_context.py` + `test_phase41.py`.
- **Eval baseline: 1/20 and 1/20** (`disabled-interval-clock` both times), 478 and 459 tool calls, 0 ContextOverflow. Failure picture: 56 % and 63 % of calls repeat an earlier call exactly; 72/234 and 152/254 edit/write calls return an error; 8 truncated tool calls (ValueError); 15 tool-cap and 5 wall-cap stops.
- Missing features (README "Known limits"):
  - **3D:** `/Volumes/ES2TB/AI-Models/comfyui/diffusion_models/hunyuan_3d_v2.1.safetensors` is already on disk (2026-11-08; shape only on Mac, texture needs CUDA). Check whether SwarmUI/ComfyUI can run it before downloading anything.
  - **Rerank:** none on disk. Plan pick: Qwen3-Reranker-4B (`Orbimodels.md`); check newer/better by benchmark.
  - **Speech in other languages:** only `ggml-base.en.bin`. `OmniVoice-bf16` (TTS, Vietnamese unchecked) is on disk. Pick a multilingual ASR (Vietnamese + English) and check Vietnamese TTS.

## 4. Done means (all of these)
1. 3D, rerank and multilingual speech each work through a real `kildall ask` job (route, README line, test), passing the fit rule; downloads logged with licence and size.
2. Eval score raised on evidence: change one lever at a time (ideas: #108 repeat-call breaker, #98 loop breaker, #107 edit errors that show the near-miss text/indentation, keep findings in step summaries, PR #18's plain grep rows and bounded summaries). Keep a change only if both runs together beat 2/20 (the round 2 total) and no gate drops. Report score, tool calls, repeats, edit errors and stops per run.
3. After each kept change: 8 no-model tests + focused tests + `test_cli` + gates (copy `gates-20261122`, new `source.json`) + live routing, then eval × 2 (about 2–2.5 h each).
4. README-1.24.md and CLAUDE.md match the results.
5. Committed and pushed on the user's word.

## 5. At 800k context
Stop new work. Write `HANDOFF-code-1.24-<date>.md` in this same shape (paste line, read list, rules, state, done list with what is left), log it in CLAUDE.md, and tell the user the paste line.
