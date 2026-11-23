# Handoff — Kildall-27b round 5 (2026-11-23)

Read `CLAUDE.md` (top rules + entries from 2026-11-23T19:04 on), `Kildall27b.md` (Change Log end), PR #21 body + last comment.

## State

- `kildall-27b` = `6778224`, `main` = `ff20e40` (both unchanged). Worktree `code_27b` on `kildall-27b-1` = `27ae6ee` (pushed).
- **Draft PR #21** `kildall-27b-1` → `kildall-27b`: build 12359, MTP n3, 32K, review should-fix items done.
  Gate run `code_27b/.session/gates-r4/` (46 steps): all pass except `test_recall_27b` 19/20. Soak with Harrier: pass.
- **User decision 2026-11-23 19:36: recall gate stays 20/20; PR #21 stays unmerged** until a thinking-on slice passes 20/20.

## Facts found in round 4

- Recall request = frozen SYSTEM + product `SYSTEM_RULES` (added by `benchmark.chat`, not frozen). `SYSTEM_RULES` holds a
  Gemma-era sentence naming recall-18's case ("a release coordinator owns the release checklist").
- `gates-r4/probe_recall.json`: recall-15 `UNKNOWN` 94% vs `orch` 4% (clear); thinking on → `orchard_test` in 110 tokens.
  recall-18 near-tie 49% vs 47.5%; thinking on → right in 311 tokens. Frozen test caps answers at `max_tokens=64`.
- Prompt reuse: every new turn re-reads the whole prompt (~2,300–2,600 tokens, ~45 s at 55 tok/s); only the in-turn tool
  follow-up reuses. `-cms 256` did not change it (`.session/cms-256/`, diff kept, not committed). Turn 3 prompt was shorter
  than turn 2, so turns are not plain extensions. Cause open.

## Next (in order) — ask the user before long Mac runs

1. **Slice 27b-3 design (brainstorm with the user first):** thinking-on memory answers. Questions to settle:
   when to think (only when recalled memories are in the turn? always?), reasoning budget, how the frozen 64-token cap is
   honoured (reasoning budget counted apart from the answer, frozen file byte-identical, argued in the PR), and whether to
   drop the Gemma-era recall-18 sentence from `SYSTEM_RULES` for 27b. Gate: frozen recall 20/20 (twice, to rule out the
   recall-18 coin flip), plus all other gates. Then fresh review → merge PR #21 + slice.
2. **Prompt-reuse slice (speed, separate):** find why turns share no prefix. Steps: dump the rendered prompt of 3 turns
   (server `/apply-template` with the exact `kildall` request bodies), find the first differing token, check whether
   checkpoints are made at all (`LLAMA_ARG_LOG_VERBOSITY` or `-lv`), then fix at the root. Worth up to ~40 s per turn.

## How to run things

- Tools: `code_27b/.session/gates-r4/` has `plan-r4.json` (46-step gate plan), `bench27b.py` (`soakh` = soak with Harrier),
  `probe_recall.py`, `apply_cms.py`; `run_list.py` + `launch.sh` in `.session/27b-1-20261122/tools/`. Copy to
  `$CLAUDE_JOB_DIR/tmp/` first (launchd cannot use plist/logs on exFAT); change `out` per run.
- `test_cli.py` is not in the 27b plan; its `control_checks()` (incl. the new reuse cases) passed on `27ae6ee` (`.session/cli-controls-r4/`). The real-model part of `test_cli` has never run on 27b.
- Edit no file while a run is going. DB: copy `code_27b/kildall27b.db*` to scratch; `orbi_inference` has `cache_n`/`prompt_n`.
- History scan before push: `code/.venv/bin/python code/.session/reroot-usb-20261102/secret_audit.py history-code <label>`.
- Stop before about 800k tokens of context and write the next handoff.
