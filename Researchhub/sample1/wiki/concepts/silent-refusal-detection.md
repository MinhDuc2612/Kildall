# Silent-refusal detection

An engineering discipline for autonomous agent pipelines: a model refusal can come back as a technically-successful response (HTTP 200, exit code 0), so scripts must check the model's own structured refusal/stop signal (its `stop_reason` field) rather than relying on exit code or transport-layer status alone.

## Mentioned in
- [agentic OS](../../OrbiOS/agentic%20OS.md)
- [Fable 5 agentic OS build](../../OrbiOS/Fable%205%20agentic%20OS%20build.md)
