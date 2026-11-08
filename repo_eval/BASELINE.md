# Frozen repo-eval baselines

## Two full runs — 2026-11-08

PR #13 was verified at `540278066ef6d6823cdae0b282c74aba9a2ba858` before starting.
Freeze `3d9b4a6c1b40cbe908cf561f77189568ed7e8662` remains unchanged: all 20 IDs,
84 task assets and five harness/selection hashes match [the frozen manifest](frozen-20.json).
Product source still matches main `f98b4a2`.

**Both runs completed all 20 tasks: 0 passed, 20 failed, 23 tool calls each.**
All 40 attempts stopped with `ContextOverflow` after tool output at the unchanged
4,096-token product context limit. No source edits were made in any task copy.
The trusted verifier rejected every final copy. These are retained failed task
scores; no retries or context, prompt, tool-output, model or limit changes followed.
The observed score difference is zero. Both runs measure behavior at the default
context limit.

### Admission

| Run | Immediately before startup (+07:00) | Pressure | Swap bytes | Ports 8123/8124/8223/8224 | Other models |
|---|---|---|---:|---|---|
| 1 | 2026-11-08T18:30:09+07:00 | normal (1) | 0 | all free | none |
| 2 | 2026-11-08T18:34:54+07:00 | normal (1) | 0 | all free | none |

Both satisfy the unchanged 3,000,000,000-byte swap limit. Only this collector's
owned Lane A and embedding services were stopped between/after runs.

### Model and method

Lane A: **Gemma 4 26B-A4B UD-IQ3_S**, the installed
`gemma-4-26B-A4B-it-UD-IQ3_S.gguf`, with the product b10809 launcher and Harrier
embedding helper. Product defaults are 4,096 context tokens per slot, three slots,
`temperature=0`, `top_p=1`, `samplers=[temperature]`, `seed=42`, `max_tokens=512`,
streaming, prompt caching, automatic tool choice and no parallel tool calls.
The default system prompt, `BASE_TOOLS`, `fit_messages` and `tool_runtime.chat`
were used with fresh empty memory/history for every task and the normal work-slot
lease. Sampling arguments were checked against the product implementation.

The reviewed harness has no model-running entry point. An external collector in
ignored evidence drove its unchanged `Trial.action` boundary. It supplied each
frozen issue and the same generic tool/verification contract, with no solution
hints. The harness's 40-call / 900-second caps and 60-second verifier bound stayed
unchanged. Its required isolated runtime paths and disabled cloud were set only
in memory. No product configuration file changed. A fresh default runtime was
started for each run, without custom warmup or OS cache clearing. Driver SHA-256:
`b40afe7c6e1121e42d0dc2d5967928f25eb54e2f9c44351349ca68d4e33be54b`.

Each model tool request counts, including refused requests; controller grading
is not a model tool call. Task wall time runs from `Trial.started` through final
grading. Run wall time includes startup and task setup, and excludes final
service shutdown. Totals are calculated before rounding to milliseconds.

### Per-task results

| Task | Run 1 | Calls | Wall s | Run 2 | Calls | Wall s |
|---|---|---:|---:|---|---:|---:|
| action-background-outcome | FAIL | 1 | 8.143 | FAIL | 1 | 7.598 |
| child-background-outcome | FAIL | 1 | 7.639 | FAIL | 1 | 7.674 |
| cloud-null-calls | FAIL | 2 | 14.651 | FAIL | 2 | 15.034 |
| disabled-interval-clock | FAIL | 1 | 7.594 | FAIL | 1 | 7.856 |
| foreground-warm-lock | FAIL | 1 | 7.497 | FAIL | 1 | 7.806 |
| local-common-directory | FAIL | 1 | 7.445 | FAIL | 1 | 7.785 |
| metadata-case-alias | FAIL | 1 | 7.570 | FAIL | 1 | 7.816 |
| missing-session-admission | FAIL | 1 | 7.593 | FAIL | 1 | 7.984 |
| missing-task-outcome | FAIL | 1 | 7.609 | FAIL | 1 | 7.846 |
| oversized-hook-audit | FAIL | 1 | 7.639 | FAIL | 1 | 7.921 |
| partial-router-warm | FAIL | 1 | 7.678 | FAIL | 1 | 7.918 |
| pdf-byte-boundary | FAIL | 1 | 7.696 | FAIL | 1 | 7.954 |
| post-hook-status | FAIL | 1 | 7.785 | FAIL | 1 | 7.932 |
| remote-macos-config | FAIL | 1 | 7.779 | FAIL | 1 | 7.910 |
| scanner-word-boundary | FAIL | 1 | 7.787 | FAIL | 1 | 7.861 |
| server-port-ownership | FAIL | 1 | 7.853 | FAIL | 1 | 7.891 |
| shell-binary-output | FAIL | 1 | 7.771 | FAIL | 1 | 7.905 |
| shell-poll-completion | FAIL | 1 | 8.079 | FAIL | 1 | 7.871 |
| switch-hidden-index | FAIL | 1 | 7.843 | FAIL | 1 | 7.942 |
| terminal-nonseekable | FAIL | 3 | 12.079 | FAIL | 3 | 12.198 |

