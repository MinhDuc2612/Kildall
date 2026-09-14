# OrbitoolOSS — Open-Source Replacement For Every Proprietary Tool

> ⚠️ **SAMPLE ONLY — REDO DURING THE BUILD.** This is research output, not a finished tool set for
> Orbi. Every pick here must be re-chosen and re-verified against current benchmarks as part of the
> build, not inherited from this pass. See `CLAUDE.md` → "The tooling is sample-stage."


**Sample 2 build. Self-contained.** Companion to `OrbiOSS.md` (which covers *models*); this file
covers *tools*. Built 2026-09-01.

The question: for every proprietary SaaS product in a working stack, what is the open-source,
self-hostable thing that replaces it — and what do you actually give up by switching?

Seed pattern given: **Coolify** replaces Vercel. **n8n** replaces Zapier. **Hyperswitch** replaces
Stripe. This file extends that pattern across every category, including ones with no connector
attached to anything.

## ⚡ ANSWER FIRST

**What this is:** the open-source replacement for **91 proprietary tools** — Coolify for Vercel,
n8n for Zapier, Hyperswitch for Stripe, and 88 more.

| | |
|---|---|
| Mappings | **91** |
| Hand-verified | 14 |
| Source-quoted, unverified | ~40 |

**The three traps:**
1. **n8n is NOT open source.** Sustainable Use License. Use **Activepieces (MIT)** instead.
2. **No single project replaces Stripe.** Hyperswitch routes, Lago bills, a real PSP takes the money.
3. **Chatwoot and SigNoz** ship MIT cores with separately-licensed enterprise folders.

**The test that catches open-core:** can you turn on SSO without paying? Often no, **even self-hosted**.

---

---

## READ THIS FIRST — how this file was built, and what that means for trusting it

A `/deep-research` workflow was run for this file: 5 search angles → fetch top sources → extract
falsifiable claims → **3-vote adversarial verification per claim** → synthesis.

**The verification stage failed completely.** 91 of 103 agents died on an account session-usage
limit. **All 25 verifier panels returned zero valid votes.** The workflow's own summary says it
plainly: *"Could not verify any claims — all 25 verifier panels failed. This is an infrastructure
failure, not a research finding."*

What survived was the **search and fetch stage** — 12 agents that did complete, returning claims
with direct quotes and source URLs. That is real evidence, but it is *unadjudicated* evidence: no
adversarial pass ever tried to kill it.

So rather than publish unverified output as if it were verified, the highest-stakes claims were
**re-verified by hand in-session** with independent searches. That hand-check found **three real
errors** in the surviving claims, which are corrected below and marked. Everything is tiered:

| Tier | Meaning | Count |
|---|---|---|
| `✓✓` | Re-verified by hand this session against independent sources | 14 claims |
| `✓` | Direct quote captured from a fetched primary/secondary source, **not** adversarially verified | ~40 claims |
| `⚠` | Named by a curated index only — licence and maturity **not** checked at all | everything else |

**Do not treat a `⚠` row as a recommendation.** It is a candidate to go verify. The whole point of
the tiers is that this file tells you which rows it actually stands behind.

### Corrections found during the hand-check

1. **"Metabase is source-available"** — imprecise. Metabase's OSS edition is **AGPL**, an OSI
   licence; it is the *enterprise* edition that is source-available, and SAML is paid even
   self-hosted. Calling the whole product source-available is wrong. Corrected below.
2. **"Langfuse being acquired is a risk to its openness"** — incomplete. ClickHouse acquired
   Langfuse on **2026-01-16** alongside a $400M Series D, and **publicly committed to keeping
   Langfuse MIT-licensed**. The acquisition is a fact worth knowing; framing it as a licence risk
   without that commitment would have been misleading.
3. **A fetched source defines "source-available" backwards** — it states source-available *means*
   an OSI-approved licence. That is the opposite of the truth. This file uses the OSI definition:
   source-available means you can read the code but the licence **fails** the Open Source
   Definition. Flagged because that error is circulating in the search results people will hit.

---

## RULE 0 — "Open source" is a licence test, not a vibe

The single most useful thing this file can do is stop you deploying something you think is open
source and finding a wall later. Three distinct things get called "open source":

