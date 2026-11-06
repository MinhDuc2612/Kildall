# Personal repo eval candidates (#112)

Unfrozen review pool: **32 validated Kildall bug tasks** (12 easy, 11 medium,
9 hard), plus **one separate explanation/empty-diff trap**. No model inference,
baseline, or final task selection has run. Claude reviews this list before a
final 8 easy / 8 medium / 4 hard selection or any baseline runs.

`candidates.json` contains each source fix, difficulty estimate, trap, task link,
validity result and deterministic agent results. Task issues describe symptoms;
solution patches and verifier files remain outside the evaluated agent's copy.
All task content comes from Kildall. No private-repository content is included.

## Provenance and validity

Every bug task pins `a90d5619345e0eef64ace17b95a90f48b46b7ccf` and applies one
reverse patch. `git_parent` identifies a correction visible against its Git
parent. `documented_precommit` identifies a real correction documented before
its slice's first public commit; its prior buggy behavior is reconstructed from
that record, not claimed to exist in a public parent. The fixed hunk is checked
against the cited public source. The foreground-lock task retains the later
platform wrapper around the same nonblocking lock operation; its adaptation is
recorded in the candidate index.

Each task has independent copies for buggy, restored real fix, fix-agent,
no-op, test-edit cheat, and every declared lazy or valid-alternative variant.
Admission requires buggy FAIL, fixed PASS, fix-agent PASS, no-op FAIL, cheat
flagged, every lazy mutant rejected by the probe, and valid alternatives passing. Invalid candidates are excluded, with failed
results retained. Validation02 accepted all 32 bug tasks and the extra trap.

The no-code task is an explicit exception to reverse-patch validity: it has no
bug patch and requires an explanation plus an empty diff. A silent no-op fails.
Its deterministic explanation checklist is a proposal for Claude's review,
not a claim of general semantic grading. It is excluded from the 30-task minimum.
The other trap types are cross-file cause (`pdf-byte-boundary`) and a correct
visible test that looks wrong (`scanner-word-boundary`, where an ordinary task
identifier resembles a credential prefix).

## Harness boundary and next-slice plan

Run deterministic checks from `code/`:

```sh
.venv/bin/python test_repo_eval.py
.venv/bin/python repo_eval.py validate --output .session/repo-eval-YYYYMMDD/validation
```

Output directories must be new; existing evidence is never overwritten. There
is no model-running command in this slice. The future driver must use Lane A,
disable cloud in its isolated runtime configuration, set the project root to
the fresh task copy, and route every action through `Trial.action`. A fresh
source archive omits Git history, benchmark answers and every executed test.
The production configuration is preserved in the archive; `run-plan.json`
records the required isolated runtime settings for the future driver.

The harness approves Confirm only for in-copy typed writes/edits and the exact
manifest verification command. Other commands and operations are declined;
production permissions are unchanged. Never remains Never. Every decision is
logged. Each trial has a 40-call / 900-second cap; verification subprocesses
also have a 60-second bound. The verifier uses a separate copy, injects hidden
tests only there, denies network and access to control/source/credential data,
and returns only scoring booleans and failed regression-test names. Raw output
stays in controller evidence. macOS setuid `ps` is unavailable under Seatbelt,
so the isolated verifier uses a fixed process-start fixture. Host control suites
run separately without that fixture.

Metrics include validity, correctness, executable status, wrong-but-valid,
pass, calls to green, wall time, non-test diff lines, cheat reasons and other
tests broken. Protected-file edits, hidden-path write attempts, removed/changed
assertions, added skip syntax, and verifier-side test edits are flagged. This
is deterministic file/syntax detection, not proof against every semantic way
of evading a test. `other_tests_broken` covers the task's declared regression
suite (`test_tool_validation.py`); it does not claim the entire repository suite
ran in every copy. The full standing suites are a separate delivery gate.

## Recorded gates

Evidence: `.session/repo-eval-20261025/`.

