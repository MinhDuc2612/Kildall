# Researchhub Wiki — Index

Auto-built from every research file in `Researchhub/` (OrbiIntelligent, OrbiLLM, OrbiOS). 175 entity pages + 57 concept pages, each linking back to the source doc(s) that discuss it. Built 2026-08-24 by reading every research file and extracting only what's actually stated in them — unverified claims in a source doc carry that caveat into its wiki page rather than being stated as fact.

## How to use this

- `entities/` — real people, companies, and named tools/products/models found across the research (175 pages)
- `concepts/` — named techniques, frameworks, and patterns found across the research (57 pages)
- Each page has a "Mentioned in" list linking back to every Researchhub doc that discusses it — the wiki is a cross-reference index, not a replacement for the source docs themselves

## By source folder

**OrbiIntelligent/** (business-automation research: lead-gen, onboarding, content tools) — 88 entities, 14 concepts. Notable cross-cutting entities: [[n8n]], [[gohighlevel]], [[apollo-io]], [[blotato]], [[lobo-brothers-ai-automation]] (creator of most watched reels in this folder).

**OrbiLLM/** (open-weight model research + hardware minimization) — 56 entities, 24 concepts. Notable: [[kimi-k3]], [[llama.cpp]], [[moonshot-ai]], [[unsloth]] — plus the hardware-minimization concept cluster ([[moe-expert-streaming]], [[gguf-quantization]], [[extreme-sub-2-bit-quantization]]).

**OrbiOS/** (agentic-OS pattern research from watched videos/reels) — 36 entities, 18 concepts. Notable: [[anthropic]], [[claude-code]], [[hermes-agent]], [[fable-5]] — plus the pattern-level concepts ([[agentic-os]], [[staged-autonomy-governance]], [[scout-manager-worker-inspector-pipeline]]).

## Known gaps

- This wiki reflects the research docs as of 2026-08-24. It does not auto-update — re-run this analysis after adding new research files.
- Some entities appear only once (a single mention in one doc); others (Anthropic, Claude Code, n8n, GoHighLevel) recur across many docs and are genuine cross-cutting reference points worth reading first if you're new to this vault.
- A handful of source docs (Orbi OSSLLM research.md especially) are large enough that only the most prominent named entities got their own page — sub-detail lives in the source doc itself, not duplicated here.

## Change log

- 2026-08-24 — Created. Built by 3 parallel research passes (one per Researchhub subfolder) reading all 27 research .md files and extracting entities/concepts into `wiki/entities/` and `wiki/concepts/`, then this index tying it together. Cross-checked for slug collisions between the parallel passes — none found (spot-checked `anthropic.md` and `claude-code.md`, the two most likely collision candidates; both intact, single-author, no data loss).