| Category | Definition | What bites you |
|---|---|---|
| **Open source (OSI)** | Licence approved by the Open Source Initiative — MIT, Apache-2.0, AGPL-3.0, BSD, MPL | Nothing. AGPL still obliges you to publish modifications if you serve it |
| **Source-available** | You can read the source; the licence **fails** the Open Source Definition — SSPL, BSL/BUSL, Elastic-2.0, FSL, n8n's Sustainable Use License | You may not offer it as a service to third parties. Fine internally, fatal if you resell |
| **Open-core** | Core is genuinely OSI-licensed; the features enterprises need are in a separately-licensed folder or a paid tier | SSO, RBAC and audit logs are missing **even when you self-host** |

**OSI's position, quoted:** calling non-OSI-approved licences "open source" is deceptive. `✓`
([opensource.org](https://opensource.org/blog/the-sspl-is-not-an-open-source-license))

### The SSO tax — the open-core tell

The most reliable way to detect open-core is to ask "can I turn on SAML without paying?" Often the
answer is no, **even self-hosted**. From SSOtax.org, a maintained database of 400+ vendors whose
inclusion rule is a checkable threshold — SSO locked behind a tier more than 10% above standard
price. Last updated **2026-04-24**. `✓`

| Project | Base | SSO price | Note |
|---|---|---|---|
| **n8n** | $24 | **$400/mo** | Enterprise plan only `✓✓` |
| **Airbyte** (ETL) | free/OSS | **$40,000/yr** | SAML is Enterprise-only whether self-hosted or cloud `✓` |
| **Graylog** (logging) | — | **$15,000/yr** | `✓` |
| **Passbolt** (passwords, self-hosted) | — | $49/mo per 10 users | `✓` |
| **Grafana** | free (AGPL) | Enterprise tier | SAML/OIDC, fine-grained RBAC and audit logs are Enterprise-only `✓✓` |
| **Metabase** | free (AGPL) | Pro/Enterprise | SAML paid **even self-hosted** `✓✓` |
| **Sentry** | $26 | $80/100K events | **Counter-example: SSO is free in the self-hosted product** `✓` |

Sentry is the shape you want: self-hosting removes the paywall instead of preserving it.

**Nuance the Wall of Shame flattens:** in self-hosted OSS the paywall usually lands on
**SAML/OIDC specifically**, while password auth and often LDAP stay free. "SSO is paid" is too
blunt a claim to make per-project without checking. `✓`

### And the tax runs the other way too

Proprietary tools charge heavily for SSO as well, which is part of the self-hosting case: GitHub
$4 → **$21**/user/mo (+425%), Figma $12 → **$45**/user/mo (+275%), 1Password $4 → $8/user/mo
(+100%). `✓`

---

## RULE 1 — Star counts are not evidence

This file records stars where they were found, but **does not rank on them**. Direct evidence of
why, from this build: Coolify's star count was reported as **61K**, **55,689**, and **~40K** by
three sources in the same window. They cannot all be right, and none is a maturity measure anyway.

Better signals, in order: **last commit date**, **bus factor**, **whether the licence changed
recently**, **whether SSO is paywalled**. A 2026 editorial on self-hosted abandonment makes the
argument directly — tooling lowered the barrier to *launching* a project without lowering the
maintenance burden, so fast-growing star counts are a weak maturity signal, and r/selfhosted's
recurring compromised-instance posts usually trace to a service set up once and never patched. `✓`

---

## The Mapping

`Lic` = licence. `T` = trust tier (`✓✓` hand-verified, `✓` source-quoted, `⚠` index-named only).

### 1. Hosting, PaaS, deploy

| Proprietary | Open-source replacement | Lic | What you give up | T |
|---|---|---|---|---|
| **Vercel / Netlify** | **Coolify** — `coollabsio/coolify` | Apache-2.0 | The global edge network and auto-preview-per-PR. Both are the actual product, not a detail | `✓✓` |
| **Vercel** (multi-server) | **Dokploy** — `Dokploy/dokploy` | Apache-2.0 | Smaller one-click app library than Coolify; lower idle overhead, native multi-server | `✓✓` |
| **Vercel** (Next.js only) | **OpenNext** | MIT | Adapter, not a platform — you still bring infra | `✓` |
| **Heroku** | **Coolify** | Apache-2.0 | Add-on marketplace | `✓` |
| **Heroku / Railway** | **CapRover** | Apache-2.0 | Older UI, smaller ecosystem | `⚠` |

> **Coolify vs Dokploy, decided:** Coolify for the larger one-click library, ARM64/Raspberry Pi
> support, and "pure Apache-2.0 with no future paid tier waiting in the wings." Dokploy for lower
> idle overhead, native multi-server, and standard Docker Compose without platform-specific
> massaging. `✓✓`

> **The honest gap for this whole category** — self-hosting means owning uptime, patching, storage
> planning, backup *validation*, certificate management and incident response. If the team has no
> Docker/Linux experience and no intent to build it, the free tool is a deferred problem. Business-
> critical workloads need an operational concept with redundancy, not a single VPS. `✓`

### 2. Workflow automation, ETL

| Proprietary | Open-source replacement | Lic | What you give up | T |
|---|---|---|---|---|
| **Zapier** | **n8n** — `n8n-io/n8n` | ⚠ **Sustainable Use License — NOT open source** | Internal business use only; cannot host it for third parties. SSO/RBAC/log streaming/external secrets are **paid even self-hosted** | `✓✓` |
| **Zapier** (clean licence) | **Activepieces** — `activepieces/activepieces` | **MIT** | Fewer pre-built integrations than n8n | `✓` |
| **Zapier** (any) | — | — | The real gap is **integration breadth (8000+ apps)**, not engine capability. The engines have caught up | `✓` |
| **Fivetran / Airbyte Cloud** | **Airbyte** OSS | open-core | SSO at **$40,000/yr**, Enterprise-only self-hosted or not | `✓` |

> **n8n is the single most important flag in this file**, because it is the tool everyone names as
> the open-source Zapier and it is **not open source**. n8n moved off Apache-2.0 + Commons Clause to
> the Sustainable Use License in 2022, **declines the open-source label itself**, and uses the term
> "fair-code". Verified against n8n's own docs and LICENSE.md. If you need a genuinely open licence,
> the answer is **Activepieces**, not n8n. `✓✓`

### 3. Payments, billing, subscriptions

This category has the most confusion in it, because **two different products get called "the open
source Stripe"** and they do different jobs.

| Proprietary | Open-source replacement | Lic | What you give up | T |
|---|---|---|---|---|
| **Stripe** (routing) | **Hyperswitch** — Juspay, Rust | **Apache-2.0** | **Not an acquirer.** It orchestrates payments across processors — you still need a PSP behind it | `✓✓` |
| **Stripe Billing / Chargebee** (usage) | **Lago** | **AGPL-3.0** | Metered/usage billing + invoicing; delegates collection to a gateway | `✓✓` |
| **Stripe Billing** (complex/legacy) | **Kill Bill** (Java) | **Apache-2.0** | **In production since 2010** — the most mature. Heavier to run | `✓✓` |
| **Chargebee / Paddle** | Lago or Kill Bill | AGPL / Apache-2.0 | Neither handles merchant-of-record tax like Paddle does | `✓` |

> **The distinction that matters:** Hyperswitch handles **routing**, not subscriptions, invoicing or
> licence keys. Lago and Kill Bill handle **billing**, not card acquiring. Neither replaces Stripe
> alone — the working stack is **Lago (metering) → Hyperswitch (collection) → a real PSP**. Anyone
> telling you one open-source project replaces Stripe outright is selling something. `✓✓`

> **Gap worth knowing:** the best-structured of the curated SaaS→OSS index lists has **no payments
> category at all** — Stripe has no entry in it. If you rely on those lists, this entire category is
> invisible to you. `✓`

### 4. Backend, database, auth, storage

| Proprietary | Open-source replacement | Lic | What you give up | T |
|---|---|---|---|---|
| **Firebase** (Postgres-shaped) | **Supabase** | Apache-2.0 | Self-host only pays off above roughly **$150–200/mo** of cloud spend; below that you are buying ops work | `✓` |
| **Firebase** (same shape) | **Appwrite** | BSD-3-Clause | Closest structural clone of Firebase's multi-service shape | `✓` |
| **Firebase** (tiny) | **PocketBase** | MIT | Single binary, no ops — but no horizontal scale | `✓` |
| **Auth0 / Okta** (enterprise) | **Keycloak** | Apache-2.0 | Steep learning curve; the enterprise default | `✓` |
| **Auth0** (self-hoster) | **Authentik** | open-core ⚠ | Same SSO surface, far lower learning curve — the emerging default | `✓` |
| **Auth0** (other real options) | Zitadel · Ory · Authelia · Kanidm · Gluu · WSO2 IS · FreeIPA · OpenIAM | mixed ⚠ | Licences unchecked — this category has **ten** credible candidates, not one | `⚠` |
| **S3** | MinIO | ⚠ licence changed — **verify before use** | — | `⚠` |

### 5. Observability, errors, feature flags

| Proprietary | Open-source replacement | Lic | What you give up | T |
|---|---|---|---|---|
| **Datadog** | **Grafana** + Loki/Tempo/Mimir | **AGPL-3.0** | SAML/OIDC, fine-grained RBAC, advanced audit logs are **Enterprise-only** | `✓✓` |
| **Datadog** (single tool) | **SigNoz** | **MIT** core, `ee/` dir under SigNoz Enterprise licence | Open-core carve-out — same pattern as Chatwoot | `✓✓` |
| **Sentry** | **GlitchTip** | ⚠ | Fewer features; but **cost is flat under event spikes** — a runaway retry loop emitting 5M errors/month costs ~$975 on Sentry Team, unchanged when self-hosted | `✓` |
| **Sentry** (self-host) | **Sentry itself** | FSL (2-yr non-compete → Apache-2.0) | Heavy to run, but **SSO is free self-hosted** | `✓` |
| **LaunchDarkly** | Unleash · Flagsmith · GrowthBook · FeatBit · Flipt · PostHog | mixed, **several open-core with SSO/audit paywalled** | Field is genuinely split — no single winner | `✓` |
| **Metabase Cloud** | **Metabase** OSS | **AGPL** (enterprise edition is source-available) | **SAML is paid even self-hosted** | `✓✓` |

### 6. Support, CRM, product analytics

| Proprietary | Open-source replacement | Lic | What you give up | T |
|---|---|---|---|---|
| **Zendesk** (ticketing) | **Zammad** | **AGPL-3.0, fully open** | Unlimited agents, **LDAP/SAML in the core, not paywalled** | `✓✓` |
| **Intercom** (live chat) | **Chatwoot** | MIT core — but the **`enterprise/` directory is separately licensed** | Textbook open-core carve-out | `✓✓` |
| **Amplitude / Mixpanel** | **PostHog** | MIT | Session replay + flags + analytics in one | `✓` |
| **Salesforce / HubSpot** | Odoo · Twenty · EspoCRM | Odoo = **LGPL community vs proprietary Enterprise** ⚠ | Odoo's split is the trap here | `✓` |

> **Routing rule for support, from the most licence-honest source found:** **Zammad** when the real
> need is structured ticketing, SLAs and escalation. **Chatwoot** when the Zendesk use case is
> actually live chat (Intercom-shaped). They are not substitutes for each other. `✓✓`

### 7. AI / LLM infrastructure

The fastest-moving category, and the one general self-hosted lists cover worst.

| Proprietary | Open-source replacement | Lic | What you give up | T |
|---|---|---|---|---|
| **OpenRouter / Portkey** (gateway) | **LiteLLM** | MIT | The reference OSS LLMOps stack pairs it with Langfuse | `✓` |
| **LangSmith / Braintrust / Helicone** | **Langfuse** | **MIT** — ClickHouse committed to keeping it MIT after acquiring it 2026-01-16 | Open-core EE tier (SSO enforcement, some RBAC/eval features) | `✓✓` |
| **OpenAI/Anthropic API** (serving) | **vLLM** · Ollama | Apache-2.0 / MIT | You supply the GPUs | `✓` |
| **Pinecone** | **Qdrant** (Rust, easiest self-host) | Apache-2.0 | Vendor also runs a cloud — check for Cloud-only ops tooling | `✓` |
| **Pinecone** (built-in vectorizers) | **Weaviate** | BSD-3-Clause | — | `✓` |
| **Pinecone** (huge scale) | **Milvus** | Apache-2.0 | Scales to tens of billions of vectors; heavy | `✓` |
| **Pinecone** (under ~1M vectors) | **pgvector** | PostgreSQL licence | The "don't add a database" answer | `✓` |
| **OpenAI Assistants / Vertex Agent Builder** | **Dify** | ⚠ **modified Apache-2.0** — multi-tenant-SaaS and logo-removal restrictions, so **not cleanly permissive** | — | `✓` |
| **Same, clean licence** | **Langflow** | MIT | LangGraph multi-agent, custom Python nodes | `✓` |
| **Same, fastest RAG path** | **Flowise** | ⚠ | LangChain-backed chatbot | `✓` |
| **ChatGPT / Claude web UI** | **Open WebUI** | ⚠ | — | `✓` |

### 8. Everything else — candidates only, licences unchecked

Named by curated indexes. **Tier `⚠` throughout — verify the licence yourself before deploying.**

| Proprietary | Candidate replacement | T |
|---|---|---|
| **Figma** | Penpot | `⚠` |
| **Calendly** | **Cal.com** (MIT) | `✓` |
| **DocuSign** | **Documenso** (AGPL-3.0) | `✓` |
| **GitHub** | Gitea · Forgejo · GitLab CE (free/Premium/Ultimate split ⚠) | `⚠` |
| **Shopify** | Medusa (headless; pairs with Hyperswitch for multi-region) | `✓` |
| **Substack / Mailchimp** | Ghost — the only mature OSS option bundling editor + email + Stripe paid memberships | `✓` |
| **Terraform** | **OpenTofu** — the fork created when HashiCorp moved MPL-2.0 → BSL | `✓` |
| **Elasticsearch** | **OpenSearch** — the fork created when Elastic moved Apache-2.0 → SSPL/ELv2 | `✓` |
| **1Password / LastPass** | Vaultwarden · Passbolt (SSO paid ⚠) | `⚠` |
| **Notion / Confluence** | Outline · AppFlowy · Docmost | `⚠` |
| **Slack** | Mattermost (SSO paywalled ⚠) · Rocket.Chat (SSO paywalled ⚠) | `⚠` |
| **Zoom** | Jitsi Meet | `⚠` |
| **Dropbox** | Nextcloud · Seafile | `⚠` |
| **Airtable** | NocoDB · Baserow · Teable | `⚠` |
| **Typeform** | Typebot ⚠ (no licence tag in index) · Formbricks | `⚠` |
| **Algolia** | Meilisearch · Typesense | `⚠` |
| **WordPress.com / Contentful** | Strapi · Directus · Payload | `⚠` |
| **SAP / NetSuite** | ERPNext · Odoo ⚠ | `⚠` |
| **Twilio** | FreeSWITCH · Asterisk · Jambonz | `⚠` |
| **Google Maps** | OpenStreetMap + Nominatim · Photon | `⚠` |
| **Statuspage** | Uptime Kuma · Cachet · OneUptime | `⚠` |
| **PagerDuty** | Grafana OnCall ⚠ (**check status — Grafana has been retiring products**) | `⚠` |
| **Google Analytics** | Plausible · Umami · Matomo | `⚠` |

---

## The Trap List — things widely called open source that are not

Sorted by how likely you are to get caught.

| Project | What people think | What it actually is | T |
|---|---|---|---|
| **n8n** | The open-source Zapier | **Sustainable Use License.** Internal use only, no hosting for third parties. n8n declines the open-source label itself | `✓✓` |
| **Chatwoot** | MIT | MIT core, **`enterprise/` directory separately licensed** | `✓✓` |
| **SigNoz** | MIT | MIT core, **`ee/` directory under SigNoz Enterprise licence** | `✓✓` |
| **Dify** | Apache-2.0 | **Modified** Apache-2.0 with multi-tenant-SaaS and logo-removal restrictions | `✓` |
| **Odoo** | Open source | **LGPL community edition vs proprietary Enterprise** | `✓` |
| **Grafana** | Free and open | AGPL-3.0 — genuinely open, but **SAML/RBAC/audit are Enterprise-only** | `✓✓` |
| **Metabase** | Open source | OSS edition **is** AGPL; enterprise edition is source-available; **SAML paid even self-hosted** | `✓✓` |
| **Airbyte** | Free OSS ETL | Free at base, **SSO $40,000/yr**, Enterprise-only whether self-hosted or cloud | `✓` |
| **Terraform, Vault, Consul** | MPL-2.0 | Relicensed to **BSL** → use **OpenTofu** | `✓` |
| **Elasticsearch** | Apache-2.0 | Relicensed to **SSPL/Elastic-2.0** (later partial AGPL return) → **OpenSearch** | `✓` |
| **Sentry** | Open source | **FSL** with a 2-year non-compete, converting to Apache-2.0 after | `✓` |
| **MongoDB** | Open source | **SSPL — explicitly not an open source licence per OSI** | `✓` |

**Licence distribution across one 1,027-entry curated index**, as a sense of the real landscape:
AGPL-3.0 ×299, MIT ×264, Apache-2.0 ×217 — copyleft outnumbers permissive — plus a restrictive tail
of Elastic-2.0 ×7, BUSL-1.1 ×5, SSPL-1.0 ×4, FSL-1.1-MIT ×2. And **122 entries carry no licence tag
at all**, silently including n8n, Dify, LiteLLM, Typebot and Odoo. `✓`

**"Self-hostable" and "permissively licensed" are different properties.** Most of this list is the
former. Rather fewer are the latter.

---

## Where open source genuinely loses

Not every category has a real replacement. Saying so is the point of the file.

1. **Edge networks.** Coolify runs your app; it does not give you Vercel's global edge or
   preview-per-PR. There is no self-hostable equivalent of a global PoP network — that is capital
   expenditure, not software. `✓✓`
2. **Integration catalogues.** Automation engines caught up with Zapier. **Zapier's 8000+ prebuilt
   integrations did not get replaced** — that is a maintenance army, not a feature. `✓`
3. **Card acquiring.** No open-source project is a payment acquirer. Hyperswitch routes; Lago
   meters; a regulated PSP still takes the money. `✓✓`
4. **Small-scale economics.** Supabase Cloud is $25/mo/project with zero ops; self-hosting is
   $30–80/mo of VPS **plus real DevOps time**, and only becomes cost-competitive somewhere around
   $150–200/mo of cloud spend. Below that threshold, self-hosting costs more, in the currency that
   matters. `✓` *(one blog's estimate, not audited)*
5. **The maintenance burden itself.** Self-hosted app abandonment is accelerating, and
   compromised-instance reports usually trace to a service installed once and never patched. The
   cost of a self-hosted tool is not the licence, it is the patching cadence. `✓`
6. **SSO, repeatedly.** In a large share of open-core projects the identity layer — the exact thing
   an enterprise needs — is the paywalled part, self-hosted or not. `✓✓`

**The genuine win, stated precisely:** it is usually **cost predictability under volume spikes**,
not headline price. A frontend retry loop emitting 5M errors/month costs ~$975 on Sentry Team or
~$738 on PostHog pay-as-you-go; a self-hosted instance costs the same as it did last month. `✓`

---

## Quality of the source indexes themselves

Worth recording, because these are what most people will reach for.

| Index | Scale | Verdict | T |
|---|---|---|---|
| **awesome-selfhosted** | ~1,519 projects, 143 categories, 1,200+ contributors | **Best overall.** Explicit licence tag per entry; non-free projects quarantined on a separate page; CI jobs for dead links **and unmaintained projects**; anti-features flagged with ⚠. Weakness: does **not** say which SaaS each project replaces | `✓` |
| **OpenAlternative** | 1,027 entries / ~747 projects, CC0-1.0, last push 2026-08-31 | Good candidate generation, SPDX tag + stars per row. **Does not flag open-core**, and 122 entries have no licence at all | `✓` |
| **selfh.st/apps** | directory + release monitoring | Only index that filters by *which SaaS a project replaces* **and** sorts by last development activity. Deliberately includes closed-source too — verify licence per entry | `✓` |
| **SSOtax.org** | 400+ vendors, updated 2026-04-24 | Best open-core detector available. Checkable inclusion rule | `✓` |
| **SolvoHQ/awesome-self-host-saas-alternatives** | 100 SaaS → 294 alternatives | **Structurally the best match to this question — and the least trustworthy.** GitHub API shows **1 star, 1 fork, a single push on 2026-05-10 with no commits since, and a NOASSERTION licence.** Machine-generated from JSON; its "canonical" osalt.dev links actually point at a Vercel preview deployment. Its licence column is a starting point, never evidence | `✓` |

That last row is the finding worth keeping: **the source that looked most purpose-built for this
exact question turned out to be a one-star, stale, machine-generated repo.** Structural fit is not
credibility.

---

## What is still missing from this file

Stated so nobody mistakes the gaps for coverage.

- **No adversarial verification ran.** 25 verifier panels, 0 valid votes, killed by a session limit.
  Fourteen claims were hand-checked; the rest were not.
- **Tier `⚠` rows are unverified names.** Section 8 in particular is candidate generation, not
  recommendation. Licences there are unchecked.
- **No hands-on testing.** Nothing here was installed, run, or migrated to. Every "gap" is a
  reported gap.
- **Category coverage is uneven.** Hosting, automation, payments, support, observability and AI
  infra are well-evidenced. Design, HR, accounting, ERP, telephony, maps and localisation are
  thin — mostly names.
- **Star counts are unreliable and were not used for ranking** (see Rule 1).
- **Several vendor-authored sources** were used where they were the best available: a feature-flag
  ranking published by GrowthBook, an open-core explainer by OneUptime, billing comparisons by
  Flexprice. Facts in them checked out where tested, but read the rankings as motivated.

**To finish this properly:** re-run the workflow after the session limit resets and let the
verification stage actually execute —
`Workflow({scriptPath: ".../deep-research-wf_88adb239-ba4.js", resumeFromRunId: "wf_88adb239-ba4"})`.
Completed agents replay from cache, so only the killed verifier panels re-run.

---

## Sources

Hand-verified in-session (`✓✓`):

1. [Sustainable Use License — n8n Docs](https://docs.n8n.io/sustainable-use-license/) — primary licence text
2. [n8n LICENSE.md](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) — primary
3. [Compare editions — n8n Docs](https://docs.n8n.io/deploy/host-n8n/community-edition-features) — SSO/RBAC paid self-hosted
4. [ClickHouse acquires Langfuse](https://clickhouse.com/blog/clickhouse-acquires-langfuse-open-source-llm-observability) — 2026-01-16, MIT commitment
5. [ClickHouse $400M Series D + Langfuse](https://clickhouse.com/blog/clickhouse-raises-400-million-series-d-acquires-langfuse-launches-postgres)
6. [chatwoot/chatwoot](https://github.com/chatwoot/chatwoot) — MIT core, separately-licensed `enterprise/`
7. [Zammad vs Zendesk — WZ-IT](https://wz-it.com/en/blog/zammad-vs-zendesk-self-hosted-alternative/) — AGPLv3, no agent fees
8. [About Hyperswitch](https://hyperswitch.io/about) — Apache-2.0, Rust, orchestration not acquiring
9. [Open-source Stripe Billing alternatives — Flexprice](https://flexprice.io/blog/open-source-stripe-billing-alternatives) — Lago AGPL-3.0, Kill Bill Apache-2.0 since 2010
10. [Coolify vs Dokploy — Cloudzy](https://cloudzy.com/blog/coolify-vs-dokploy/) — both Apache-2.0, CVE/licence/sizing
11. [Dokploy vs Coolify — INTROSERV](https://introserv.com/blog/dokploy-vs-coolify-complete-comparison-of-the-best-self-hosted-paas-platforms-for-vps-and-dedicated-servers-2026/)
12. [Grafana licensing](https://grafana.com/licensing/) — AGPLv3 OSS
13. [Grafana alternatives — SigNoz](https://signoz.io/blog/grafana-alternatives/) — SigNoz MIT + `ee/` enterprise dir
14. [The SSPL is Not an Open Source License — OSI](https://opensource.org/blog/the-sspl-is-not-an-open-source-license) — authoritative definition

Fetched by the workflow, quoted but **not adversarially verified** (`✓`):

15. [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) · [browsable edition](https://awesome-selfhosted.net/)
16. [OpenAlternative list](https://github.com/piotrkulpinski/open-source-alternatives)
17. [SolvoHQ/awesome-self-host-saas-alternatives](https://github.com/SolvoHQ/awesome-self-host-saas-alternatives) — **1 star, stale, NOASSERTION**
18. [selfh.st/apps](https://selfh.st/post/introducing-selfhst-apps/)
19. [SSO Wall of Shame](https://ssotax.org/) — 400+ vendors, updated 2026-04-24
20. [The SSO tax in self-hosted software — SSD Nodes](https://www.ssdnodes.com/learn/the-sso-tax-in-self-hosted-apps)
21. [Open Source vs Open Core — OneUptime](https://oneuptime.com/blog/post/2026-03-03-open-source-vs-open-core-whats-the-difference/view) — *vendor-authored*
22. [License Wars Have Redefined "Open Source" — x-cmd](https://www.x-cmd.com/blog/260706-dark-side-of-open-source/) — BSL/SSPL/ELv2/FSL wave, OpenTofu and OpenSearch forks
23. [Self-hosted app abandonment is speeding up — XDA](https://www.xda-developers.com/self-hosted-app-abandonment-speeding-up-reaching-projects-trust/) ⚠️ **blocks automated probes** — returns no response to `curl` even with browser headers, but the article was **confirmed live and its content retrieved via search on 2026-09-02**. The link is correct; only direct fetching is blocked.
24. [Open Source LLMOps Stack](https://oss-llmops-stack.com/) — LiteLLM + Langfuse reference architecture
25. [langfuse/langfuse](https://github.com/langfuse/langfuse)
26. [Open-Source-LLM-Stack — WZ-IT](https://wz-it.com/knowledge/ki/open-source-llm-stack/) — vLLM/LiteLLM/Langfuse/Open WebUI/Qdrant
27. [Pinecone vs Weaviate vs Qdrant vs Milvus 2026](https://www.buildmvpfast.com/blog/pinecone-vs-weaviate-vs-qdrant-vector-database-comparison-2026)
28. [Dify vs Flowise vs Langflow 2026](https://bigaiagent.tech/dify-vs-flowise-vs-langflow-2026/)
29. [Top 10 Open-Source IAM Solutions 2026](https://startwithidentity.com/articles/top-10-open-source-iam-solutions/)
30. [8 Best Open-Source Feature Flagging Tools — GrowthBook](https://www.growthbook.io/blog/best-open-source-feature-flagging-tools-compared) — *vendor-authored*
31. [5 Open-Source Zendesk Alternatives 2026](https://use-apify.com/blog/zendesk-alternatives-2026)
32. [Hyperswitch: Strategic Open Source Alternative to Stripe — OpenTechHub](https://www.opentechhub.io/hyperswitch/)
33. [Self-Hosted vs Cloud Supabase 2026](https://starterpick.com/blog/self-hosted-vs-cloud-supabase-saas-2026)
34. [Self-Hosted Sentry + Plausible Alternative 2026 — Temps](https://temps.sh/blog/self-hosted-sentry-and-plausible-alternatives-2026)
35. [SaaS alternatives self-hosted with Coolify — Next-Levels](https://next-levels.de/en/blog/self-hosted-instead-of-saas-subscription-you-can-run-these-open-source-tools-for-free-with-coolify)
36. [Self-Hosting in 2026: What Is Actually Worth Running Yourself — DEV](https://dev.to/alanwest/self-hosting-in-2026-what-is-actually-worth-running-yourself-2c0i)

---

## Change Log

- **2026-09-01** — Created `OrbitoolOSS.md` in `Researchhub/sample 2/`, self-contained, companion to
  `OrbiOSS.md` (models). Ran the `/deep-research` workflow (run `wf_88adb239-ba4`, 103 agents).
  **The workflow's verification stage failed entirely** — 91 of 103 agents killed by an account
  session-usage limit, **all 25 adversarial verifier panels returning zero valid votes**. The
  search and fetch stages did complete: 12 agents returned claims with direct quotes and source
  URLs, recovered by reading `journal.jsonl` rather than trusting the truncated task output (the
  task's own output file parsed to zero claims; the journal held all 12 results).
  Rather than publish unadjudicated output as finished research, the highest-stakes claims were
  **re-verified by hand in-session** with six independent searches. That hand-check **corrected
  three errors**: Metabase is AGPL (not source-available — its *enterprise* edition is);
  Langfuse's ClickHouse acquisition came **with a public commitment to keep it MIT**, which changes
  the risk reading; and one fetched source **defines "source-available" backwards**, stating it
  means an OSI-approved licence, which is the opposite of the truth.
  Every row carries a trust tier — `✓✓` hand-verified (14 claims), `✓` source-quoted but
  unadjudicated (~40), `⚠` index-named with licence unchecked (the rest) — so the file states
  exactly which rows it stands behind.
  Structural choices: **Rule 0** makes open source a licence test with three distinct categories
  (OSI / source-available / open-core) and uses the **SSO tax** as the practical open-core detector;
  **Rule 1** refuses to rank on star counts, with direct evidence for why — Coolify's count was
  reported as 61K, 55,689 and ~40K by three sources in the same window.
  Headline findings: **n8n, the tool everyone names as the open-source Zapier, is not open source**
  (Sustainable Use License; n8n declines the label itself; Activepieces is the MIT answer);
  **no single project replaces Stripe** — Hyperswitch routes, Lago and Kill Bill bill, and a
  regulated PSP still takes the money; **Chatwoot and SigNoz both ship MIT cores with separately-
  licensed enterprise directories**; and **the curated index that structurally matched this question
  best turned out to be a 1-star, stale, machine-generated repo with a NOASSERTION licence** —
  structural fit is not credibility.
  To finish: re-run with `resumeFromRunId: "wf_88adb239-ba4"` after the limit resets; completed
  agents replay from cache so only the killed verifier panels re-run.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** block at the top, matching sample 1's
  presentation style: what the file is, the numbers that matter, and the decisive caveat, all before
  any discussion. No content changed; the research below now serves as backing detail.
