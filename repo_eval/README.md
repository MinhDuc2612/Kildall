# Personal repo eval candidates (#112)

Unfrozen review pool: **32 validated Kildall bug tasks** (12 easy, 11 medium,
9 hard), plus **one separate explanation/empty-diff trap**. No model inference,
baseline, or task freeze has run. The user accepted the 8 easy / 8 medium /
4 hard proposal; it remains unfrozen and subject to Claude review.

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
also have a 60-second bound. Candidate code runs in a sandboxed worker. Trusted
assertions run in a separate sandboxed process and access product objects through
a JSON bridge; they never import candidate Python. Only the verifier receives
the private result channel. The controller persists its report outside the copy
and returns scoring booleans and failed regression-test names. Worker exit codes,
stdout and files cannot supply a passing result. Raw output stays in controller
evidence. macOS setuid `ps` is unavailable under Seatbelt,
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

The latest per-task matrix, including check counts, is below.

### Accepted 20 — not frozen

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

## Verifier isolation review (2026-11-07)

The three review findings are addressed for Claude's review. PR #15 remains
unchanged and awaits the user's merge word. Product files still match main
`f98b4a2`; this change is confined to evaluation code, fixtures and reports.

### Independent scoring

Both processes use `python -I -S -B`, an explicit environment and Seatbelt
profiles that deny network and writes outside candidate home. The worker cannot
read verifier suites or configuration. The verifier cannot follow a fixture
symlink into a writable controller file. The JSON bridge exposes only supplied
fixture capabilities: private attributes, mock bookkeeping and fixture mutation
are refused. Callback assertion failures remain failures even when candidate
code catches them. No candidate pickle or Python source is evaluated in the
assertion process.

Only the verifier writes the private report pipe; the worker never inherits
that descriptor. The controller stores the report in `verify-*/trusted/`, outside
both source copies, and requires completion, every collected check executed,
no skips, positive collection and no assertion failure. Exit zero alone is
insufficient. Inputs record hashes of the harness, both runtime files, task
assets and source copy.

`test_repo_eval.py` passes nine adversarial routes: runpy preload, fake exit and
stdout markers, copy-side verifier replacement, copy-side result JSON,
sitecustomize/usercustomize/pth, conftest/pytest configuration, stdlib shadow
files, environment poisoning, and attempted controller-result writes. Startup
and environment attacks also preserve valid repairs. Separate controls reject
zero checks, skips, uncalled assertion/exception/mock checks, and premature
exit zero. Fixture controls reject private/mock access, host writes through a
symlink, swallowed assertions and forged non-exception decoder types.

### Executed suites and removed suites

Every trial executes its explicit `.repo_eval_verify.py` and the base version
of `test_tool_validation.py`. Collection counts assertion sites, expected-
exception checks and mock assertions; these script suites have no pytest
discovery step. A passing repair must execute every collected site. Candidate
admission also refuses any skipped or zero-check suite in its control matrix.
There are 140 probe sites across the 33 tasks and 37 regression sites per trial.

The following 11 distinct suites were removed from `hidden_test_files` and
recorded in `removed_hidden_suites` with a reason:

`test_phase41.py`, `test_shell_lifecycle.py`, `test_phase44.py`, `test_cloud.py`,
`test_permissions.py`, `test_router_warmth.py`, `test_cli.py`, `test_nuke.py`,
`test_phase43.py`, `test_phase42.py`, `test_platform_keys.py`.

Their host integration fixtures are not supported by this restricted object
bridge. They no longer count as isolated checks. All eleven really ran among
the **28/28 passing standing controls** at the actual product root, without a
HOME/root override. Those host results do not claim per-candidate coverage.
Manifests retain the exact removal list for each task.

### Base hints

Only the accepted 20 task copies omit all remaining base `test_*` files and
Markdown documents (the base has README, BASELINE and BENCHMARKS). Hidden suites
and BENCHMARKS were already withheld. Each copy records its additional removals
in `redactions.json`; product files and behavior are preserved. The other 13
tasks retain their earlier visibility. The explanation exercise stays unscored.

### Final controls and retained failures

Evidence: `.session/repo-eval-isolation-20261107T071400/`.
Validation02 passes all **33 candidate matrices / 237 trials / 474 suite
invocations**: real fixes and fix-agents pass, no-ops fail, cheats are flagged,
**67/67 lazy mutants fail their probe and 5/5 alternatives pass**. All 67 lazy
and five alternative definitions are byte-identical to `dd356af`. The cheat
agent edits protected configuration because selected copies no longer expose
base tests; direct test-edit attempts remain covered by harness controls.
Harness07 and all 28 standing controls pass. `check.sh` exits 0. The live nuke
dry-run reports 389,883 entries, zero outside and zero rejected. Two reporting
parser errors are retained; the result was recovered from the existing raw log
without repeating the dry-run. There was no inference, baseline or freeze.

