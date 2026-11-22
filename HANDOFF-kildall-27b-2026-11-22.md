# Handoff — Kildall-27b (2026-11-22)

Read `CLAUDE.md` (top rules + last 2026-11-22 entries), then `Kildall27b.md`, then
`Researchhub/sample4/kildall27b-methods.md`.

## State

- Plan written and pushed: vault commit `0c6482f` on `kildall/workspace` (Orbiplan v60, Kildall27b.md v1,
  checklist Group 21 = 265 items). Vault history audit `vault-scan-20261122-kildall27b` passed.
- No Kildall-27b code yet. Branch `kildall-27b` and folder `code_27b` do not exist yet.
- Main code checkout: branch per `git -C code status`; main = `ff20e40` at last check; PR #18 still draft.
- code_1.24: eval run 1 = 1/20, run 2 = 1/20 (459 calls, 6,074 s). **Still pending: README-1.24 update and the
  commit/push of the code_1.24 round-2 port** (user said "commit and push when all gates pass"; gates passed).

## Next (in order)

1. Finish code_1.24: add round-2 eval results to `code_1.24/README-1.24.md`, commit only code_1.24 files +
   CLAUDE.md, vault audit, push `reroot-usb:workspace`.
2. Kildall-27b slice **27b-0 Setup** (see `Kildall27b.md` table). Side track: main Kildall goes first, so check with
   the user before taking the Mac for long runs.
3. Slice 27b-1 speed + memory (Homebrew llama.cpp 12359: plain, MTP, DFlash 2; fit rule 600 s soak).

## Rules to keep

- Gates run under a launchd job with `ProcessType=Interactive` (not the Claude shell: exFAT AppleDouble files;
  not `launchctl submit`: throttled timers).
- Downloads: each 2 GB or less, belonging to the 27B; tell the user the name and size first.
- Stop before about 800k tokens of context and write the next handoff.
