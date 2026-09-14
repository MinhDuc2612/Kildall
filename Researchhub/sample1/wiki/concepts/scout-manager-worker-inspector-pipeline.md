# Scout / Manager / Worker / Inspector pipeline

A four-role agent pipeline for staged autonomy governance, triggered by a daily cron job: **Scout** (a cheap model, read-only, checks whether anything changed); **Manager** (the expensive/flagship model, decides what must happen and writes a work order but never executes it); **Worker** (a mid-tier model that does the actual work); **Inspector** (a fresh instance of the expensive model that reviews the Worker's output against the Manager's order). Demonstrated concretely using Claude Fable 5 as the Manager/Inspector model.

## Mentioned in
- [agentic OS](../../OrbiOS/agentic%20OS.md)
- [Fable 5 agentic OS build](../../OrbiOS/Fable%205%20agentic%20OS%20build.md)
