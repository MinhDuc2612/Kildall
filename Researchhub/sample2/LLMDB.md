# LLMDB — TencentDB Agent Memory

**Built:** 2026-09-02 · Sample 2 · self-contained
**Source:** [github.com/TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory)
— README and live GitHub API, both read 2026-09-02.

**One line:** a **team-level memory hub for AI agents** that turns conversations, documents and code
into four governed, shareable memory assets — and plugs into **Claude Code by pointing a base URL at
a proxy**, with no plugin, hook or MCP server.

---

## 1. Verified facts

| Field | Value |
|---|---|
| Repo | [`TencentCloud/TencentDB-Agent-Memory`](https://github.com/TencentCloud/TencentDB-Agent-Memory) |
| Licence | **MIT** — see the correction below |
| Stars / forks | **25,580 / 2,387** |
| Open issues | **764** |
| Language | **TypeScript** |
| Created | 2026-04-07 |
| Last push | 2026-08-31 |
| Archived | No |
| npm | `@tencentdb-agent-memory/memory-tencentdb` |
| Requires | **Node ≥ 22.16**, OpenClaw ≥ 2026.3.13 |

### ⚠️ Licence correction — GitHub reports this wrong

**GitHub's API returns `NOASSERTION` / "Other"** for this repository, which normally signals an
unlicensed or custom-licensed project and is a deployment blocker.

**That is a detection failure, not the licence.** Reading `LICENSE` directly:

> *"Tencent is pleased to support the open source community by making TencentDB Agent Memory
> available. Copyright (C) 2026 Tencent. All rights reserved. **TencentDB Agent Memory is licensed
> under the MIT.**"* — followed by the full, unmodified MIT terms.

**It is MIT.** GitHub's classifier fails because Tencent prepends a corporate preamble before the
standard text. **Anyone filtering repositories by GitHub's licence field would wrongly exclude this
one** — worth knowing generally, since Tencent uses that preamble across its open-source portfolio.

### ⚠️ A second error, in their own README

The README's install block says:

```bash
git clone https://github.com/Tencent/TencentDB-Agent-Memory.git
```

**The repository is `TencentCloud/TencentDB-Agent-Memory`, not `Tencent/`.** Verify the org before
cloning.

---

## 2. What it actually is

Not a vector database, and not a chat-log store. The README's own framing:

> *"Memory here means more than just 'remembering conversations.' **Any information that helps the
> next Agent avoid reinventing the wheel** should be saved, organized, and reused."*

> *"Existing information → Reusable memory assets → Fewer turns → Less rework → More stable results
> and higher efficiency"*

### The four memory assets

| Asset | What it holds |
|---|---|
| **Chat Memory** | preferences, facts, decisions, interaction history — each agent gets its own automatically |
| **Skill** | reusable expertise extracted from completed work — **with versions, resource files, trigger boundaries, execution steps and validation rules**. *"A Skill isn't just a prompt snippet."* Private by default; shareable to the team after review |
| **LLM-Wiki** | documents turned into searchable pages with **link-graph drill-down** |
| **Code-Graph** | codebases indexed into **files, symbols and call relationships** |

**Skills having versions, trigger boundaries and validation rules is the strongest design idea here.**
It treats an agent capability as a governed artefact rather than a prompt string — the same instinct
behind Prime Agent's executable skills in `LLM train/LLM-autotrain.md`, but with team governance on top.

---

## 3. The architecture

### L0–L3 memory layering

Conversations are stored raw, then refined by an **async pipeline** into levels of granularity:

| Layer | Stores | Used for |
|---|---|---|
| **L0 Conversation** | raw conversations, full context | verifying exact wording, timestamps, sources |
| **L1 Atom** | facts, preferences, constraints, events | precise recall of actionable information |
| **L2 Scenario** | knowledge blocks around projects/scenarios | quickly restoring a working context |
| **L3 Core / Persona** | long-term profiles, stable patterns, high-level cognition | entering a user's or team's context fast |

**Retrieval is layered too, and this is the clever part:** L2/L3 give a **quick context bootstrap**;
when specific facts are needed it **falls back down** to L1/L0 using **BM25 + vector retrieval + RRF**
(reciprocal rank fusion — hybrid keyword *and* semantic).

> **"Results are further capped by item count, character budget, and timeout limits to prevent memory
> from overwhelming the context window."**

**That constraint is the mature detail.** The failure mode of every memory system is dumping so much
recalled context that it crowds out the actual task. Capping on **three axes — count, characters and
time** — is a direct answer, and it is the same context-rot problem `deepresearch.md` documents
HyperResearch solving with just-in-time step loading.

### Governance: Fixed Binding + ACL

All four asset types register uniformly as **Memory Assets**. The Hub uses **Fixed Binding + ACL** to
decide what a given agent may use: **first narrow by Team, User, Agent and visibility, then retrieve**.

> *"This lets teams share experience without exposing all their private information; switching Agents
> or frameworks only requires **re-equipping, not retraining**."*

**Permission-scope-then-retrieve is the right order** — filtering after retrieval leaks.

### On-demand knowledge

Agents discover capabilities via **`/v3/tools/list`**, then read pages, source, or impact paths via
**`/v3/tools/call`**. Documents and code *"remain available tools that only enter context when truly
needed."*

---

## 4. Integration — the part that matters for Claude Code

> **"One Proxy, unchanged protocol, zero-code integration — point the Agent's base URL to the Proxy
> and it's done. No plugin, hook, or MCP server is required."**

**Supported agents, each with its own install section:** **Claude Code** · Codex · DeepSeek Harness ·
CodeBuddy · WorkBuddy · Hermes · OpenClaw — plus a generic adapter guide.

**Three services** run together: `memory-core` + `memory-hub` + `proxy`, deployed from
`deploy/global-images`, configured with **two sets of LLM parameters** (one for the memory group, one
for the proxy group).

**The proxy approach is a genuine architectural choice.** MCP servers and hooks bind you to one
framework; a base-URL swap works with anything speaking the same protocol. It also means **every
request routes through their proxy** — see §6.

---

## 5. The benchmark

| Benchmark | Without | With | Relative |
|---|---|---|---|
| **PersonaMem** | 48% | **76%** | **+59%** |

*"PersonaMem tests whether an Agent can correctly understand and apply user information after extended
interactions."*

**One benchmark, self-reported, no third-party validation.** A 48→76% jump is large and plausible for
a memory system on a memory benchmark — but it is exactly the benchmark the product is built to win.
**Treat it as directional.**

---

## 6. Honest assessment

### What is genuinely good

1. **The README states its own incomplete parts.** Verbatim:
   - *"Wiki and CodeGraph are built **asynchronously**; allow some processing time before they reach `ready` status."*
   - *"CodeGraph currently **prioritizes public HTTPS repositories**; support for private repositories and SSH credentials is **still being refined**."*
   - *"The Hub supports **manual** asset binding; **fully automated memory routing is still under iteration**."*

   **That third one materially qualifies the pitch.** The vision is memory that flows automatically
   between agents; the shipped reality is that a human binds assets manually.

2. **Skills as governed artefacts** — versions, trigger boundaries, validation rules, review before
   sharing.
3. **Context-budget caps** on three axes.
4. **Permission-before-retrieval** ordering.
5. **MIT**, genuinely — despite GitHub's misreport.

### What to weigh before deploying

- **764 open issues** against 25,580 stars, on a repo **under five months old**. Fast-moving and
  heavily used, or strained — not determinable from counts alone.
- **"Team Memory Beta is evolving quickly"** — the README's own word is *Beta*.
- **A v2→v3 migration tool exists already**, in a project created 2026-04-07. **Breaking changes have
  already happened once** in under five months.
- **Everything routes through their proxy.** Zero-code integration is bought by putting a component
  between your agent and its model. On a self-hosted deployment that is your own box — but it is the
  correct thing to be deliberate about, and the deployment asks for **two sets of LLM credentials**.
- **CodeGraph on public HTTPS repos first** means the private-repo path — the one most teams need — is
  the less-finished one.

---

## 7. Where it fits in this vault

| File | Layer | Relationship |
|---|---|---|
| `UHWmini.md` | running a model locally | LLMDB is orthogonal — it manages *context*, not inference |
| `LLM train/LLM-autotrain.md` | Prime Agent's `/refine`, self-written skills | **Same instinct.** Prime Agent persists skills for **one agent**; LLMDB governs them **across a team**, with ACL and review |
| `deepresearch.md` | HyperResearch's compounding source vault | **Same problem, different scope** — HyperResearch accumulates *sources*; LLMDB accumulates *experience* |
| `LLM train/Unsloth-finetune&train.md` | changing the weights | **The alternative to fine-tuning.** LLMDB improves behaviour by managing context; fine-tuning does it by changing the model |

**The last row is the useful framing.** When an agent keeps getting something wrong, there are two
fixes: **retrain it** (Unsloth, Soup) or **give it better memory** (LLMDB). Memory is cheaper,
reversible, and auditable. Fine-tuning is permanent and needs data. **Try memory first.**

---

## 8. Honest gaps

- **Not deployed, not run, nothing measured.** All claims are the project's own.
- **The PersonaMem result is single-source and self-reported.** No third-party reproduction sought.
- **Linked docs not read:** `INSTALL.md`, `ROADMAP.md`, the four v3 API documents, the Knowledge
  OpenAPI spec.
- **The 764 open issues were not sampled**, so their severity is unknown.
- **No security review.** The proxy sits in the request path and holds LLM credentials; its auth and
  isolation model were not examined.
- **"TencentDB" in the name was not resolved** — whether a Tencent Cloud managed database is required,
  optional, or merely the origin of the name is unestablished. **Check before assuming it runs fully
  self-hosted.**

## 9. Sources

1. [`TencentCloud/TencentDB-Agent-Memory`](https://github.com/TencentCloud/TencentDB-Agent-Memory) — primary: README, `LICENSE`, and live GitHub API metadata, 2026-09-02
2. [`@tencentdb-agent-memory/memory-tencentdb` on npm](https://www.npmjs.com/package/@tencentdb-agent-memory/memory-tencentdb)
3. `INSTALL.md`, `ROADMAP.md`, `MemoryCore/v3-api-memorycore-doc.md`, `MemoryKnowledge/openapi.yaml`, `MemoryProxy/v3-api-memoryproxy-doc.md` — **identified in the README, not read**

## Change Log

- **2026-09-02** — Created from the repo's README, its `LICENSE` file, and live GitHub API metadata:
  **25,580 stars, 2,387 forks, 764 open issues, TypeScript, created 2026-04-07, pushed 2026-08-31**.
  **Two errors corrected.** First, **GitHub's API reports the licence as `NOASSERTION`/"Other"**,
  which normally reads as a deployment blocker — but reading `LICENSE` directly shows *"TencentDB
  Agent Memory is licensed under the MIT"* followed by the full unmodified MIT terms. **It is MIT**;
  GitHub's classifier is defeated by Tencent's corporate preamble, so anyone filtering repos by
  GitHub's licence field would wrongly exclude it. Second, **the README's own install block clones
  `Tencent/TencentDB-Agent-Memory` when the repository is `TencentCloud/`**.
  Documented the architecture: **four memory assets** (Chat Memory, Skill, LLM-Wiki, Code-Graph) over
  an **L0–L3 layering** — raw conversation, extracted atoms, scenario blocks, long-term persona —
  where **L2/L3 give a fast context bootstrap and retrieval falls back to L1/L0 via BM25 + vector +
  RRF**, with results **capped by item count, character budget and timeout** *"to prevent memory from
  overwhelming the context window"*. Recorded **Fixed Binding + ACL** governance that narrows by team,
  user, agent and visibility **before** retrieving, and the on-demand `/v3/tools/list` →
  `/v3/tools/call` knowledge path.
  Noted the integration model — **"point the Agent's base URL to the Proxy... No plugin, hook, or MCP
  server is required"** — with named support for **Claude Code**, Codex, DeepSeek Harness, CodeBuddy,
  WorkBuddy, Hermes and OpenClaw, running as three services (`memory-core` + `memory-hub` + `proxy`)
  configured with two sets of LLM credentials.
  Recorded the benchmark honestly: **PersonaMem 48% → 76% (+59%)**, single-source, self-reported, and
  on precisely the benchmark the product is designed to win. Balanced it against the README's own
  admissions — **Wiki and CodeGraph build asynchronously**, **CodeGraph prioritises public HTTPS repos
  with private/SSH support "still being refined"**, and **"fully automated memory routing is still
  under iteration"** with only manual binding shipped, which materially qualifies the pitch. Flagged
  **764 open issues on a repo under five months old**, the README's own *Beta* label, and the
  existence of a **v2→v3 migration tool** showing breaking changes have already occurred once.
  Placed it against the rest of the vault, with the framing that when an agent keeps getting something
  wrong there are two fixes — **retrain it** (`LLM train/Unsloth-finetune&train.md`, `LLM train/Soup-finetune&train.md`) or
  **give it better memory** (this) — and that memory is cheaper, reversible and auditable, so it
  should be tried first. Left open the unresolved question of **whether "TencentDB" implies a required
  Tencent Cloud managed database**, which should be checked before assuming a fully self-hosted deploy.
