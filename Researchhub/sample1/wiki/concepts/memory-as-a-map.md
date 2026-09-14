# Memory as a map (not a database)

The recurring, explicitly-stated distinction that a Markdown vault used as an agent's "memory" is not semantic/RAG memory but cheap navigation: a folder structure plus an `index.md` table-of-contents at every level, so the agent can find the right file quickly at scale, cutting both token usage and lookup latency — "it's not really giving it more memory, it's giving it a map," and explicitly "not like a graph RAG at all." The specific `raw/ → wiki/ → outputs/` folder convention (raw = unsynthesized dumps, wiki = agent-authored synthesized articles, outputs = deliverables) is credited to Andrej Karpathy's viral April 2026 tweet. Whether a notes-vault app is even the right tool for this is contested in community discussion — one Reddit commenter argues a dedicated local-agent-memory harness is a better fit.

## Mentioned in
- [agentic OS](../../OrbiOS/agentic%20OS.md)
- [Claude Code agentic OS four-level framework](../../OrbiOS/Claude%20Code%20agentic%20OS%20four-level%20framework.md)
- [Claude Code Obsidian voice command center](../../OrbiOS/Claude%20Code%20Obsidian%20voice%20command%20center.md)
