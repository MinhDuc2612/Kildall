# Model tiering

Routing routine/frequent agent checks to a cheap, fast model and reserving an expensive, capable model for actual decisions — the cost-control pattern that makes running a frontier model as a persistent background agent economically viable rather than a demo that burns money. One source cites roughly a 60x per-call cost difference between the cheap and expensive tiers (~$0.001/call at 1,200+ calls/day vs. ~$0.068/call at ~40 calls/day). The Scout (cheap) / Manager (expensive) split in the Scout/Manager/Worker/Inspector pipeline is a concrete instance of this same pattern.

## Mentioned in
- [agentic OS](../../OrbiOS/agentic%20OS.md)
- [Claude Fable 5 agentic OS](../../OrbiOS/Claude%20Fable%205%20agentic%20OS.md)
- [Fable 5 agentic OS build](../../OrbiOS/Fable%205%20agentic%20OS%20build.md)
