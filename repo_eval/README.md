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

Each task has five independent copies: buggy, restored real fix, fix-agent,
no-op, and test-edit cheat. Admission requires buggy FAIL, fixed PASS, fix-agent
PASS, no-op FAIL, and cheat flagged. Invalid candidates are excluded, with failed
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
