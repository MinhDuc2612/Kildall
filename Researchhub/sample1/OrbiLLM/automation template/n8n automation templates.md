# n8n Automation Templates (awesome-n8n-templates)

Research + local mirror of github.com/enescingoz/awesome-n8n-templates. Compiled 2026-08-22.

---

## 1. What was done

Cloned the full repository into `automation template/awesome-n8n-templates/` in this vault (346 ready-to-import n8n workflow JSON files, 420 files total including docs/READMEs). This is a straight `git clone` of a fully public repo, kept for local reference — not a redistribution to any third party.

## 2. What the repo is

**awesome-n8n-templates** (Enes Cingoz, github.com/enescingoz/awesome-n8n-templates, ~24.9k GitHub stars) bills itself as the largest open-source collection of n8n automation templates — 280+ (346 in the actual current clone) free, ready-to-use workflow files spanning AI agents, RAG/chatbots, email automation, social media, DevOps, and document processing.

**Licensing nuance worth knowing:** the repo root ships a `LICENSE` file under CC BY 4.0 (Enes Cingoz, 2024-2026) — but the repo's own README is explicit that **the individual templates themselves were "found online" and are not created or owned by the repository author**; rights to each original template belong to its original creator, and the author disclaims responsibility for issues arising from their use. Read as: the CC BY 4.0 license covers Cingoz's own curation/repo work, not a blanket claim over every aggregated template's underlying rights. Worth keeping in mind before redistributing any specific template further, even though pulling the collection for local/personal reference is unproblematic.

## 3. What's actually in the clone — by category (file counts)

| Category | Files |
|---|---|
| OpenAI_and_LLMs | 92 |
| Other_Integrations_and_Use_Cases | 45 |
| AI_Research_RAG_and_Data_Analysis | 44 |
| Telegram | 26 |
| Gmail_and_Email_Automation | 26 |
| Google_Drive_and_Google_Sheets | 20 |
| PDF_and_Document_Processing | 18 |
| Instagram_Twitter_Social_Media | 14 |
| Notion | 10 |
| Slack | 9 |
| WhatsApp | 7 |
| WordPress | 6 |
| devops | 5 |
| Database_and_Storage | 5 |
| Airtable | 5 |
| HR_and_Recruitment | 4 |
| Forms_and_Surveys | 4 |
| Discord | 4 |
| Other | 1 |

Every template is a plain `.json` file — n8n's native workflow export format, directly importable via n8n's UI (Workflows → Import from File) with no conversion step.

## 4. What n8n itself is (context, since this is a template library for it)

n8n (pronounced "n-eight-n," short for "nodemation") is a Berlin-founded (Jan Oberhauser, 2019) workflow-automation platform: a visual node-based canvas for wiring together apps/services/AI models, with the option to drop into custom JavaScript or Python wherever the visual nodes fall short. It's positioned as a more technical, self-hostable alternative to Zapier/Make — 1,500+ integrations, native AI Agent nodes (bundling a chat model, system prompt, memory, and tools into one reasoning node), MCP client/server support, and a free self-hosted Community edition alongside paid Cloud/Enterprise tiers. Licensed "fair-code" (Sustainable Use License — source-visible, self-hostable, but not resellable as a competing hosted service). As of mid-2026: 150,000+ GitHub stars, a $2.5B valuation post-Series-C, and a further SAP strategic investment (May 2026) that roughly doubled that to ~$5.2B, with n8n now embedded inside SAP's Joule Studio.

## 5. How to actually use one of these templates

1. Have an n8n instance running (self-hosted Community edition is free, or n8n Cloud).
2. Pick a `.json` file from `automation template/awesome-n8n-templates/<category>/`.
3. In n8n: Workflows → Import from File → select the JSON.
4. Add your own credentials for whichever services the workflow connects to (Gmail, Slack, OpenAI, etc. — credentials are never bundled in the template file itself).
5. Activate.

## 6. Sources

- Repo — https://github.com/enescingoz/awesome-n8n-templates
- Repo README (source-of-truth for the "templates found online, not owned by repo author" disclaimer) — https://github.com/enescingoz/awesome-n8n-templates/blob/main/README.md
- n8n official site — https://n8n.io/
- n8n — Wikipedia — https://en.wikipedia.org/wiki/N8n
- n8n 2026 guide — https://hatchworks.com/blog/ai-agents/n8n-guide/

## Change log
- 2026-08-22 — Created. Repo cloned into `automation template/awesome-n8n-templates/`, researched via GitHub API + web search.
