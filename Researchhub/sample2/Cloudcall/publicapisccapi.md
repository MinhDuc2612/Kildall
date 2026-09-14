# publicapisccapi — `public-apis/public-apis`

**Repo:** [github.com/public-apis/public-apis](https://github.com/public-apis/public-apis)
**Built:** 2026-09-01 · Sample 2 · self-contained
**Part of the `ccapi` set** — see `mnfstccapi.md`, `freellmapiccapi.md`, and the 18 per-provider files.

**One line:** the largest free-API directory on GitHub — **1,730 APIs across 51 categories**, one of
the most-starred repositories in existence — and **almost none of it is about LLMs**.

---

## 1. Verified repository facts

Live GitHub API, 2026-09-01:

| Field | Value |
|---|---|
| Repo | `public-apis/public-apis` |
| Description | *"A collective list of free APIs"* |
| Licence | **MIT** |
| Stars / forks | **473,984 / 52,334** |
| Created | **2016-03-20** — ten years old |
| Last push | 2026-08-31 |
| Archived | No |
| README size | **241,584 bytes** |

**By an order of magnitude the largest of the three repos** — 474K stars against `freellmapi`'s
23.4K and `mnfst`'s 7.3K, and 52K forks.

---

## 2. Measured contents

These were **counted directly from the README**, not taken from any description:

| Measure | Value |
|---|---|
| **API entries** | **1,730** |
| **Categories** | **51** |
| Table schema | `API · Description · Auth · HTTPS · CORS` |

### Authentication distribution

| Auth type | Count | Share |
|---|---|---|
| **No auth** | **806** | 47% |
| `apiKey` | 751 (+3 unformatted) | 44% |
| `OAuth` | 150 | 9% |
| `X-Mashape-Key` | 6 | <1% |
| `User-Agent` | 1 | <1% |

**Nearly half need no key at all.** That is the repo's real value — 806 APIs you can hit from a
`curl` with no signup.

### Transport security

| HTTPS | Count |
|---|---|
| Yes | 1,627 |
| **No** | **92** |

> ⚠️ **92 listed APIs do not support HTTPS.** Anything sent to them — including any key — travels in
> plaintext. The repo records this faithfully in a column; it does not warn you. **Filter on this
> before using anything from the list.**

### CORS

| CORS | Count | Share |
|---|---|---|
| **Unknown** | **986** | **57%** |
| Yes | 580 | 34% |
| No | 153 | 9% |

**The majority of entries have undocumented CORS status**, which for browser-side use means "assume
it will fail until tested."

---

## 3. The 51 categories

Animals · Anime · Anti-Malware · Art & Design · Authentication & Authorization · Blockchain · Books ·
Business · Calendar · Cloud Storage & File Sharing · Continuous Integration · Cryptocurrency ·
Currency Exchange · Data Validation · Development · Dictionaries · Documents & Productivity · Email ·
Entertainment · Environment · Events · Finance · Food & Drink · Games & Comics · Geocoding ·
Government · Health · Jobs · **Machine Learning** · Music · News · Open Data · Open Source Projects ·
Patent · Personality · Phone · Photography · Programming · Science & Math · Security · Shopping ·
Social · Sports & Fitness · Test Data · Text Analysis · Tracking · Transportation · URL Shorteners ·
Vehicle · Video · Weather

**Only one category — Machine Learning — is AI-adjacent**, and it is a general ML-services category,
not free-LLM-inference. **For the free-LLM question that prompted this research, `mnfst` and
`freellmapi` are the relevant repos and this one is mostly orthogonal.** It is included because it
was asked for, and because it is genuinely the best general free-API index that exists.

---

## 4. Data-quality findings

Counted, not asserted:

1. **Inconsistent formatting in the Auth column.** `` `apiKey` `` (751) versus bare `apiKey` (3), and
   `No` (806) versus `` `No` `` (2). Small, but it breaks naive parsing — **anyone scripting against
   this README must normalise before counting.** Every automated summary of this repo that reports
   round numbers has probably tripped on it.
2. **57% of CORS fields are `Unknown`.** Not an error, but it means the column cannot be relied on
   for filtering.
3. **92 HTTP-only entries** in a list titled "free APIs" with no inline warning.
4. **No rate limits anywhere.** The schema has no quota column. For the free-LLM use case this is
   disqualifying — `mnfst` records RPM/RPD/TPD per model; this repo records none.
5. **No last-verified dates.** A ten-year-old list with 1,730 entries certainly contains dead
   endpoints; nothing in the README says which were last checked.

---

## 5. How the three repos compare

| | `mnfst` | `freellmapi` | `public-apis` |
|---|---|---|---|
| Type | curated list | **running router** | curated list |
| Scale | 16 providers | 34 providers / 635 endpoints | **1,730 APIs / 51 categories** |
| Stars | 7.3K | 23.5K | **474K** |
| Licence | **CC0-1.0** | MIT | MIT |
| Age | 5 months | 4 months | **10 years** |
| LLM-specific | **yes, entirely** | **yes, entirely** | **no — 1 of 51 categories** |
| Rate limits recorded | **yes, per model** | tracked at runtime | **none** |
| Data-training policy | **yes** | no | no |
| Auth status recorded | implicitly | n/a | **yes, per API** |
| HTTPS status recorded | no | no | **yes, per API** |

**Use each for what it is good at:** `mnfst` to choose a free LLM provider on real limits;
`freellmapi` to actually *consume* several at once; `public-apis` for the other 1,700 things that are
not LLMs.

---


## 5b. ⚠️ Governance — added after the deep-research run

The workflow surfaced a **maintainer-versus-owner dispute** that bears directly on whether this
catalogue is reliably stewarded.

**November 2023:** the volunteer maintainers publicly stated that under owner **APILayer** they had
their repository access silently reduced:

> *"all of us maintainers had our access levels lowered without any communication, motivation or
> anything close to that."* `✓W`

They asked for either full organisational ownership or a complete transfer. The dispute led to the
**`marcelscruz/public-apis` maintainer fork.** `✓W`

**Three findings that affect how much you can trust an entry:**

1. **The project has been dormant before.** Before the ~late-2022 revival it was *"dead, with over
   300 open pull requests"*; four maintainers cleared that backlog in two months and have since
   handled **1,000+ PRs**. `✓W` Upkeep has been **discontinuous, not continuous**.
2. **Entries can bypass the repo's own validation.** The owner-controlled `apilayer-admin` account
   pushed commits that *"broke tests and policies"*. `✓W` So the link and format checks were **not
   always in force** when entries were merged.
3. **There is no systematic verification of any listed API.** Content quality depends entirely on
   volunteer PR triage. `✓W` Nobody is calling these 1,730 endpoints to confirm they still work, are
   still free, or still match their stated auth.

**Fair caveat:** the dispute is dated **22 November 2023** and is closed — nearly three years before
this file. It says nothing about LLM providers or rate limits. `✓W` It is a **stewardship** signal
about a corporate-owned, volunteer-maintained catalogue, not evidence that any specific row is wrong.

## 6. Honest limitations

- **README-level analysis only.** No API in the list was called. Every count above is a count of
  *rows*, not of *working endpoints*.
- **"Free" is undefined in this repo.** It spans no-auth-no-limits, free tiers, and freemium
  services with paid gates. The schema cannot distinguish them.
- **No maintenance signal per entry.** Repo-level activity is healthy (pushed 2026-08-31), but a
  1,730-row list cannot be uniformly fresh, and nothing marks which rows are stale.
- **Category counts were not computed per-category** — only the 51 names were extracted.
- **The `APILayer APIs` section** appears above the index and is a sponsor placement; it was not
  analysed separately.

## Sources

1. [`public-apis/public-apis`](https://github.com/public-apis/public-apis) — README (241,584 bytes) fetched via GitHub API and parsed directly; repo metadata; both 2026-09-01

## Change Log

- **2026-09-01** — Created by **parsing the repo's README directly** rather than repeating its
  description. Live GitHub API metadata confirmed: **MIT**, **473,984 stars / 52,334 forks**, created
  **2016-03-20**, pushed 2026-08-31, not archived.
  Measured contents: **1,730 API entries across 51 categories** — figures counted from the README,
  not quoted from anywhere. Auth distribution counted: **806 need no authentication at all (47%)**,
  751 use `apiKey`, 150 use OAuth. Transport counted: **1,627 HTTPS, 92 without** — flagged as a real
  security finding since the repo records HTTP-only status in a column without warning. CORS counted:
  **986 of 1,730 (57%) are `Unknown`.**
  Data-quality findings from parsing: **inconsistent formatting in the Auth column** (`` `apiKey` ``
  ×751 vs bare `apiKey` ×3; `No` ×806 vs `` `No` `` ×2) that will break naive scripted counts; **no
  rate-limit column anywhere**, which is disqualifying for the free-LLM use case that prompted this
  research; and **no per-entry last-verified dates** on a ten-year-old list.
  Principal conclusion recorded plainly: **this repo is largely orthogonal to the free-LLM question**
  — only 1 of its 51 categories (Machine Learning) is AI-adjacent, and it is general ML services
  rather than free LLM inference. It is included because it was asked for and because it is the best
  general free-API index in existence, not because it answers the LLM question. Added a three-repo
  comparison table showing which of the three to reach for and why.

- **2026-09-01 (update — post-workflow)** — Added section 5b after the deep-research run
  (`wf_5cf67b3e-3b8`) surfaced a **governance dispute**: in November 2023 the volunteer maintainers
  stated that owner **APILayer** silently reduced all their access levels, and asked for ownership or
  transfer — the dispute behind the `marcelscruz/public-apis` fork. Three points recorded as they
  affect entry trustworthiness: the project **had been dormant** before its late-2022 revival (300+
  stalled PRs, then 1,000+ handled), the owner's `apilayer-admin` account **pushed commits that broke
  the repo's own tests and policies** so entries could bypass validation, and **no systematic
  verification of any listed API exists** — quality rests entirely on volunteer PR triage. Balanced
  with the fair caveat that the dispute is closed and dates from three years before this file, and
  says nothing about any specific entry's accuracy.