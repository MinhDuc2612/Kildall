# Orbi computer mode — controlling the Mac

**Verdict first.** Orbi should build computer mode as **two layers, not one choice**:

| Layer | What it is | Vision model? | Extra RAM | Build |
|---|---|---|---|---|
| **A — accessibility tree** | Read `AXUIElement`, act on named elements | **No** | **0 GB** | **First** |
| **B — pixel vision** | Screenshot → predict click coordinates | Yes | ~4–8 GB | **Fallback only** |

**Layer A covers roughly everything Orbi actually needs and costs nothing.** macOS exposes a
structured tree of every button, field and menu in every running app. That is text. Lane A already
reads text. **No vision model, no extra residency, no change to the 24 GB budget.**

**Layer B exists only for what the tree cannot see** — canvas apps, games, remote desktop windows,
custom-drawn UIs and images. Run A first, fall to B only on an empty tree, and log which path ran.

🔴 **The most important finding in this file is in §4, and it is a security finding, not a capability
one: every published defence against prompt injection of computer-use agents fails.** Measured
attack success reaches **51% on computer-use agents and 100% on browser-use agents**.
**System-prompt defences do not measurably help.** That decides how Orbi ships computer mode, and it
is why §5 makes it opt-in, attended, and never default.

---

## 1. The four architectures

Computer use is not one technique. Conflating them is the main error in most write-ups.

| # | Approach | How it perceives | Needs a vision model | Auditable before acting |
|---|---|---|---|---|
| **1** | **OS accessibility tree** | `AXUIElement` structured element tree | No | **Yes** — role + label known |
| **2** | **Browser a11y tree / DOM** | Playwright accessibility snapshot | No | **Yes** |
| **3** | **Pixel vision grounding** | Screenshot → coordinates | **Yes** | **No** — coordinates only |
| **4** | **Delegation** | Nothing. Another agent drives. | No | No — opaque |

**Why "auditable" is the column that matters for Orbi.** Phase 3 defines an Auto / Confirm / Never
permission model. Approaches 1 and 2 hand Orbi the element's **role and label before it acts**, so
"am I about to click *Delete*?" is answerable and routable to the Confirm tier. Approach 3 returns
coordinates and cannot reliably say what is underneath them. **A pixel-only build walks straight
through the permission system.**

⚠️ **Auditable is not the same as safe.** See §4 — layer A is checkable but *still* injectable.

---

## 2. The tool landscape — verified 2026-09-21

**Every row below was verified directly against the GitHub and Hugging Face APIs on 2026-09-21**,
not from search summaries. This matters: the automated research pass behind this file **lost its
verification phase to a session limit** (see §7), so the factual table was re-checked by hand.

| Project | Stars | License | Last push | Architecture | Local-only |
|---|---|---|---|---|---|
| `browser-use/browser-use` | **115,727** | MIT | 2026-09-18 | browser, DOM + optional vision | yes |
| `microsoft/playwright-mcp` | **37,435** | Apache-2.0 | 2026-09-18 | browser, **a11y snapshot** | yes |
| `wonderwhy-er/DesktopCommanderMCP` | 9,682 | MIT | 2026-09-21 | shell + files, **not GUI** | yes |
| `microsoft/Fara` | 6,189 | MIT | 2026-07-22 | **pixel vision model** | yes |
| `openclaw/Peekaboo` | **5,193** | MIT | 2026-09-21 | **hybrid** a11y + screenshot | yes |
| `xlang-ai/OpenCUA` | 843 | MIT | 2026-05-25 | **pixel vision models** | yes |
| `macOS26/Agent` | 621 | ⚠️ **NOASSERTION** | 2026-09-21 | Apple Events + AX + XPC | yes |
| `CursorTouch/macOS-MCP` | 185 | MIT | 2026-09-09 | **AX API + AppleScript** | yes |
| `hanzili/comet-mcp` | 180 | MIT | ⚠️ **2026-01-13** | **delegation → cloud** | **no** |
| `munimtechnologies/munim-computer-use` | 7 | Apache-2.0 | 2026-09-20 | Swift, AX + ScreenCaptureKit | yes |
| `CursorTouch/macOS-use` | 5 | 🔴 **NONE** | 2026-05-13 | AX API | yes |
| `entpnomad/mac-use` | 5 | MIT | 2026-03-30 | AppleScript + System Events | yes |
| `danilonovaisv/MacOS-Use` | 1 | MIT | 2026-09-16 | AX API | yes |

### Three corrections

