# Sub-agent forking

A distinct sub-agent pattern in Claude Code, the opposite of the normal isolation model: a forked sub-agent inherits the parent conversation's *full* context instead of starting fresh. Started via `/subtask`, or spawned automatically when "fork mode" is toggled on — the right choice when a task genuinely needs everything the parent already knows and you just want its noisy follow-up work kept out of the parent's context, versus a normal fresh sub-agent for a self-contained side task.

## Mentioned in
- [Claude Code sub-agent system](../../OrbiOS/Claude%20Code%20sub-agent%20system.md)
