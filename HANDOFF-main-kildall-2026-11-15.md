# Handoff — continue main Kildall (written 2026-11-15 02:35 +07)

Read `CLAUDE.md` first (the last ~25 entries from 2026-11-13 onward are enough to resume; the whole file is 5,300+
lines). Then read `HANDOFF-main-kildall.md` for the hard rules, the 800k session budget and the user's style. Its
"First job" section is DONE. This file is the current state. Claude is the only builder, reviewer and merger.

## What changed this session (2026-11-14 → 15)
- **PR #17 (#48 in-turn compaction) MERGED.** Every gate passed at `5530167`. Frozen #112 eval: **0/20 and 0/20**,
  but ContextOverflow stops went 19/17 → **0/0**; 15/14 tasks now end at the 40-call cap.
- **PR #13 (#112 eval harness + baseline) MERGED.** Open: draft PR #18 only.
- **main = `ff20e40`** (code repo `/Volumes/ES2TB/Kildall/code`, checkout on `main`, clean; local branch `tool-output-diet` = PR #18).
- Vault `/Volumes/ES2TB/Kildall` branch `reroot-usb` → remote `kildall` branch `workspace` (see CLAUDE.md for the SHA).

## The evidence that picks the next slice
Transcript audit of both eval runs (1,424 tool calls): **736 exact repeat calls (52%)**; 586 grep, 638 read, 98
edits of which 82 returned an error; 17 of 40 task runs made no edit. The model re-issues searches whose results
were compacted away, and its edits fail. Report: `code/BENCHMARKS.md` (last section), evidence
`code/.session/compaction-fix-20261114e/` (transcripts in `frozen/.session/run-1|2/<task>/transcript.jsonl`).

## Next jobs, in order (one slice per PR, full gates each, then the frozen eval twice)
0. **FIRST: finish draft PR #18 `tool-output-diet` (`209f929`).** Already built and pushed: plain `path:line:text`
   grep rows (4–5× smaller), step summaries that keep read line ranges and grep match places, a note on exact
   repeat calls, edit errors with the match count. Focused test PASS 7/7. **Gates NOT run.** Do: quiet Mac
   (check `pgrep -lf "hf download"` — a foreign model download was loading the USB drive on 2026-11-15 and made
   `test_phase41`/`test_phase44` miss their timing; do not stop it, wait for it), restart, then full gates + frozen
   eval ×2 with the launchd recipe below (new evidence folder, new `source.json` for `209f929`). Keep only if it
   beats 0/20 or clearly cuts the 52% repeat calls; record either way. It covers most of #108 and part of #107.
   **The eval driver only exercises `fit_messages`, `system_prompt`, `BASE_TOOLS`, `tool_runtime.chat` and the
   product tools — changes inside `_run_turn` are not measured.**
   After it: one predefined split-16K soak from a clean-swap start (the 2026-10-14 fail began at 10.3 GB swap);
   a 4,096 window holds only 1–2 file reads, 16K would hold ~8. Gate limit unchanged (≤ 103 warnings, 0 critical).
1. **#108 repeat-call breaker** (biggest lever: 52% repeats). An exact repeat of an earlier call in the same turn
   should return a short "you already ran this; result was …" message instead of running again. Consider with it:
   keep findings (file:line hits) in the compaction step summaries, so the model does not need to search again.
2. **#107 error messages** for failed `edit` calls (82/98 failed): read 5–10 failed edit results in the transcripts
   first, then make the error say what to do (not unique → show the candidates; not found → show nearest text).
3. **#98 loop breaker**, then the rest of 5d in `Orbiplan.md` → "Queued small slices" (#89, #88, #91, #97, #102,
   #104, #105, #90), then test #3, 5e, 4.5b–e, quality slice, Gemma vision, 4C.
4. **Small open slice: AppleDouble tolerance** on the exFAT root. WIP: `code/.session/appledouble-20261114/
   skip-appledouble.patch` (also `git stash` on local branch `skip-appledouble`): glob skips `._*` files;
   `git_switch` clean check ignores untracked `._*`. Still needed: `test_phase42.py` asserts raw `git status` is
   empty, so its fixture needs the same tolerance; then gates.
5. **Harness debt (PR #13 reviews):** lazy fixes can pass, some correct fixes are rejected, `communicate()` has no
   timeout, `process-info*` in the sandbox profile. Fix before trusting any score above 0.
Keep-on-evidence rule: a 5d slice stays only if it beats the baseline on the frozen eval (now 0/20, 0 overflow).

## How to run gates now (learned the hard way this session — do exactly this)
- **Never start gate or test chains from the Claude job shell.** Its processes put `com.apple.provenance` on new
  files; exFAT stores that as `._name` AppleDouble files; `test_phase41`/`test_phase42` then fail.
- **Never use `launchctl submit`.** Background-type launchd jobs get throttled timers; `test_memory.py` fails at
  ~388 ms against its 300 ms cap (5/5).
- **Do:** a launchd plist with `ProcessType=Interactive`, `RunAtLoad`, program = the venv Python
  (`/Volumes/ES2TB/Kildall/code/.venv/bin/python -B <script on the internal disk>`), stdout/stderr paths on the
  internal disk; `launchctl bootstrap gui/$(id -u) <plist>`; wait for a DONE marker; then `launchctl bootout`.
  bash as the launchd program cannot write to the USB volume. Working copies:
  `code/.session/compaction-fix-20261114e/local.kildall.gates.plist`, `run_e.py` (builds a clean evidence folder,
  then execs `chain.sh`), `chain.sh` (routing → recall → abstention → quality → cli → post_live → eval_control →
  eval 1 → eval 2; stops at first failure).
- Let the launchd script build the evidence folder itself (copy the 12 collectors by hash from
  `compaction-fix-20261113`, write a new `source.json` = sha256 of the 76+ tracked files at the tested commit,
  `before.json`, `frozen/` copy). Folders copied from the Claude shell get thousands of `._` files.
- For a new product commit: regenerate `source.json` (`git ls-files` + sha256) and update `source_commit` in
  `measurement-protocol.json`; the frozen harness copy now comes from main (`repo_eval*` is in main).
- **Admission:** swap ≤ 3 GB, pressure 1, ports 8123/8124 free, no other model, wired 20480. The first model load
  adds ~2 GB of swap when Chrome is open, so a run started above ~1 GB swap dies at the restart check. Ask the user
  to **restart the Mac and keep Chrome and Wuthering Waves closed** before a gate run. Gates ≈ 20 min; the two
  evals ≈ 7.5 h (3 h 26 min + 3 h 55 min this time).
- Timing misses seen once and passed on rerun: `test_phase44.py` SIGINT test (1 of 15). `test_repo_eval.py` runs
  ~20 min with no output — do not kill it.
- A PreToolUse hook ("Fact-Forcing Gate") blocks the first Bash call after each user message and commands it sees
  as destructive (`rm`, `git checkout --`, `branch -D`): state the request and what the command does, then retry;
  prefer `git stash` and leave scratch folders in the ignored `.session/`.

## Hard rules (unchanged — see `HANDOFF-main-kildall.md` and CLAUDE.md top)
USB root only · PRs only, ordinary fast-forward of main, no force · full-history secret scan before every push
(`code/.session/compaction-fix-20261114e/code_secret_audit.py history-code <label>`; vault:
`code/.session/verifier-compaction-20261111-swr_9zup/vault_audit.py <ref> <label>`) · never a paid API · no sudo ·
never stop another session's processes · hooks stay on · log every action in CLAUDE.md at once · never merge on a
failed or unscored gate · one attempt per stage, failures retained · planning files (`Orbiplan.md`,
`Orbimodels.md`, `Orbichecklist.md`) and `Researchhub/` are read-only without the user's word.

## Rolling handoff
Work until ~800k tokens, then write the next `HANDOFF-main-kildall-<date>.md` in this shape, commit and push the
vault, and send the file to the user with SendUserFile.