| Total | Run 1 | Run 2 | Difference (2 − 1) |
|---|---:|---:|---:|
| Tasks attempted | 20/20 | 20/20 | 0 |
| Passed / failed | 0 / 20 | 0 / 20 | 0 / 0 |
| Tool calls | 23 | 23 | 0 |
| Task wall s | 165.729 | 168.702 | +2.972 |
| Startup s | 70.545 | 22.264 | -48.281 |
| Run wall s | 238.564 | 193.025 | -45.539 |

Every task's defect probe was started and collected checks; no suite was skipped
or collected zero. Each `test_tool_validation.py` regression suite completed all
37 checks successfully (40/40 suite runs). In each run, `cloud-null-calls`,
`pdf-byte-boundary` and `remote-macos-config` raised their buggy-source exception
before the first assertion; the trusted verifier recorded those as failures.
Across all 40 grades, failures were 32 `AssertionError`, two `ValueError`, two
`KeyError`, two `PermissionError` and two `UnsupportedOperation`
(`terminal-nonseekable`). None was credited as a pass.

### Retained evidence and limitations

Local evidence: `.session/repo-eval-baseline-20261108-lexz0qi5/`, including both
admissions, `baseline.py`, both protocol files, every model response/transcript,
agent error, verifier result, copied source, service ownership/shutdown record,
and aggregate `baseline-result.json`. Evidence remains ignored and is not pushed.
All frozen hashes and the collector hash were checked after both runs. No
product or task changes, model retries, merge, HF sync, sudo or paid API occurred.

A post-run report audit initially asserted that every failing probe must execute
an assertion. The three pre-assert exceptions above disproved that assumption;
`report-check-01-failure.json` retains the failure. A second report-only check
incorrectly expected all other probes to fail assertions;
`report-check-02-failure.json` retains the two `UnsupportedOperation` cases that
disproved it. The corrected read-only audit checks that suites started, collected
tests and cannot pass on missing checks.
No inference or verifier run was repeated. Earlier failed admissions and controls
remain below and in the historical evidence. Draft PR #13 awaits Claude review.

## Previous admission failure — 2026-11-07

Freeze commit: `3d9b4a6c1b40cbe908cf561f77189568ed7e8662`. [Frozen task/assets/harness manifest](frozen-20.json).
Product source: `f98b4a2`; configured Lane A model: Gemma 4 26B-A4B UD-IQ3_S. Task assets and the reviewed harness are unchanged.

**STOPPED before inference.** Run 1 admission at 2026-11-07T23:17:23+07:00 found pressure **warning (2)** and swap **12.515017 GB** (12515016704 bytes), exceeding the unchanged **3.000 GB** limit. Ports 8123, 8124, 8223 and 8224 were free; the process check detected no model runtime.

Run 2 was not admitted or started after the failed first admission. No retries, changed limits, model launches or process stops occurred. The noise floor remains **unmeasured**.

`—` means no task timer ran. These are not failed task scores.

| Task | Run 1 | Calls | Wall s | Run 2 | Calls | Wall s |
|---|---|---:|---:|---|---:|---:|
| action-background-outcome | NOT RUN | 0 | — | NOT RUN | 0 | — |
| child-background-outcome | NOT RUN | 0 | — | NOT RUN | 0 | — |
| cloud-null-calls | NOT RUN | 0 | — | NOT RUN | 0 | — |
| disabled-interval-clock | NOT RUN | 0 | — | NOT RUN | 0 | — |
| foreground-warm-lock | NOT RUN | 0 | — | NOT RUN | 0 | — |
| local-common-directory | NOT RUN | 0 | — | NOT RUN | 0 | — |
| metadata-case-alias | NOT RUN | 0 | — | NOT RUN | 0 | — |
| missing-session-admission | NOT RUN | 0 | — | NOT RUN | 0 | — |
| missing-task-outcome | NOT RUN | 0 | — | NOT RUN | 0 | — |
| oversized-hook-audit | NOT RUN | 0 | — | NOT RUN | 0 | — |
| partial-router-warm | NOT RUN | 0 | — | NOT RUN | 0 | — |
| pdf-byte-boundary | NOT RUN | 0 | — | NOT RUN | 0 | — |
| post-hook-status | NOT RUN | 0 | — | NOT RUN | 0 | — |
| remote-macos-config | NOT RUN | 0 | — | NOT RUN | 0 | — |
| scanner-word-boundary | NOT RUN | 0 | — | NOT RUN | 0 | — |
| server-port-ownership | NOT RUN | 0 | — | NOT RUN | 0 | — |
| shell-binary-output | NOT RUN | 0 | — | NOT RUN | 0 | — |
| shell-poll-completion | NOT RUN | 0 | — | NOT RUN | 0 | — |
| switch-hidden-index | NOT RUN | 0 | — | NOT RUN | 0 | — |
| terminal-nonseekable | NOT RUN | 0 | — | NOT RUN | 0 | — |

| Total | Run 1 | Run 2 |
|---|---|---|
| Tasks attempted | 0/20 | 0/20 |
| Pass/fail total | — | — |
| Tool calls | 0 | 0 |
| Task wall time | — | — |

Difference: **not measurable**; neither run executed.

Evidence: `.session/workspace-freeze-20261107/baseline-1-admission.json` and `baseline-result.json`. The failed admission is retained. No product changes or merge; draft PR #13 awaits Claude review.