🔴 **`comet-mcp` is not viable for Orbi, on two independent grounds.** It is a **delegation bridge**,
not a computer-use tool: the agent sends a goal → MCP → Chrome DevTools Protocol → **Perplexity
Comet**, a proprietary cloud browser that performs every action. There is no local fallback path,
which disqualifies it under Orbi's local-first, never-spend rules. Separately it was **last pushed
2026-01-13 — eight months stale.** Its *delegation pattern* is worth studying; its implementation is
not adoptable.

🔴 **`CursorTouch/macOS-use` has no license file at all.** Not permissive, not restrictive — absent.
Legally unusable in a product; do not vendor it. Do not confuse it with **`CursorTouch/macOS-MCP`**
(185 stars, MIT, actively pushed), which is the real project in that org.

⚠️ **"MacOS-Use" names at least three different repos** — 5, 5 and 1 stars, different licenses,
different maintenance states. Any claim about "MacOS-Use" must name the owner. Real adoption in this
category sits with **`openclaw/Peekaboo` (5,193)** and **`CursorTouch/macOS-MCP` (185)**.

⚠️ **`macOS26/Agent` reports `NOASSERTION`** — GitHub cannot identify its license despite the project
describing itself as open source. Orbi's standing rule is to check licence per component and exclude
unclear terms. **Resolve before adopting.**

### What to actually use

| Need | Pick | Why |
|---|---|---|
| **Browser control** | **`microsoft/playwright-mcp`** | Apache-2.0, 37k stars, a11y snapshot not screenshots, Microsoft-maintained |
| **macOS app control** | **`openclaw/Peekaboo`** | MIT, 5.2k stars, pushed 2026-09-21, hybrid a11y + capture, macOS-native CLI with optional MCP |
| **Lighter macOS option** | `CursorTouch/macOS-MCP` | MIT, AX + AppleScript, no VLM required |
| **Shell and files** | *(already Orbi's own)* | `DesktopCommanderMCP` overlaps Phase 4's own tool layer |

---

## 3. Models — and why the benchmark numbers mean less than they look

### The numbers already in Orbi's research, re-examined

| Model | Claimed | Status after checking |
|---|---|---|
| Qwen3.8-27B | **84.3% OSWorld-Verified** | Corroborated at BenchLM rank 4 — **but listed by bare model name, no scaffold identified** |
| Qwen3.5-122B-A10B | **0.704 ScreenSpot-Pro** | Corroborated at rank #9, flagged open-weight — **but it is not the top open model** |

🔴 **Correction to `sample1/OrbiLLM/Orbi OSSLLM research.md` lines 140–141.** That file states
Qwen3.5-122B-A10B is *"the top-ranked open-source model on ScreenSpot Pro"*. **It is not.**
**Meta's Muse Glimmer-30B leads open models at 0.754 (rank #7)**, above every open Qwen entry.
⚠️ Unverified pending the §7 re-run — but that leaf's evidence line needs re-checking either way.

⚠️ **`sample3/OrbiOSS.md` line 257 is also stale on this.** It records Qwen3-VL-235B-A22B as
*"Top-ranked open model on OSWorld, 0.667 (rank #5 overall) — the computer-use ceiling for open
weights."* **That model was dropped from the project on 2026-09-06.** So sample 3's only
computer-use claim points at a model Orbi no longer carries.

### Four findings that matter more than any leaderboard position

🔑 **1. These are system scores, not model scores.** Computer-use results are substantially
determined by the **scaffold** — prompts, tool surface, termination rules, retries, judges — rather
than by weights. OSWorld's own page says its rankings reflect *"submitted system setups (model plus
tools and policy), not just a base model."*

🔑 **2. Scaffold moves the score by tens of points.** A **Qwen 3B** model with a simplified XML
prompt reached roughly **50%** on Showdown-Clicks, against roughly **20% for Qwen 72B**. The prompt
was worth more than 24× the parameters.

🔑 **3. Small specialised beats large general, decisively.** On Showdown-Clicks a large off-the-shelf
model scores **~20%**, while small fine-tuned grounding models score **~70–80%**.

🔑 **4. So Orbi does not need a giant vision model for layer B.** The 27B dense and 122B picks
currently implied by the model list are the wrong shape for this job. A small specialised grounder
is both better at it and affordable.

### Layer B candidates, if and when it is built

