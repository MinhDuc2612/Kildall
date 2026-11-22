# Handoff — Kildall-27b round 3 (2026-11-22, night)

Read `CLAUDE.md` (top rules + last 2026-11-22 entries), `Kildall27b.md`, `code_27b/README-27b.md`.

## State

- `kildall-27b` = `6778224` (pushed). Never merged into `main` (`ff20e40`).
- **27b-0 merged** (PR #19, review blocker fixed in `0a111c3`). **27b-0b merged** (PR #20): Qwen XML tool calls,
  own GBNF, family picked by the prompt's Swift ending. Worktree `code_27b` is on branch `kildall-27b-0b` (= `6778224`).
- Live: `kildall ask` tool turn works (`read_file` Auto → right answer). Gates `6778224`: 39/39
  (`code_27b/.session/gates-0b-2/`).
- Open quirk: the first plain reply once printed `READY` + stray `</parameter></function></tool_call>`; not seen in 5 later
  plain turns. Watch for it; if it repeats, think about a fix (no symptom patch without a cause).
- Review nits not fixed: unused `orbi_routes`; cloud `catalog_model` only from tests; removed `job submit`/`--explain`
  give generic errors; `work_slots` keeps slot 0 aside at parallel>1; duplicate unused grammar rules; frozen
  `test_recall.py` still on 8123/8124 (refuses in 27b; 27b needs its own recall gate wrapper, not an edit to the frozen file).

## Next (in order)

1. **Ask the user before taking the Mac** (main Kildall goes first; 27b-1 needs long runs).
2. **Slice 27b-1 speed + memory** (row in `Kildall27b.md`): Homebrew build 12359 — plain, MTP
   (`--spec-type draft-mtp --spec-draft-n-max 2`), DFlash 2 (`--spec-type draft-dflash`; drafter GGUF ≤ 2 GB, name and
   size to the user first). Greedy output identical with/without drafter. Longest context (8K/16K/32K) that passes the
   fit rule in a 600 s soak; peak memory; 0 critical pressure, 0 GPU OOM. Check that the Qwen tool path still renders
   the same on 12359 (`/apply-template` ending, `<tool_call>` token).
3. A 27b recall gate (wrapper with ports 8423/8424 around the frozen recall cases, no edit to `test_recall.py`).

## How to run things

- Gates under launchd `ProcessType=Interactive`; plist and logs on the internal disk (`$CLAUDE_JOB_DIR/tmp`).
  Copy `run_list.py`, `launch.sh` from `code/.session/kildall27b-0-20261122/`. Plans used this round:
  `plan-pr19.json` / `plan-0b.json` pattern (setup + 27 controls + `test_qwen_tools` + backups + check + nuke + smoke).
  Write evidence into `code_27b/.session/` (not main's `code/.session`).
- `kildall ask` smoke must run under launchd too. Stop with `code_27b/.venv/bin/kildall --stop`.
- Read the DB by copying `code_27b/kildall27b.db*` to scratch (read-only open fails on exFAT).
- History scan before push: `code/.venv/bin/python code/.session/reroot-usb-20261102/secret_audit.py history-code <label>`.

## Rules to keep

- Main Kildall goes first; ask before long Mac runs. Downloads ≤ 2 GB each, 27B-only, named and sized first.
- Builder ≠ reviewer: a fresh agent reviews each PR before merge into `kildall-27b`.
- Stop before about 800k tokens of context and write the next handoff.
