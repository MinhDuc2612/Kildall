# ScrapeGraphAI

An open-source (MIT-licensed) Python library (github.com/ScrapeGraphAI/Scrapegraph-ai; confirmed at 28,505 stars, 2,838 forks in the source video) that uses an LLM plus graph-based pipeline logic to build web-scraping workflows — instead of writing CSS selectors or XPath, you describe what you want extracted in plain language. Install via `pip install scrapegraphai`. Core pipeline types: `SmartScraperGraph` (single page), `SearchGraph` (top-N search results), `SmartScraperMultiGraph` (many pages from one prompt), `SpeechGraph` (page → audio). Supports OpenAI, Groq, Azure, Gemini, or local models via Ollama — the "$0.00 to scrape" claim shown in a demo video only holds when pointed at a local Ollama model rather than a paid API. Also runs a separate, paid managed cloud API/SDK (scrapegraphai.com) distinct from the open-source library.

## Mentioned in

- [[../../OrbiIntelligent/leadfind/leads find.md]]