| Model | Size | License | Measured | Note |
|---|---|---|---|---|
| **BrowserVLM** | **0.54 B** (~0.94 B with vision tower) | ⚠️ unverified | grounding only | **Ships GGUF + a llama.cpp fork, runs on Apple Silicon MPS** — directly usable on Orbi's stack |
| `microsoft/Fara-7B` | 7 B | **MIT** | — | SFT of Qwen2.5-VL-7B. **Discards the accessibility tree at inference**; pure screenshots |
| `xlangai/OpenCUA-7B` | 7 B | **MIT** | **26.6% OSWorld-Verified** | The affordable tier, and it is weak |
| OpenCUA-32B / 72B | 32 B / 72 B | MIT | **72B: 45.0% OSWorld-V, 60.8% ScreenSpot-Pro** | Will not fit 24 GB |

⚠️ **A steep capability cliff.** OpenCUA drops from **45.0% at 72B to 26.6% at 7B** on
OSWorld-Verified. The tier Orbi can afford is the weak tier. This is the strongest argument for
keeping layer B narrow — a fallback for blind spots, never the primary path.

⚠️ **Every ScreenSpot-Pro score is self-reported by the model vendor**, with no independent audit.
Treat that whole leaderboard as vendor claims.

⚠️ **Counter-signal, recorded rather than buried.** **BrowserOS officially restricts local models to
Chat Mode and excludes them from Agent Mode**, its own docs stating local LLMs are not capable enough
for agentic browser control. One practitioner's reported threshold is **>7 B parameters** for
reliable tool-calling, with models fine for chat failing when asked to invoke browser tools.
**Orbi's Lane A has 4 B active. Whether it can drive a GUI at all is unmeasured — and that is
phase CU-0's only job.**

---

## 4. 🔴 Security — every published defence fails

This finding should govern the whole feature.

### Measured attack success

| Attack | Success rate | Scope |
|---|---|---|
| Visual prompt injection → **computer-use agents** | **up to 51%** | 306-case benchmark |
| Visual prompt injection → **browser-use agents** | **up to 100%** | Amazon, Booking.com, BBC News, Messenger, Email |

### What does not work

- **System-prompt defences do not measurably reduce attack success or attempt rates.** The cheapest
  and most commonly proposed mitigation is ineffective.
- **Layered defence is also insufficient.** Model-level fine-tuning **plus** a framework defence
  layer **plus** prompt-level instructions still leaves agents vulnerable. **No published defence
  stack is sufficient for an autonomous GUI-control agent.**

### Why a better model will not fix it

**The root cause is architectural: the prompt is assembled with no trust boundary between the user's
instructions and page content.** Improving the model does not help. The prompt construction has to
change.

### Layer A is auditable but still injectable

⚠️ **This corrects the intuition that the accessibility tree is inherently safe.**
**Playwright MCP's accessibility-snapshot mode is vulnerable to indirect prompt injection**: a
malicious page embeds instructions in accessibility-tree attributes such as `aria-label`, the
snapshot passes them faithfully to the model, and the model may follow them.

Layer A's real advantage is narrower and more precise than "it is safe": **it lets Orbi check what
it is about to click.** It does **not** stop the page from talking to the model.

### Other documented vectors

- **Images carry injections invisible to humans.** Screenshot → OCR → text fed to the model
  unmarked. **Any vision loop is an injection surface, not just the DOM.**
- **Timing attacks.** AgentScan showed a notification injected milliseconds before an intended click
  diverting the tap to an attacker's pop-up, with consequences including malware installation and
  phishing redirection.
- **No session trust boundary.** Multi-page MCP browser sessions retain context across sites, so
  nothing separates legitimate content from injected instructions.
- **Real agent-level outcomes**, not merely confused text: navigation to attacker URLs, form
  submission, and cross-page data exfiltration within one session.

### What the existing tools do about it

**Almost nothing.**

| Project | Security model |
|---|---|
| `CursorTouch/macOS-MCP` | **None.** No sandbox, confirmation, allow-list or region restriction |
| MacOS-Use family | **None.** Its own documented mitigation is *"run it in a VM or on a throwaway Mac"* |
| `openclaw/Peekaboo` | OS-level TCC grants only — Screen Recording + Accessibility, all-or-nothing |
| `entpnomad/mac-use` | **None.** A grep of its 1,126-line server for confirm/allowlist/sandbox/approve found only an error string |
| `comet-mcp` | **None**, and worse: six coarse verbs mean the host sees one opaque `ask` and cannot gate individual actions |

🔑 **The whole category ships with no permission model. Orbi's Phase 3 tiers would be the
distinguishing feature, not a formality.**

---

## 5. What Orbi should build

### The rule

```
1. Try the accessibility tree.
2. Usable element returned?  → act on it, with role + label checked
                                against the Phase 3 permission tiers.
3. Tree empty or unusable?   → fall through to pixel vision,
                                LOG that this happened,
                                and require Confirm for any action.
4. Always record which path ran.
```

