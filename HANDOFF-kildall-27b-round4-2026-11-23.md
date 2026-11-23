# Handoff — Kildall-27b round 4 (2026-11-23)

Read `CLAUDE.md` (top rules + entries from 2026-11-22T22:40 on), `Kildall27b.md` (Change Log end), PR #21 body.

## State

- `kildall-27b` = `6778224` (unchanged). `main` = `ff20e40` (unchanged). Worktree `code_27b` on `kildall-27b-1`.
- **Draft PR #21** `kildall-27b-1` = `96926b7` → `kildall-27b`: Homebrew llama.cpp build 12359, MTP n3 drafting,
  32K context (user chose this, 2026-11-23 06:50), `test_recall_27b.py` (frozen recall on ports 8423/8424, 20/20 rule).
- 27b-1 measured (evidence `code_27b/.session/27b-1-20261122/`): write tok/s code/prose plain 5.88/5.83, MTP n3
  13.25/8.22, DFlash n7 20.93/9.02. Fit soak 32K: plain pass, MTP n3 pass (8.08 tok/s, 18.07 GB), DFlash n7 OOM.
  Drafted text = the 27B's own batched output (near-tie proof in `tie.json`).
- DFlash drafter on disk: `/Volumes/ES2TB/AI-Models/Qwen3.8-27B-DFlash2-GGUF/Qwen3.8-27B-DFlash2-Q4_K_M.gguf` (unused).
- Gates on `49002b2`: 36/40; 3 controls fixed in `96926b7` (pass). Smoke clean (stray-tag quirk not seen).

## Next (in order) — ask the user before long Mac runs

1. **Should-fix items from the review**, then the full gate plan again (tools below):
   - reuse path: store `server` + `server_build` in `services.json`, refuse reuse when they differ (kildall.py ~241-253);
   - GBNF acceptance tests (`test_tool_grammar.py:23`, used by `test_qwen_tools.py`) also against 12359
     `/opt/homebrew/Cellar/llama.cpp/1.0.0/lib/libllama.dylib` (check symbols first);
   - `setup_kildall.py` checks the configured `server` + `server_build`; `test_recall_27b.py` checks embedding port 8424.
2. **Evidence gaps under MTP**: 600 s soak at 32K with Harrier running too (product as run); one grammar tool turn and
   one 2-turn prompt-reuse smoke with drafting on.
3. **Recall 20/20** (slice 27b-3 work, but PR #21 waits on it per review): 19/20 on MTP 32K (recall-15 `orchard_test` →
   `UNKNOWN`, fact retrieved). Find the cause first (prompt wording? near-tie?), no symptom patch. Frozen files stay frozen.
4. Fresh review agent → merge PR #21 into `kildall-27b` when gates are green (builder ≠ reviewer).

## How to run things

- Copy `run_list.py`, `launch.sh`, `bench27b.py`, plan JSONs from `code_27b/.session/27b-1-20261122/tools/` to
  `$CLAUDE_JOB_DIR/tmp/` (launchd cannot use plist/logs on exFAT). Full gate plan: `plan-27b1-gates.json`
  (40 steps incl. `test_recall_27b`). Change `out` per run.
- Edit no file while a gate run is going (a run reads the working tree).
- Read the DB by copying `code_27b/kildall27b.db*` to scratch. History scan before push:
  `code/.venv/bin/python code/.session/reroot-usb-20261102/secret_audit.py history-code <label>`.
- Stop before about 800k tokens of context and write the next handoff.
