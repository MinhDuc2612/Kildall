# Frozen repo-eval baseline attempt — 2026-11-07

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