### Non-negotiables, all consequences of §4

1. **Computer mode is opt-in and off by default.** Not a capability Orbi has until asked.
2. **Never runs unattended.** §4's numbers make autonomous GUI control indefensible today.
3. **Every action passes the Phase 3 tiers before the event is synthesised**, not after.
4. **Screen and page content is data, never instructions** — the Phase 3 rule extended to the
   accessibility tree and to OCR'd screenshots, because both are proven injection surfaces.
5. **Application allow-list.** Orbi drives only apps the user named.
6. **The pixel path always requires Confirm.** It cannot name what it is clicking.
7. **Log every action with its path, target element and outcome.**

### Suggested phases

| Phase | Content | Depends on |
|---|---|---|
| **CU-0** | **Measure first.** Can Lane A (4 B active) drive an accessibility tree at all? Go/no-go, currently unknown | Phase 3 |
| **CU-1** | Layer A — macOS AX tree via Peekaboo or macOS-MCP, wired to the Phase 3 tiers, app allow-list, full logging | CU-0 |
| **CU-2** | Layer A for the browser — `playwright-mcp` accessibility snapshot | CU-1 |
| **CU-3** | Layer B — small specialised grounder, fallback only, Confirm-gated | CU-2, plus RAM headroom that does not exist today |

⚠️ **CU-3 has an unmet hardware precondition.** Lane A alone already runs **96 of 121 memory-pressure
samples in warning**. A resident vision model is not currently affordable. Measure before planning it.

---

## 6. Does one layer include the other?

**No. Neither contains the other.**

| Target | A — tree | B — pixels |
|---|---|---|
| Mail, Finder, Calendar, Safari, web apps, forms | ✅ exact | ⚠️ ~70% |
| Figma, canvas apps, games | ❌ **blind** | ⚠️ ~70% |
| Remote desktop / VNC | ❌ **blind** | ⚠️ ~70% |
| A screenshot handed to it | ❌ **blind** | ⚠️ ~70% |

**A is blind to the bottom three — a hard wall, not a quality gap.** **B sees all four badly and
cannot say what it clicked.** So the build is **A then B**: A is free, exact and checkable; B is the
only thing that reaches the blind spots.

---

## 7. ⚠️ Verification status — read before trusting this file

**The automated research pass behind this file lost its verification phase.** Of 105 agents,
**30 completed and 75 failed** with `You've hit your session limit`. The extraction agents fetched
real sources; the 3-vote adversarial verification never ran.

Per this project's own standing lesson — *do not merge automated research that ran out of quota* —
the claims are labelled, not laundered:

| Status | What it covers |
|---|---|
| ✅ **Hand-verified 2026-09-21** | **Every row of §2's table** — stars, licenses, push dates, via the GitHub API. Both Hugging Face entries in §3, via the HF API |
| ⚠️ **Extracted, not cross-verified** | All of §3's benchmark numbers and all of §4's attack rates. Fetched from real sources by agents whose verification pass then died |
| 🔲 **Not attempted** | Independent reproduction of any benchmark. Orbi has measured none of this on its own hardware |

**Before acting on §3 or §4, re-run the verification pass.** Re-check specifically: the
Muse Glimmer-30B vs Qwen3.5-122B-A10B ScreenSpot-Pro ordering, the 51% / 100% injection rates, the
OpenCUA tier scores, and BrowserVLM's license and GGUF availability.

---

## Sources

**Verified by direct API call, 2026-09-21:** GitHub API for every §2 repository; Hugging Face API for
`xlangai/OpenCUA-7B` and `microsoft/Fara-7B`.

**Fetched by research agents, verification incomplete:** BenchLM OSWorld-Verified leaderboard,
llm-stats OSWorld and ScreenSpot-Pro leaderboards, Steel.dev OSWorld leaderboard, project READMEs for
each §2 entry, and the prompt-injection literature underlying §4 — including the 306-case
visual-injection benchmark and the AgentScan notification-timing result.

---

## Change log

- **2026-09-21 — created.** Written after finding computer use appeared **zero times** in
  `Orbiplan.md` and `Orbichecklist.md`, despite four benchmark-tagged leaves in
  `sample1/OrbiLLM/Orbi OSSLLM research.md` (lines 140, 141, 269, 270) and a model assignment in
  `Orbimodels.md`. The same structural gap `UHWmini.md` had before 2026-09-11: real research, no
  execution path. §2 hand-verified against live APIs; §3 and §4 carry the quota-failure caveat in §7.
