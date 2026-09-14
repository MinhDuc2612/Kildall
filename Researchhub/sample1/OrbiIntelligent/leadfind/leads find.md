# Leads Find

Source: Instagram reel (https://www.instagram.com/reel/DbvWERsuDuA/). Audio transcribed locally via whisper.cpp (no captions on Instagram's side — whisper misheard "Claude" as "Quad" throughout, corrected below); frames (screen recording) confirmed and expanded on the audio. Researched further via web search. Compiled 2026-08-19.

---

## 1. What the video shows

A demo of using Claude (Claude Code, per the on-screen terminal) to scrape business leads for free using an open-source scraping library. The workflow shown:
1. Paste the tool's GitHub link into Claude Code and say "install this" — Claude clones the repo and runs `pip install scrapegraphai` itself.
2. Tell Claude in plain language what to find, e.g. `claude "find plumbing business owners"`.
3. Claude scrapes public directories/search results and fills a spreadsheet with company name, owner, and email — one demo screen shows a sheet hitting 2,299 rows, another 2,418.
4. Save it as a recurring workflow (shown scheduled for 7:00 AM daily) so fresh leads land in the sheet automatically.
5. Cost comparison shown on-screen: scraping 998 companies costs $0.00 with this tool vs. $3.99 (~$0.004/company) with Apify.

## 2. What the tool actually is

**ScrapeGraphAI** (github.com/ScrapeGraphAI/Scrapegraph-ai) — confirmed directly from the frame showing the repo card: 28,505 stars (video says "almost 29,000" — accurate), MIT license, 2,838 forks, tagged "Python scraper based on AI."

It's an open-source Python library that uses an LLM plus graph-based pipeline logic to build web-scraping workflows — instead of writing CSS selectors or XPath, you describe what you want extracted in plain language and it handles the extraction. Install: `pip install scrapegraphai`. Core pipeline types include `SmartScraperGraph` (single page), `SearchGraph` (top-N search results), `SmartScraperMultiGraph` (many pages from one prompt), and `SpeechGraph` (page → audio).

**Why the video's "$0.00" claim is true but conditional:** the library itself is free and open source — but it still needs an LLM to do the actual extraction reasoning. It supports OpenAI, Groq, Azure, Gemini, or **local models via Ollama**. The zero-cost path shown in the video only holds if you point it at a local Ollama model (free, runs on your own hardware) rather than a paid API — the video's narrator explicitly calls this out ("you can even use local models so you're not paying [per company scraped]"). If you use OpenAI/Groq/Gemini APIs instead, you're paying LLM token costs per page, just usually far less than a managed scraping service charges per row.

Beyond the open-source core library, ScrapeGraphAI also runs a separate managed cloud API/SDK (scrapegraphai.com) for people who don't want to self-host — that's a different, paid product from what's demoed in the reel.

## 3. Where ScrapeGraphAI sits versus other scraping/lead tools (2026 landscape)

| Tool | Model | Starting price | Best for |
|---|---|---|---|
| **ScrapeGraphAI** (open-source, self-hosted) | Free library + your own LLM cost (or $0 with local Ollama) | $0 self-hosted / $99/mo managed API | Structured field extraction via natural-language prompt |
| Apify | Compute-based + proxy passthrough | Free ($5 credit) / $49/mo | 6,000+ pre-built scrapers (LinkedIn, Google Maps, job boards) — breadth over do-it-yourself |
| Firecrawl | Credit-based | Free (1K credits) / $16–19/mo | LLM-ready markdown/JSON output, RAG pipelines |
| Crawl4AI | Open-source, self-hosted | Free | Cost-conscious engineers who manage their own infra (closest direct peer to ScrapeGraphAI) |
| SyncGTM / LocalProspects.ai / Prospeo | Managed, verified-contact focused | ~$29–39/mo+ | Skips raw scraping entirely — sells pre-verified emails/contacts instead |

The honest tradeoff versus Apify (the comparison the video makes directly): Apify wins on breadth — thousands of ready-made scrapers for specific sites (LinkedIn, Google Maps) that already handle anti-bot measures and site-specific quirks. ScrapeGraphAI wins on cost and flexibility — you're not paying per-row, and the natural-language extraction adapts to layout changes an Apify Actor written against fixed selectors might not. The real cost of the "free" path is engineering/setup time plus local compute if you go the Ollama route, and general risk that AI-scrapers are slower and can still misfire compared to hand-tuned traditional scrapers on well-known targets.

## 4. Practical/legal notes

- Scraping public directory/contact data is generally lower-risk than scraping login-gated platforms (e.g. LinkedIn profile scraping specifically carries higher ToS/legal exposure than public business directories).
- Bulk-collected owner emails used for cold outreach are still subject to applicable anti-spam law (e.g. CAN-SPAM in the US, GDPR/PECR in the EU/UK) regardless of how the list was built — "I found it publicly" doesn't exempt outbound email from consent/opt-out requirements in those jurisdictions.
- Respect target sites' `robots.txt` and rate limits; aggressive scraping frequency is the most common way this kind of workflow gets an IP blocked or triggers a ToS violation notice.

## 5. Sources

- ScrapeGraphAI (open-source repo) — https://github.com/ScrapeGraphAI/Scrapegraph-ai
- ScrapeGraphAI org page (SDKs, integrations) — https://github.com/scrapegraphai
- ScrapeGraphAI open-source docs — https://docs.scrapegraphai.com/contribute/opensource
- Repo profile/stats writeup — https://dev.co/ai/frameworks/scrapegraph-ai
- ScrapeGraphAI CLI (`just-scrape`) — https://github.com/ScrapeGraphAI/just-scrape
- "Best API for Web Crawling in AI Lead Gen (2026)" — https://syncgtm.com/blog/best-api-for-web-crawling-in-ai-lead-gen
- "5 Best Apify Alternatives for Reliable Web Scraping in 2026" — Firecrawl — https://www.firecrawl.dev/blog/apify-alternatives
- "10 Best AI Web Scrapers in 2026" — https://dataimpulse.com/blog/best-ai-web-scrapers/
- "Best Web Extraction Tools for AI in 2026" — Firecrawl — https://www.firecrawl.dev/blog/best-web-extraction-tools

## 6. Change log
- 2026-08-19 — Created. Sourced from Instagram reel (whisper.cpp transcript + frame confirmation) + deep research pass.
- 2026-08-20 — Link/claim verification sweep: star count reconfirmed consistent with current trackers (27.9k-29.8k range), framing as historical snapshot was already correct. No corrections needed.
