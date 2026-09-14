---
title: ScrapeGraphAI free lead scraping via Claude Code
source_url: https://www.instagram.com/reel/DbvWERsuDuA/
watched: 2026-08-19
intent: research about it (leads find)
hero_frames:
  - hero-repo-card.jpg
  - hero-cost-compare.jpg
  - hero-claude-install.jpg
---

## TL;DR
- Demo of pasting the ScrapeGraphAI GitHub repo into Claude Code and saying "install this" to set up free AI-driven lead scraping.
- Claude then runs plain-language scrape commands (e.g. "find plumbing business owners") that fill a spreadsheet with company, owner, email.
- Cost claim on screen: 998 companies scraped for $0.00 vs $3.99 (~$0.004/company) on Apify — true only when using a local Ollama model instead of a paid LLM API.
- Workflow is saved and scheduled to run daily at 7:00 AM, so leads accumulate on autopilot.

## Key moments
- 0:00–0:05 — Hook: Claude can scrape thousands of leads for free; names the tool, ScrapeGraphAI, ~29k GitHub stars.
- 0:05–0:16 — Explains it can search the web or crawl directories, pulls public contact details, writes to a clean sheet, runs locally, can use local models to avoid per-scrape API cost.
- 0:16–0:22 — Repo card on screen: ScrapeGraphAI/Scrapegraph-ai, 28,505 stars, MIT license, 2,838 forks.
- 0:24–0:28 — Install shown: paste repo link into Claude Code, say "install this" → Claude clones repo + `pip install scrapegraphai`.
- 0:28–0:33 — Demo prompt: `claude "find plumbing business owners"`; sheet fills with rows live.
- 0:33–0:38 — Cost comparison card: ScrapeGraphAI $0.00 vs Apify $3.99 for 998 companies; workflow saved to run daily at 7:00 AM.
- 0:38–0:45 — CTA: comment "leads" for the repo link, full setup, and exact prompts.

## Hook microscope
Opens on a direct capability claim ("Claude can now scrape thousands of leads for free") layered over a spreadsheet already full of rows — pattern is demo-first/proof-first rather than a question or contrarian hook. The visual (a populated sheet) does the persuasion work before the tool name is even given, which is why the repo-card reveal a few seconds later lands as confirmation rather than introduction.

## Editorial profile
Fast-cut screen-recording + talking-head hybrid, on-screen captions synced to every sentence, numeric proof points (star count, row count, cost) shown as static cards rather than spoken — typical high-density tool-demo format optimized for muted autoplay viewing.

## Quotable moments
- "Claude can now scrape thousands of leads for your business for free."
- "You can even use local models so you're not paying [per company] that it scrapes."
- "Watch — I just tell it to find me specific business owners and the sheet starts filling up on autopilot."

## Entities mentioned
- [[claude-code]]
- [[scrapegraphai]]
- [[apify]]
- [[ollama]]

## Concepts surfaced
- **AI-native scraping** — natural-language extraction prompts replacing hand-written CSS/XPath selectors.
- **Local-model cost avoidance** — routing LLM inference through Ollama locally to eliminate per-page API cost.
- **Agentic install-and-run pattern** — handing an agent a repo URL and a plain-language goal instead of manually configuring a scraping pipeline.

## Full research
See `Research docs/leads find.md` in this vault for the full write-up: tool identity confirmation, how ScrapeGraphAI works, cost-claim breakdown, 2026 scraper-tool comparison table, and scraping/outreach legal notes.

## Transcript
Auto-transcribed locally via whisper.cpp (base.en). Opens: "Claude can now scrape thousands of leads for your business for free. The tool is called Scrape Graph API..." — full transcript stored at `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch4/transcript.txt`; substance is fully captured in Key Moments and the linked Research doc above.