| Gate | Result |
|---|---|
| Bug validity | 32/32 buggy FAIL / real fix PASS |
| Fix-agent / no-op / cheat | 33/33 pass / fail / flagged, including extra trap |
| Harness boundaries | PASS; includes actual filesystem/network refusals and caps |
| Existing controls | **FAIL: 26/27**; slot-isolation cancellation produces an empty HTTP response and `JSONDecodeError` |
| Hooks / Phase3 empty-system Never | 5/5 / PASS |
| Existing source, configuration, frozen fixtures, planning files | Byte-identical to starting snapshot |
| Live nuke dry-run | 92,584 entries; 0 outside; 0 rejected |
| `check.sh` / wired | Exit 0 / 20480 |
| Secrets | PASS: private exact-value scan 0 hits; staged-tree/Keychain scanner 0 findings |

The slot-isolation failure is retained without a production fix or rerun.
Validation01's rejected switch task remains recorded: a raw-text cheat detector
incorrectly matched `skip-worktree` in a diagnostic. The AST detector fixed that
harness error. Initial sandbox, probe-generation and harness-control failures
are also retained. This PR stays draft for candidate review; no merge or baseline.

## Full-pool hardening (2026-11-06)

The branch now includes main `f98b4a2` through ordinary merge `ed045ec`.
Product files match main. Historical task bases stay pinned to `a90d561`.
All 33 probes check successful behavior as well as the reported defect; all
33 tasks require lazy self-tests. A lazy mutant must be valid, executable,
unflagged as cheating, and rejected by the task probe itself. Missing mutants
or a surviving mutant exclude the candidate. Five valid alternative repairs
also have to pass, covering exception types, terminal arguments and Git flag order.

Validation02: **32/32 bugs fail before repair and pass after repair; 33/33
fix-agent / no-op / cheat controls pass; 67/67 lazy mutants are rejected;
5/5 valid alternatives pass.** This includes the explanation exercise as an
unscored control. `test_repo_eval.py` passes, including real archive refusal
before extraction. The unchanged product passes all **28 standing controls**,
including hooks and empty-system Never, at its real USB root. `check.sh` exits 0.
No model inference, baseline or task freeze ran.

Evidence: `.session/repo-eval-review-20261106T193139/`. Validation01 and
`review-before/` are retained: the first set of 33 mutants all failed, but
**34 additional Claude mutants still passed and five valid alternatives
were rejected**. Validation02 adds all 39 review cases to the permanent
self-tests. Older failures and the slot cancellation reproduction remain
available; no failed evidence was deleted. The cancellation product fix is
separate, in draft PR #15.

The explanation trap is `scored: false`, `graded_by: claude`, and excluded
from the proposal and any automatic score. Its keyword checklist remains
only a smoke test. Each row below has successful real-fix/fix-agent checks,
a failing no-op, and a flagged test-edit cheat.

