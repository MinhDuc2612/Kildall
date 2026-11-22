# Handoff — code_1.24 round 2 (written 2026-11-21 23:55 by Claude, job e23e6252)

**Status 2026-11-22 12:00: DONE (job b6c50591).** PR #16/#17 ported; gates pass (routing 20/20, recall 20/20 ×2, abstention 20/20, callable 20/20, tools 20/20 after retry, CLI 18/18); frozen eval 1/20 and 1/20, 0 ContextOverflow; README and CLAUDE.md updated; committed and pushed. Left: only the out-of-scope items in section 4.6 (downloads).

Paste this to start the next session:

> Read `/Volumes/ES2TB/Kildall/HANDOFF-code-1.24-round2-2026-11-21.md` and follow it. Finish code_1.24 round 2.
> Work until this session reaches 800k context, then write the next handoff the same way and stop.

## 1. Read first
1. `/Volumes/ES2TB/Kildall/CLAUDE.md`: standing rules at the top, then the log from "2026-11-21T13:04" to the end.
2. `/Volumes/ES2TB/Kildall/code_1.24/README-1.24.md` (measured state at `b3ecfac`).
3. The two main-branch fixes to port (code repo `/Volumes/ES2TB/Kildall/code`, read only):
   - PR #16, tool-result fitting: `git -C code diff ec3b17e c7c50ed -- kildall.py file_tools.py test_tool_result_context.py test_phase41.py`
   - PR #17, in-turn step compaction: `git -C code diff c7c50ed 3b3a4a9 -- kildall.py test_tool_result_context.py`
   - Do **not** port PR #18 (`tool-output-diet`, draft, not merged).

## 2. Rules
- **Fit rule:** a model is used only if it writes ≥ 2 tok/s at all times on this Mac (longest context, 600 s soak, measured). Lane A runs at `batch = 32` for this reason; do not raise it without a new soak.
- code_1.24 uses only models already on this Mac: cloud off. **No downloads** unless the user says so (3D, rerank and multilingual speech all need downloads).
- **Commit or push only on the user's word.** Ask once at the start: "Commit and push when all gates pass?" Push goes to `kildall` branch `workspace` after `code/.venv/bin/python code/.session/workspace-freeze-20261107/vault_audit.py HEAD <new-label>` finds 0. Never stage the `code` link (it points at the PR #18 branch).
- **Quiet Mac before live tests:** no other `llama-server` (Flash-Next on 8099 and Inkling on 8082 appeared on 2026-11-21), Colima VM off, still wallpaper (Aerial video slows the GPU), swap ≤ 3 GB, `iogpu.wired_limit_mb` = 20480 (`test_routing --live` refuses 22528). Never stop the user's processes and never run sudo: ask, with the exact command.
- Edit and test in the main folder `code_1.24` (the worktree is stale). Run tests with `.venv/bin/python` inside `code_1.24`.
- Log every action in `CLAUDE.md` with the time from `date`. Output style ELIS.

## 3. State at handoff
- Vault `reroot-usb` = `kildall/workspace` = `b3ecfac` (plus this handoff and the last log lines, uncommitted if the push below did not happen).
- code_1.24 passes: `test_cli` 18/18, live routing 20/20, the 8 no-model tests; fit soak Gemma batch 32 pass (worst 2.48 tok/s), Bolt pass (20.26).
- code_1.24 was copied from main on 2026-11-04, so it has **no** `trim_tool_result` (PR #16) and **no** `tool_step_summary` (PR #17). On main these removed the ContextOverflow stops in long tool jobs.
- code_1.24's `fit_messages` already differs from main: it takes `limit`/`room` for big local models and keeps recalled memory in the user message. Keep both when porting.
- Frozen gates (recall, abstention, callable/tools) last ran 2026-11-06 at batch 128 (`code_1.24/.session/gates-20261106/`).

## 4. Done means (all of these)
1. PR #16 and #17 behaviour ported into `code_1.24/kildall.py` and `file_tools.py`, with main's focused tests adapted (`test_tool_result_context.py`) passing, and the 8 no-model tests + `test_cli` passing.
2. Frozen gates re-run on code_1.24 at batch 32 with the 2026-11-06 scripts: recall 20/20 on one slot and the work slot, abstention 20/20, callable 20/20, tools 20/20 after retry. Live routing 20/20 again.
3. The frozen 20-task repo eval (#112) run twice on code_1.24 (harness at code `ff20e40`, `repo_eval/`, collector pattern in `code/.session/compaction-fix-20261114e/`). Each run is ~3.5 h. Report score, tool calls and stop reasons per run; main for comparison: PR #17 0/20 and 0/20, PR #18 2/20 and 1/20.
4. README-1.24.md and CLAUDE.md match the results.
5. Committed and pushed on the user's word.
6. Not in scope unless the user asks: 3D, rerank and non-English speech (downloads).

## 5. At 800k context
Stop new work. Write `HANDOFF-code-1.24-<date>.md` in this same shape (paste line, read list, rules, state, done list with what is left), log it in CLAUDE.md, and tell the user the paste line.
