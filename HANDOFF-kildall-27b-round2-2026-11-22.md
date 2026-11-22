# Handoff — Kildall-27b round 2 (2026-11-22, evening)

Read `CLAUDE.md` (top rules + last 2026-11-22 entries), `Kildall27b.md`, `code_27b/README-27b.md`.

## State

- **code_1.24 round 2 is done** (README has the eval table; `c778bbe` pushed). The older handoff said "pending"; it was not.
- **Slice 27b-0 built.** Worktree `/Volumes/ES2TB/Kildall/code_27b`. Branch `kildall-27b` = main `ff20e40` (pushed).
  Slice branch `kildall-27b-0-setup` = `f7cbc5d` (pushed). **Draft PR #19** into `kildall-27b`:
  https://github.com/MinhDuc2612/Kildall/pull/19
- Gates on `f7cbc5d`: 27/27 controls, `check.sh` 0, nuke dry-run 13,864 entries / 0 outside / 0 refused,
  code-history scan 1,923 objects / 0 findings. Evidence: `code/.session/kildall27b-0-20261122/gates-3/`.
- **Live smoke failed (known gap):** servers start on 8423/8424 in 47 s, then
  `kildall: Expected the pinned Gemma 4 native chat template` (`code_27b/tool_runtime.py:61`).
  `tool_runtime.py` and `tool_grammar.py` build only Gemma 4 native tool calls. Evidence: `.../smoke/`.
- New persistent items (part of the 27b plan): LaunchAgent `local.kildall27b.backup` (03:00 + login),
  launcher `~/Library/Application Support/Kildall27b/launcher.py`, logs `~/Library/Logs/Kildall27b`.
  Remove with `launchctl bootout gui/$(id -u)/local.kildall27b.backup` and delete
  `~/Library/LaunchAgents/local.kildall27b.backup.plist`.

## Next (in order)

1. **Independent review of PR #19** (fresh agent, not the builder). If no blocking finding: mark ready, merge into
   `kildall-27b` (normal merge, merge authority 2026-11-09). Never into `main`.
2. **Slice 27b-0b: Qwen3.8 tool calls** (new row in `Kildall27b.md`). Read the Swift GGUF chat template
   (`tokenizer.chat_template`) first. Two ways; pick by evidence:
   (a) server-side tool parsing via `/v1/chat/completions` with `tools` and `--jinja` on b10809, plus a schema grammar;
   (b) own GBNF for the Qwen `<tool_call>` format, same as the Gemma path does today.
   Keep `test_tool_grammar.py` (Gemma acceptance) passing. Gate: one live turn with a tool call works; controls pass.
3. Slice 27b-1 speed + memory (Homebrew 12359: plain, MTP, DFlash 2; fit rule 600 s soak).

## How to run things (learned this session)

- Gates run under launchd `ProcessType=Interactive`. **Put the plist and its log files on the internal disk**
  (`$CLAUDE_JOB_DIR/tmp`): launchd cannot open log files on the exFAT drive (exit 78) and refused a plist there
  (bootstrap error 5). Step outputs may go to the drive.
- Tools: `code/.session/kildall27b-0-20261122/` has `run_list.py`, `launch.sh` (copy both to `$CLAUDE_JOB_DIR/tmp`),
  and `plan-gates-3.json` (setup steps + 27 controls + backups + check + nuke). Use `code_27b/.venv/bin/python`.
- `code_27b/.session` and the `.tools` link (to `code/.tools`) are not in git; `plan-gates-3.json` re-creates them.
- History scan before push: `code/.venv/bin/python code/.session/reroot-usb-20261102/secret_audit.py history-code <label>`.

## Rules to keep

- Main Kildall goes first; ask before taking the Mac for long runs.
- Downloads: each 2 GB or less, belonging to the 27B; name and size to the user first.
- Stop before about 800k tokens of context and write the next handoff.
