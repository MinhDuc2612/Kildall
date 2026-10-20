# kildallideas — every improvement idea + signature features (deep research, 2026-10-20)

**Method:** `/deep-research` workflow `wf_2cd186ee-70f` — 5 search angles, 50 sources read, 250 claims extracted.
Verification was **cut short by session limits** (56 of 107 agents finished; synthesis failed), so it was synthesized
by hand from the journal. Tags: **[V]** numbers confirmed by 3-vote check · **[1]** one source, not cross-checked.
Refuted votes (0-3) all agreed the paper *numbers* were right and rejected only extra conclusions drawn for Kildall.

**Not yet in the plan** unless marked *upgrade of #N*. Gain = expected effect on a small local model agent.
Cost = build effort. **★ = helps test #3 directly.**

---

## ⚡ ANSWER FIRST — top 10 by gain ÷ cost

| # | Idea | Gain | Cost |
|---|---|---|---|
| 1 ★ | Fixed coding workflow (localize → reproduce → edit → test) instead of a free agent loop | high | medium |
| 2 ★ | Loop breaker + escalate | high | low |
| 3 ★ | Personal repo eval from your git history (*upgrade of #13*) | high | low |
| 4 ★ | Prompt diet: ~200-token system prompt, per-turn skill cards, no idle tool schemas | high at 4K | low |
| 5 ★ | Lessons ledger (200-token lesson per task, top-1 recall) | high | low–med |
| 6 ★ | Overwrite guard (write refuses existing files) | medium | very low |
| 7 ★ | Specific tool-error messages + repeat-call breaker | medium | low |
| 8 | Scout-then-escalate routing (*upgrade of #2*) | high | medium |
| 9 | Test resident candidates: Qwen3-Coder-Next, Qwen 3.6 35B-A3B | high | low |
| 10 | Taint agent-written config files | med–high | low |

---

## A. Coding quality

1. ★ **Fixed workflow scaffold.** Zero-shot open models: 19% vs 3% (32B) and 7% vs 1% (7B) on SWE-Bench Lite with a
   constrained workflow (MoatlessTools) vs open ReAct (OpenHands). **[V]** (SWE-Gym)
2. ★ **Loop breaker.** Small agents loop: >25% of trajectories repeat a 10-step sequence (Claude <4%); a 10-step repeat
   = **89% failure**; zero-shot 32B stuck on 29.4% of tasks. Simple scaffold fixes cut loops but **did not raise solve
   rate alone** → pair with a forced strategy switch (search instead of paging) or escalation. **[V]** (SWE-smith, SWE-Gym)
3. **k-patch majority vote** (*upgrade of #9*): pick the most common exact patch: +4.5 pts; with model-written
   reproduction tests: 53.9% → 65.8%. Plateaus ~k=16–24. Mini PC (needs spare slots). **[1]** (CWM)
4. **Evolutionary refine (EvoScale):** 10 samples → keep best 5 → regenerate, ≤4 rounds; 32B Best@50 = 70B Best@500.
   Shown only in a pipeline setup, not an agent loop. **[1]** (Satori-SWE)
5. **Trajectory verifier** (SWE-RM, 30B-A3B): best-of-32 51.6% → 62.0%. **[V numbers]** But it needs **128K context**
   to score 99% of trajectories and 20K+ training samples — mini PC only, not cheap.
6. ★ **Overwrite guard:** write tool refuses to overwrite an existing file → must use edit. Fired on **57%** of tasks
   in little-coder (Qwen3.5-9B, 45.6% Aider Polyglot). **[1]**
7. **Thinking cap:** cap reasoning at 2,048 tokens; on overrun keep the partial thought, retry with thinking off
   (for Lane B/C/NIM thinking models). **[1]** (little-coder)
8. ★ **Prompt diet + skill cards:** ~200-token system prompt + 4 core tools beats ~10K-token prompts on local models;
   add only 80–150-token cards for tools likely needed this turn, ≤500 tokens; MCP schemas cost 7–9% of context →
   expose CLI tools directly. **[1]** (little-coder, PI agent)
9. ★ **Lessons ledger** (ReasoningBank): after every task — success *and* failure — store title + one line + content
   (~200 tokens); retrieve **top-1 only**. SWE-bench Verified +4.6 / +3.4 pts, up to 16% fewer steps; Gemma-3-12B
   17.1% → 24.1% (WebArena). Retrieving 2–4 lessons was worse than 1. A **wrong** lesson hurts (22.2% vs 26.3% with
   none) → gate on similarity. **[1]** (ReasoningBank, SWE-ContextBench)
10. **Teacher caveat for #90 LoRA:** self-training without a stronger teacher dropped 15.3% → 8.7%. Use a stronger
    open model (local giant) as teacher, plus verified-only samples. Never Claude/GPT outputs (standing rule). **[V]**

## B. Tool-call reliability

11. ★ **Specific error messages:** say what was wrong, never the answer. Static messages: 42.75 → 44.00; specific
    ones did better. Small models recover from tool errors ~20% of the time vs >50% for frontier models. **[1]** (Fission-GRPO)
12. ★ **Repeat-invalid-call breaker:** same failing call twice → show the schema, then escalate. **[1]**
13. **Keep "reason free, constrain late":** hard schemas on whole outputs cut small-model accuracy (91.5% → 48.0%
    on one task) while staying 100% valid. Kildall's lazy grammar (fires at the tool tag) already follows this —
    **keep it**. Do **not** force a tool-name enum: it kills "no tool needed" answers. Tested ≤4B only. **[1]**
14. **Malformed-call gate:** >5% malformed tool calls → fix template/config before trusting any eval; reuse
    llama.cpp `scripts/tool_bench.py`. **[1]**
15. **Startup template self-test:** Gemma needs `--jinja` + thinking off (Kildall has it); a stray space in
    `--chat-template-kwargs` silently routes tool calls to reasoning. One test call at boot. **[1]**

## C. Evaluation

16. ★ **Personal repo eval** (*upgrade of #13*): ~20 real bug fixes from your git history, each starting at the parent
    commit with a deterministic `verify.sh`; 8 easy / 8 medium / 4 hard + 2–3 trap tasks. Track pass rate, median
    turns to green, wall time, diff size vs the human fix, and **cheat rate** (edited tests, skipped asserts).
    Served context (8K vs 32K) moved scores more than Q4 vs Q5. **This is test #3 made repeatable.** **[1]**
17. **Separate metrics:** schema-valid · answer-correct · executable · wrong-but-valid. **[1]**
18. **Task generator (SWE-smith style):** inject bugs into your own repos → hundreds of test-verified tasks; procedural
    bugs train about as well as real PRs (8.6 vs 9.2 on 7B), at $0. **[V numbers]**

## D. Routing

19. **Scout-then-escalate** (*upgrade of #2*): resident runs ~3 turns; a small judge reads that partial trajectory and
    decides stay or escalate. Prompt-only routing did **not** beat the trivial baseline on SWE-Bench; trajectory
    routing +15.3 pts Route-AUC; judge = Qwen2.5-Coder-7B + LoRA. **[1]** (SWE-Router, cascade routing)
20. **Calibrated escalation** (*upgrade of #11*): token-margin from logprobs → isotonic error probability → threshold by
    cost: −31% cost, ECE 0.12 → 0.03 — but one preprint, NER only. **[1]** (UCCI)
21. **Quality estimates beat router cleverness** — per-leaf outcome logs (#14) matter more than the algorithm. **[1]**

## E. Speed and the mini PC

22. **Gemma MTP head, not a separate drafter:** 26B-A4B +45% (43.6 → 63.2 tok/s); separate E2B drafter **−27%**;
    dense 31B 3.7×. llama.cpp turns MTP off with `--parallel` > 1 → measure 1 slot + MTP vs 3 slots. Needed a fork
    at the time. **[1]** (sleepingrobots, HF Space)
23. **ngram-cache speculation** for prompt-echo work (extraction, RAG, editing code already in the prompt): no extra
    model, prefill ~flat; fresh writing −17% → per-skill switch. **[1]**
24. **Strix Halo defaults:** Vulkan RADV = stable default, ROCm = fast path; always `-fa 1` and `--load-mode none`;
    tune SWA checkpoint count. For the Linux port brief. **[1]** (kyuz0 toolboxes)
25. **Resident candidates to test:** Qwen3-Coder-Next (80B / 3B active, 256K, 70%+ SWE-bench Verified reported, ~37
    tok/s at 32K on Strix Halo); Qwen 3.6 35B-A3B (practitioners: steadier in long agent loops than Gemma 4 26B-A4B,
    which shows frequent multi-turn tool-call failures; Gemma better at extraction). One report: Qwen agents work at
    Q8, not Q4 → Kildall's 3-bit may cost tool reliability. **[1]**
26. ⚠️ **DeepSeek V4 Flash 284B fits 128 GB** (~2.9 bpw, 25–32 tok/s decode) **but exact prefill ~23 tok/s** on short
    prompts → too slow for agent loops until sparse prefill matures. Affects the "7/10 local model" plan. **[1]**

## F. Security

27. **Taint agent-written config:** 2026 sandbox escapes in Cursor, Codex, Gemini CLI and Claude Code came from the agent
    writing a file a trusted tool later runs (hook configs, `.git` metadata/fsmonitor, Docker socket). Mark files
    Kildall wrote; confirm before any trusted tool executes them; block `docker.sock`. **[1]** (BleepingComputer, Cymulate)
28. **Allowlist on full argv, not command names** (Codex trusted `git show` by name). **[1]**
29. **Gate every tool type** (Codex hooks fired for Bash only). Kildall's single `permissions.execute` boundary already
    does — add a regression test. **[1]**
30. **Argument-level policy monitor** (Progent): attack success 25.8% → 4.2%. **[1]**

---

## 🌟 Signature features (no other coding agent has these)

| | Feature | Why only Kildall can | Built on |
|---|---|---|---|
| S1 | **Type-ahead prefill** — Kildall reads the repo map, files and memory *while you type*; Enter only adds your last words | Reading is **92%** of Kildall's answer wait (measured); local compute is free, so speculative reading costs nothing | slice 5b2 |
| S2 | **Night Shift** — idle hours run k-patch votes / EvoScale on the day's hard tasks and your repo eval; morning report of fixes with tests green | Best-of-50 costs cloud agents real money; idle local slots cost $0 | ideas 3, 4, 16 |
| S3 | **Scout & Escalate per skill leaf** — resident scouts, a judge decides, escalation goes to the best model for that exact leaf (local giant or free NIM), carrying the scout's findings | Nobody else routes mid-task across 302 skill leaves | ideas 2, 19 |
| S4 | **Your Repo Gym** — a private benchmark built from your git history + injected bugs; every model swap, LoRA and router change is scored on *your* code; blind model duels per skill in idle time | Phase 10 "best per skill" becomes measured on your work, not leaderboards | ideas 16, 18 |
| S5 | **Lessons that survive model swaps** — a shared lessons ledger; a new model inherits what the old one learned on your repos | Kildall swaps models constantly; others are tied to one model | idea 9 |
| S6 | **Live taint map** — everything Kildall writes is tracked; any trusted tool about to run agent-written code/config pauses and shows the chain | Direct answer to 2026's sandbox-escape class | idea 27 |

---

## Sources
- SWE-Gym — https://arxiv.org/pdf/2412.21139 · SWE-smith — https://arxiv.org/pdf/2504.21798
- SWE-RM — https://arxiv.org/pdf/2512.21919 · Satori-SWE (EvoScale) — https://arxiv.org/pdf/2505.23604
- CWM — https://arxiv.org/pdf/2510.02387 · SWE-World — https://arxiv.org/pdf/2602.03419
- SWE-Router — https://arxiv.org/abs/2607.00053 · Cascade routing — https://arxiv.org/html/2410.10347v3 · UCCI — https://arxiv.org/abs/2605.18796
- ReasoningBank — https://arxiv.org/abs/2509.25140 · SWE-ContextBench — https://arxiv.org/html/2602.08316
- Constraint Tax — https://www.alphaxiv.org/abs/2605.26128 · Constrained decoding in small LLMs — https://arxiv.org/pdf/2609.23742
- XGrammar-2 — https://arxiv.org/pdf/2601.04426 · Repair, Not Improvement — https://arxiv.org/pdf/2608.13959 · Fission-GRPO — https://arxiv.org/html/2601.15625v1
- llama.cpp PR #12034 — https://cdn04132025.gitlink.org.cn/replica/llama.cpp/commit/669912d9a5bf927312c553332ff997f0a99da8fb
- little-coder — https://itayinbarr.substack.com/p/honey-i-shrunk-the-coding-agent · Local agent eval — https://llmconfigurator.com/en/guides/coding-agents/evaluate-local-coding-agent
- PI agent + local models — https://insiderllm.com/guides/pi-agent-local-models-ollama/ · HN thread — https://brianlovin.com/hn/47960507
- Gemma 4 MTP on Strix Halo — https://sleepingrobots.com/dreams/gemma4-mtp-assistant-strix-halo/ · MTP vs others — https://victor-mtp-on-hf-endpoints.static.hf.space/index.html
- Strix Halo toolboxes — https://github.com/kyuz0/amd-strix-halo-toolboxes · DeepSeek V4 Flash on Strix Halo — https://huggingface.co/julianmb/ds4fa
- Sandbox escapes — https://www.bleepingcomputer.com/news/security/cursor-codex-gemini-cli-antigravity-hit-by-sandbox-escapes/
- Prompt-injection defences — https://codex.danielvaughan.com/2026/07/08/out-of-band-prompt-injection-defences-camel-fides-progent-codex-cli-sandbox-approval-hooks/
- Leads not read in full: SideQuest KV management (https://arxiv.org/pdf/2602.22603v2), Scrouting (https://arxiv.org/pdf/2608.04804).

## Change log
- **2026-10-20** — Created from deep-research run `wf_2cd186ee-70f` (verification partial: session limits). Plan v52
  speculative-decoding note corrected the same day (26B-A4B: separate drafter −27%, MTP head +45%).