| Task | Difficulty | Proposed 20 | Lazy mutants rejected | Valid alternatives |
|---|---|---|---|---|
| [action-background-outcome](tasks/action-background-outcome/lazy.json) | medium | yes | 2/2 | — |
| [child-background-outcome](tasks/child-background-outcome/lazy.json) | hard | yes | 2/2 | — |
| [cloud-anonymous-key](tasks/cloud-anonymous-key/lazy.json) | easy | no | 1/1 | — |
| [cloud-duplicate-fields](tasks/cloud-duplicate-fields/lazy.json) | medium | no | 1/1 | — |
| [cloud-null-calls](tasks/cloud-null-calls/lazy.json) | easy | yes | 2/2 | — |
| [disabled-interval-clock](tasks/disabled-interval-clock/lazy.json) | easy | yes | 3/3 | — |
| [explain-never-policy](tasks/explain-never-policy/lazy.json) | medium | no | 1/1 | — |
| [foreground-warm-lock](tasks/foreground-warm-lock/lazy.json) | medium | yes | 3/3 | — |
| [internal-transcript-capability](tasks/internal-transcript-capability/lazy.json) | hard | no | 1/1 | — |
| [local-common-directory](tasks/local-common-directory/lazy.json) | medium | yes | 3/3 | — |
| [metadata-case-alias](tasks/metadata-case-alias/lazy.json) | medium | yes | 3/3 | — |
| [missing-message-write](tasks/missing-message-write/lazy.json) | easy | no | 1/1 | — |
| [missing-session-admission](tasks/missing-session-admission/lazy.json) | medium | yes | 2/2 | 1/1 |
| [missing-task-outcome](tasks/missing-task-outcome/lazy.json) | easy | yes | 3/3 | — |
| [missing-task-state](tasks/missing-task-state/lazy.json) | easy | no | 1/1 | — |
| [nuke-sidecar-before-open](tasks/nuke-sidecar-before-open/lazy.json) | hard | no | 1/1 | — |
| [oversized-hook-audit](tasks/oversized-hook-audit/lazy.json) | medium | yes | 2/2 | — |
| [partial-router-warm](tasks/partial-router-warm/lazy.json) | easy | yes | 3/3 | 1/1 |
| [pdf-byte-boundary](tasks/pdf-byte-boundary/lazy.json) | medium | yes | 2/2 | — |
| [post-hook-status](tasks/post-hook-status/lazy.json) | hard | yes | 3/3 | — |
| [remote-hook-execution](tasks/remote-hook-execution/lazy.json) | hard | no | 1/1 | — |
| [remote-macos-config](tasks/remote-macos-config/lazy.json) | easy | yes | 2/2 | — |
| [remote-metadata-redirect](tasks/remote-metadata-redirect/lazy.json) | medium | no | 1/1 | — |
| [remote-symbolic-ref](tasks/remote-symbolic-ref/lazy.json) | hard | no | 1/1 | — |
| [router-save-link](tasks/router-save-link/lazy.json) | hard | no | 1/1 | — |
| [scanner-word-boundary](tasks/scanner-word-boundary/lazy.json) | easy | yes | 4/4 | — |
| [server-port-ownership](tasks/server-port-ownership/lazy.json) | easy | yes | 2/2 | — |
| [shell-binary-output](tasks/shell-binary-output/lazy.json) | medium | yes | 3/3 | — |
| [shell-poll-completion](tasks/shell-poll-completion/lazy.json) | hard | yes | 4/4 | — |
| [submodule-worktree-diff](tasks/submodule-worktree-diff/lazy.json) | medium | no | 1/1 | — |
| [switch-hidden-index](tasks/switch-hidden-index/lazy.json) | hard | yes | 3/3 | 1/1 |
| [terminal-nonseekable](tasks/terminal-nonseekable/lazy.json) | easy | yes | 3/3 | 2/2 |
| [unsupported-keys-diagnostic](tasks/unsupported-keys-diagnostic/lazy.json) | easy | no | 1/1 | — |

### Proposed 20 — not frozen

- Easy (8): cloud-null-calls, disabled-interval-clock, missing-task-outcome,
  partial-router-warm, remote-macos-config, scanner-word-boundary,
  server-port-ownership, terminal-nonseekable.
- Medium (8): action-background-outcome, foreground-warm-lock,
  local-common-directory, metadata-case-alias, missing-session-admission,
  oversized-hook-audit, pdf-byte-boundary, shell-binary-output.
- Hard (4): child-background-outcome, post-hook-status,
  shell-poll-completion, switch-hidden-index.

That is one rowcount task, one `git_tools.origin` task, and two `cloud.py`
tasks. Difficulty labels are estimates pending Claude review, not model results.

### Remaining review limits

These finite mutants do not establish resistance to every shortcut. Claude's
latest review also found verifier-preload/exit spoofing, unexecuted hidden
module suites, and answer hints in other base tests/docs. Those findings remain
open: the executed isolated regression suite is `test_tool_validation.py`,
while the full product controls run separately. This round does not claim an
adversarially secure scoring harness or authorize a baseline or freeze.