All failures remain in the evidence directory: startup dependency/exception
transport failures, constructor proxy and fixture audit failures in golden01,
the mock-guard syntax failure, fake-exit cleanup failure, trusted-runtime access
failure, and validation01's nuke fixture symlink audit failure (32/33 accepted).
The corrected audit uses no-follow descriptors for protected paths, without
rejecting intentional fixture links. Earlier review and slot-cancellation
failures are retained too. These finite tests do not prove resistance to every
possible shortcut; stop at the draft PR for Claude review.

The table below reports the latest run. Every row has passing real-fix and
fix-agent controls, a failing no-op and a flagged cheat. Probe counts are from
the real repair; its regression suite also executes **37/37** sites.

| Task | Difficulty | Accepted 20 | Probe checks executed | Lazy rejected | Alternatives |
|---|---|---|---|---|---|
| [action-background-outcome](tasks/action-background-outcome/lazy.json) | medium | yes | 3/3 | 2/2 | — |
| [child-background-outcome](tasks/child-background-outcome/lazy.json) | hard | yes | 5/5 | 2/2 | — |
| [cloud-anonymous-key](tasks/cloud-anonymous-key/lazy.json) | easy | no | 4/4 | 1/1 | — |
| [cloud-duplicate-fields](tasks/cloud-duplicate-fields/lazy.json) | medium | no | 3/3 | 1/1 | — |
| [cloud-null-calls](tasks/cloud-null-calls/lazy.json) | easy | yes | 4/4 | 2/2 | — |
| [disabled-interval-clock](tasks/disabled-interval-clock/lazy.json) | easy | yes | 7/7 | 3/3 | — |
| [explain-never-policy](tasks/explain-never-policy/lazy.json) | medium | no | 5/5 | 1/1 | — |
| [foreground-warm-lock](tasks/foreground-warm-lock/lazy.json) | medium | yes | 4/4 | 3/3 | — |
| [internal-transcript-capability](tasks/internal-transcript-capability/lazy.json) | hard | no | 4/4 | 1/1 | — |
| [local-common-directory](tasks/local-common-directory/lazy.json) | medium | yes | 4/4 | 3/3 | — |
| [metadata-case-alias](tasks/metadata-case-alias/lazy.json) | medium | yes | 5/5 | 3/3 | — |
| [missing-message-write](tasks/missing-message-write/lazy.json) | easy | no | 3/3 | 1/1 | — |
| [missing-session-admission](tasks/missing-session-admission/lazy.json) | medium | yes | 4/4 | 2/2 | 1/1 |
| [missing-task-outcome](tasks/missing-task-outcome/lazy.json) | easy | yes | 4/4 | 3/3 | — |
| [missing-task-state](tasks/missing-task-state/lazy.json) | easy | no | 3/3 | 1/1 | — |
| [nuke-sidecar-before-open](tasks/nuke-sidecar-before-open/lazy.json) | hard | no | 5/5 | 1/1 | — |
| [oversized-hook-audit](tasks/oversized-hook-audit/lazy.json) | medium | yes | 5/5 | 2/2 | — |
| [partial-router-warm](tasks/partial-router-warm/lazy.json) | easy | yes | 5/5 | 3/3 | 1/1 |
| [pdf-byte-boundary](tasks/pdf-byte-boundary/lazy.json) | medium | yes | 3/3 | 2/2 | — |
| [post-hook-status](tasks/post-hook-status/lazy.json) | hard | yes | 5/5 | 3/3 | — |
| [remote-hook-execution](tasks/remote-hook-execution/lazy.json) | hard | no | 2/2 | 1/1 | — |
| [remote-macos-config](tasks/remote-macos-config/lazy.json) | easy | yes | 3/3 | 2/2 | — |
| [remote-metadata-redirect](tasks/remote-metadata-redirect/lazy.json) | medium | no | 2/2 | 1/1 | — |
| [remote-symbolic-ref](tasks/remote-symbolic-ref/lazy.json) | hard | no | 2/2 | 1/1 | — |
| [router-save-link](tasks/router-save-link/lazy.json) | hard | no | 8/8 | 1/1 | — |
| [scanner-word-boundary](tasks/scanner-word-boundary/lazy.json) | easy | yes | 5/5 | 4/4 | — |
| [server-port-ownership](tasks/server-port-ownership/lazy.json) | easy | yes | 4/4 | 2/2 | — |
| [shell-binary-output](tasks/shell-binary-output/lazy.json) | medium | yes | 5/5 | 3/3 | — |
| [shell-poll-completion](tasks/shell-poll-completion/lazy.json) | hard | yes | 4/4 | 4/4 | — |
| [submodule-worktree-diff](tasks/submodule-worktree-diff/lazy.json) | medium | no | 3/3 | 1/1 | — |
| [switch-hidden-index](tasks/switch-hidden-index/lazy.json) | hard | yes | 5/5 | 3/3 | 1/1 |
| [terminal-nonseekable](tasks/terminal-nonseekable/lazy.json) | easy | yes | 5/5 | 3/3 | 2/2 |
| [unsupported-keys-diagnostic](tasks/unsupported-keys-diagnostic/lazy.json) | easy | no | 7/7 | 1/1 | — |
