# X-Ray Search: Target Sites & Operators Cheatsheet

Condensed from Benoit Bliard's "Google Search" 3-part series (Search & Go), Glen Cathey's
"How to Find Resumes on the Internet with Google" (Boolean Black Belt / ERE.net), Irina
Shamaeva's Boolean Strings target-site list, and roughly a dozen corroborating recruiter blogs.
Also now incorporates Namrata Singh's ("nammooo") Medium X-ray article, previously unreachable, and
a live-testing research pass (2026-09) that verified or corrected several previously-unconfirmed
claims — see README's Pass 4 for the full methodology. Full provenance and source-quality notes in
`README.md`. This covers **X-ray search outside LinkedIn** — for LinkedIn Boolean/X-ray, use the
LinkedIn Boolean Search skill instead (its cheatsheet already covers LinkedIn's post-2024
public-profile redaction and the Mini-People Aggregator bulk-import workflow).

## Why X-ray a platform at all, even one with decent native search

Not just a workaround for gated/paywalled content — the real, durable reason to X-ray a platform
at all is that **Google's ranking algorithm and the platform's own internal search ranking are
completely unrelated to each other.** A platform's own search ranks by its own signals (network
proximity, premium/paid-seat weighting, profile completeness, recency, engagement). Google ranks
by an entirely different signal set (inbound links, keyword match, crawl freshness). Same
underlying pool of public content, two unrelated sort orders — so X-raying doesn't just reach
what the platform's search would eventually show you on page 40; it surfaces a genuinely
different *first page* of results, independent of whatever the platform's own algorithm chose to
rank low or bury. This is the same underlying idea as the Irina cheatsheet's "dark matter
candidates" and bottom-to-top review order (both about escaping one platform's own ranking bias),
generalized: X-ray gets you a second, independent ranking engine looking at the same data, for
free, on any platform you point it at — not only LinkedIn.

Confirmed directly in a live trial (2026-09): an X-ray search against LinkedIn itself
(`site:linkedin.com/in "site reliability" pulumi OR ansible`) surfaced different named profiles,
with full headline text visible, than what would be expected from LinkedIn's own top-ranked
Recruiter results for the same terms — worth treating as real evidence for this principle, not
just a theoretical argument.

## Core operators (work on Google; most also work on Bing)

| Operator | Does | Example |
|---|---|---|
| `site:` | Restrict to one domain or path | `site:github.com`, `site:stackoverflow.com/users` |
| `intitle:` | Word must appear in the page `<title>` | `intitle:resume` |
| `inurl:` | Word must appear in the URL | `inurl:cv` |
| `filetype:` / `ext:` | Restrict to a file format | `filetype:pdf`, `ext:doc` |
| (space) | Implicit AND | `python london` = both terms |
| `OR` (caps) / `\|` | Either term | `python OR golang` |
| `-` | Exclude a term | `-job -jobs -sample` |
| `" "` | Exact phrase | `"machine learning engineer"` |
| `*` | Wildcard, fills in unknown word(s) | `"ingénieur * mécanique"`, `dev*` → developer/development |
| `..` (numrange, no spaces) | Numeric range — the classic use is a **zip/postal-code radius search substituting for a location field** | `75001..76155`, `75000..78999` |
| `()` | Groups an OR so it doesn't leak into the surrounding AND logic | `(python OR golang) london` |
| `before:` / `after:` | Date-restrict indexed content (useful for finding recently-active profiles/posts) | `after:2025-01-01` |
| `AROUND(n)` | Proximity — both terms within `n` words of each other, order-independent | `(B.Tech \| BE) AROUND(5) IIT` |
| `related:` | Finds sites similar to a given domain — useful for discovering adjacent platforms to X-ray, not a candidate-search operator itself | `related:github.com` |
| `allintitle:` | All following terms must appear in the title (stricter multi-term variant of `intitle:`) | `allintitle: resume "product manager"` |

Found via the nammooo Medium article (previously unreachable — Medium blocks bots; recovered
directly 2026-09 once the exact URL was known). The rest of that article was standard LinkedIn
Boolean and operators already covered above; `AROUND()`, `related:`, and `allintitle:` were the
only genuinely new additions it contributed.

**Rule that trips people up (Bliard, both languages, both sources independently confirm it):**
never use capitals in the operator name itself, never put a space after the colon. A bare space
between terms already means AND — don't type the word `AND`. Wrapping several words in `"..."`
does something different, not a stronger AND: it forces them to be matched as one exact phrase.
`OR` (or `|`) is the only way to get genuine either/or logic between terms or `"phrases"`.

**Second rule, also Bliard, confirmed directly in the group (2026-09) while fixing someone else's
broken query:** when building an `intitle:`/`inanchor:`/`inurl:` stack (his own 4-step method,
below), avoid putting a quoted multi-word phrase directly behind the operator (`inanchor:"conducteur
de travaux"`) — split it into separate single-word operator instances instead
(`inanchor:conducteur inanchor:travaux`), and don't reuse the same keyword more than once across
the query (e.g. `électricité` appearing both bare and inside a quoted phrase elsewhere in the same
string). The live example: a member's draft `inanchor:"conducteur de travaux"|"conducteur
travaux" inanchor:électricité|"électricité industrielle"|"HTA"|"BT"` was fixed by Bliard to
`inanchor:conducteur|conductrice inanchor:travaux électricité|electrique|"HTA"|"BT"|chantier|affaires`
— note this is presented as his stated best practice for this specific operator-stacking
technique, not a blanket claim that Google can never parse a quoted phrase after an operator: this
same file's GitHub section has one live-tested counter-case (`intitle:"at master"`, confirmed
working, just not useful for profile-finding) — worth testing live rather than assuming either
rule always wins if a stacked query behaves unexpectedly.

## Bliard's 4-step method for building a site-specific query (don't skip to keyword-bashing)

1. **Identify what you're actually looking for** on the target site — a profile, a CV, a member
   list, a repo.
2. **Observe the URL structure** of a known example page on that site (open one manually first)
   — most sites that expose profiles use a predictable path (`/users/`, `/in/`, `/members/`,
   `/projects/`).
3. **Examine the page title** of that same example — often structured predictably too (`Name -
   Job Title | Site`), which is what makes `intitle:` powerful.
4. **Locate structured recurring text** on the page — phrases that only appear on the page type
   you want (`"joined on"`, `"member since"`, `"interests"`) — use these to exclude everything
   else on the domain that isn't a profile page.

Worked example, built up in layers exactly the way Part 2 of the series does it:
```
site:linkedin.com/in intitle:director intitle:recruitment
→ site:linkedin.com/in intitle:director | intitle:manager | intitle:responsible intitle:recruitment
→ ...same, + "paris and suburbs"
```
Same layering approach applies to any target site below — start narrow on one signal, add the
next once you've confirmed the first actually returns profile pages and not noise.

**When a site has no predictable directory** (results come back in inconsistent order/language),
use a wildcard in the path itself: `site:example.com/*/p`.

## Platform-specific query bank

### GitHub (developers)
```
site:github.com "followers" "following" "repositories" python golang -inurl:issues -inurl:blob -inurl:pull -inurl:topics -inurl:orgs
```
Confirmed working profile-page anchor — see the full writeup below, this replaces the older
`"joined on"` version that failed live testing. `language:go location:london followers:5..10` is
GitHub-native search-UI syntax, not literal page text — **confirmed NOT working as a Google X-ray
operator** (tested live 2026-09: `site:github.com "language:python" "location:france"
"followers:"` returned zero individual profiles, only topic pages and an unrelated followers-tab
URL). `intitle:"at master"` **is** real, indexed page-title text — but it's the title of a repo
file/tree page (`reponame/path at master · owner/repo`), not a profile page (confirmed live,
2026-09: every result was a file or folder listing). Useful if you're hunting for a specific file
pattern inside repos, not for finding people directly — don't reach for it as a profile-page
anchor. Older `site:github.com inurl:tab=repositories <language> <technology>` pattern still
surfaces profiles by repo-tab content; GitHub removed public emails from profiles, so don't expect
the classic `"gmail.com" site:github.com` email-discovery trick to still work — plan to enrich
separately once you have usernames.

**"joined on" as the anchor phrase failed to surface any individual profile pages in two
independent live trials (2026-09)** — repo/topic/doc pages dominated every time. Root cause found
by debugging live: `"joined on"` just isn't reliably crawled as page text. **Fix: use the sidebar
trio instead — `"followers" "following" "repositories"` together** — confirmed working (surfaced
real individual profiles, e.g. a Senior Developer Advocate at Pulumi and a former Pulumi engineer,
on the first successful test):
```
site:github.com "followers" "following" "repositories" pulumi ansible -inurl:issues -inurl:blob -inurl:pull -inurl:topics -inurl:orgs
```
**Location fits, but only if you drop to ONE tech keyword to make room for it — confirmed live.**
Stacking two tech terms (`pulumi ansible`) plus location collapsed back to repo/topic noise, same
as before. Dropping to a single tech term freed up the budget and surfaced real, location-tagged
individual profiles:
```
site:github.com "followers" "following" "repositories" ansible france -inurl:issues -inurl:blob -inurl:pull
```
→ surfaced a real hit: a GitHub user from Lille, France with Ansible relevance, directly in the
result snippet. **Prefer `france` over a specific city name here** — a city-name test
(`pulumi bordeaux`) top-matched a Seattle-based user whose surname happened to be "Lacey-Bordeaux,"
a false positive from a bio being freeform text. GitHub bios don't have LinkedIn's structured
location field, so a city name risks matching an unrelated substring; the country name is safer.
Working ceiling, confirmed: **anchor trio + one tech term + one location term (`france`, not a
city)** — three real signals total, not four. Replace `"joined on"` with the trio anywhere else it
appears in this cheatsheet or in Diane's own saved queries.

**Correction after further live testing — don't over-generalize "collapse every OR."** First
attempt stacked a 4-way synonym OR (`mlops OR production OR deployment OR monitoring`, genuinely
good synonym coverage, not vagueness) on top of the core skill and location, and that combination
didn't return confirmed France-based hits. Collapsing it down to the single word `production`
(alongside a single anchor phrase) did work — **but re-testing the full 4-way OR-group again with
only a single location term (`france` alone, then `bordeaux` alone, no OR between them) still
failed both times.** So the issue isn't "too many total signals" or "OR-groups are bad" — it's
specifically that this rich a synonym group plus *any* location constraint underperforms in this
tool, full stop. Don't gut a well-built synonym OR-group just to force a location match into the
same query. Instead, **run it in two passes**:
1. Full synonym coverage, no location — the best-quality candidate list:
   `site:linkedin.com/in "AI agent" OR "agentic AI" langchain (mlops OR production OR deployment OR monitoring)`
2. Check location by hand on whoever surfaces (LinkedIn shows it directly on the result) rather
   than trying to bake France/Bordeaux into the same query.

The trimmed single-term version below still stands as a **separate, working alternative** when
Diane specifically wants a location-scoped query in one shot and is fine trading some synonym
coverage for it — not as something that should replace the full version by default.

**What worked instead, for a niche/emerging specialization: search for the distinctive PROJECT,
not the profile.** `site:github.com "mcp server" agent langchain -inurl:issues -inurl:pull
-inurl:blob` surfaced real repos directly, each with the builder's username sitting right there
in the repo path (`github.com/<username>/<repo>`) — go from the repo to `github.com/<username>`
yourself rather than trying to search the profile directly. This is the more productive angle
whenever the role is built around a specific, nameable kind of artifact (an MCP server, a
particular agent framework, a specific kind of pipeline) rather than a generic language/library —
the project's README has far more indexable text than any profile ever will.

### GitLab (developers — confirmed alternative/supplement to GitHub)
```
site:gitlab.com devops france -issues -merge_requests
```
Confirmed working directly (2026-09) — individual profile pages (`gitlab.com/<username>`)
surfaced with no strong anchor phrase needed at all, just a role/stack keyword, a location term,
and exclusions for the two noisiest non-profile page types (`issues`, `merge_requests`). Worth
reaching for alongside GitHub, especially for candidates at companies that run self-hosted GitLab
or use it as their primary forge — Europe-heavy usage in particular. Anchor-phrase equivalent to
GitHub's `"followers" "following" "repositories"` trio not yet tested; the plain keyword approach
above already works well enough that this hasn't been a blocker.

### Stack Overflow — confirmed NOT working as a bare-profile X-ray target
```
site:stackoverflow.com/users "ruby on rails" belfast
site:stackoverflow.com/users amsterdam (react OR typescript)
```
Every user with an account has a profile under `/users/` — this is the single most-repeated
example across every source checked, going back to Cathey's original 2009 material, which is
exactly why it's worth flagging hard: **it has now failed live in three independent trials
(2026-09)**, including a third attempt (`site:stackoverflow.com/users devops france`) that
returned zero `/users/` pages at all — Google substituted unrelated GitLab and Stack Share results
instead. Treat this as a **confirmed negative**, not a gap in query-writing skill. Don't present
this template to Diane as working; if Stack Overflow itself becomes relevant, point her to its own
native search instead of X-raying it.

### Behance / Dribbble (designers)
```
site:behance.net inurl:projects "Graphic Designer"
site:dribbble.com "UX Designer" london
```

### Independent portfolios (any creative/technical role without a platform monopoly)
```
intitle:portfolio "UX Designer" ("London" OR "UK") -template -jobs -wordpress
```

### Kaggle / Google Scholar / ResearchGate / ORCID (data science, ML, academic/research roles)

**ResearchGate — strongly confirmed, best of this group.** A plain query already returns rich,
directly-usable profile pages:
```
site:researchgate.net/profile "machine learning" france
```
confirmed live (2026-09): every result was a real named individual, and the page **title alone**
already carries name + role + institution + department (e.g. "Nguyen Anh Minh MAI | R&D AI SW
Engineer | Doctor of Philosophy | Valeo, Paris" — usable for triage without even opening the
page). Best-confirmed academic-sourcing target in this whole cheatsheet; lead with this one.

**Kaggle — works, but not as a bare profile search; go through the person's activity pages
instead.** `site:kaggle.com <skill/competition keyword>` surfaces real people, but via their
notebook/discussion/dataset pages, not a bare profile — confirmed live (2026-09):
```
site:kaggle.com "gradient boosting" competition
```
returned individually-authored notebooks (`kaggle.com/code/<username>/<notebook-title>`) with the
username sitting directly in the URL, same pattern as the GitHub project-level technique above.
The bare profile root (`kaggle.com/<username>`) itself sits behind a bot-check wall, but the same
username's `/code`, `/discussion`, and `/datasets` sub-pages are indexed and even carry an
expertise-tier label in the title (confirmed: "Cam Nugent | Notebooks Expert | Kaggle", "Cam
Nugent | Datasets Expert | Kaggle") — go through those, not the bare root.

**ORCID — new addition, confirmed working.** Every researcher's unique ORCID iD page is public
and indexed:
```
site:orcid.org "machine learning" researcher
```
confirmed live (2026-09) — real individual pages (`orcid.org/0000-xxxx-xxxx-xxxx`) surfaced
directly with names attached. Thinner on role/seniority detail than ResearchGate's page titles,
but a good second confirmation source for the same population, especially for anyone whose main
public footprint is publication history rather than an active ResearchGate profile.

**Google Scholar**: still only thin corroboration from the original research pass, no live test
run this session — treat as a starting point to test, not a proven template, unlike the three
above.

### Xing (DACH-region professional network, LinkedIn's regional competitor) — downgraded: unconfirmed, likely not indexed this way

**Correction to an earlier assumption.** This cheatsheet previously assumed Xing follows the same
`site:` + profile-path logic as LinkedIn. **Two independent live tests (2026-09) found zero
individual Xing profile pages** —
```
site:xing.com/profile "software engineer" berlin
site:xing.com "berufserfahrung" software
```
both returned only unrelated StepStone job listings and Wikipedia/generic pages, no
`xing.com/profile/...` hits at all. Don't present a Xing X-ray query to Diane as working without
retesting it directly first — it may need a different path structure than `/profile/`
(untested), or Xing's profile pages may simply not be signed-out-indexable the way LinkedIn's
still partially are. For DACH-region roles in the meantime, lean on the general resume/CV search
and company team-page techniques instead of assuming Xing will fill the gap.

### Wellfound / AngelList — company pages yes, candidate profiles no
Tested directly: **X-ray does not work as a backdoor into Wellfound's candidate pool** — unlike
LinkedIn, individual candidate profiles aren't crawlable this way. What *is* crawlable is the
company side:
```
site:wellfound.com "series a" "backend engineer"
```
Useful for mapping which startups are hiring what and who else is competing for the same
candidate — a market-intel query, not a candidate-finder. Don't present Wellfound as a general
X-ray target for startup-adjacent candidates; it isn't one.

### Product, Sales, and Marketing — no strong platform-specific target, lean on the cross-functional techniques below

**Product Hunt — now confirmed NOT working**, not just untested. `site:producthunt.com/@
"product manager"` (live test, 2026-09) returned zero individual maker/hunter profile pages —
only product-listing and generic Product Hunt pages. Don't present a Product Hunt query as working
at all; this has moved from "untested guess" to a confirmed dead end.

**Sales and Marketing have the same shape of gap as Product** — no dedicated, confirmed candidate
platform surfaced in research. Two sales-specific candidates were tested and both failed as
candidate sources (see "Not X-ray targets" below: RepVue is company-review data, not candidate
profiles; Bravado didn't surface at all). Treat Sales and Marketing the same way as Product: lean
on the Substack author-bio search (confirmed to extend to sales — see below) and ADPList (whose
own categories explicitly include marketing, content, talent acquisition, and sales/BizDev).

For product specifically, the Substack author-bio search and ADPList mentor search (both below)
carry more of the weight than they do for functions with a dedicated platform.

### Customer support / success — Zendesk community profiles (scoped)
```
site:support.zendesk.com/hc/*/profiles/ "customer success" OR "customer support"
```
Confirmed working — individual named profile pages (e.g. "User profile for Claire Flanagan," "User
profile for Customer Support Manager") surface directly. **Scope caveat**: this surfaces people
active in *Zendesk's own community forum* specifically — support/CS practitioners and admins at
companies that use Zendesk, skewed toward those engaged enough to post publicly, not a general
cross-section of everyone in the function. Treat as one useful, confirmed source for this
function rather than a complete answer — pair with the Substack author-bio search below.

### Meetup (community/group membership as a proxy signal, not a direct skill match)
```
site:meetup.com/[group-name]/members/ "member since"
site:meetup.com RoR (OR "rubyist" OR "rails")
```
Member-profile pages carry recurring phrases (`"member of"`, `"interests"`, `"member since"`) —
use those the same way `"joined on"` works for GitHub. **GDPR note**: treat EU member data caught
this way the same way you'd treat any other public-web scrape — same handling standard as
everything else X-ray surfaces, not a free pass.

### Company "team" / "about us" pages (find employees of a specific company directly, bypassing every social platform)
```
intitle:("our team" OR "meet the team") "machine learning" amsterdam -inurl:blog
```
This is the one category that showed up in the research pass but had never been named in the
original source list — genuinely useful when you already know which companies to target (feeder
companies, competitors) and want names/roles directly rather than going through a platform.

**Don't add `"about us"` to the `intitle:` OR-group** — confirmed live (Diane, 2026-09, testing
against Platform.sh/Scalingo/Artifakt) that it pulls in noise `"our team"`/`"meet the team"` don't:
generic company-history/mission pages instead of the actual team-roster page. Stick to `"our
team"`/`"meet the team"` only; if a specific target company's roster page turns out to be titled
something else, confirm that page's actual title by opening it manually (per Bliard's 4-step
method above) rather than widening the OR-group speculatively.

### Resumes / CVs floating on the open web
```
(intitle:resume OR inurl:resume) -job -jobs -sample -samples -eoe -submit -free -"resume service" -template -"resume writers" -"resume writing"
filetype:pdf (intitle:cv OR intitle:resume) "data engineer" amsterdam -inurl:(job OR jobs OR vacancy OR sample OR template)
ext:pdf | ext:doc | ext:docx inurl:cv | inurl:curriculum | intitle:cv | intitle:curriculum <role keyword>
```
**Geographic targeting without a location field** — combine with an area code or a postal/zip
range instead of a place name:
```
(intitle:resume OR inurl:resume) -job -jobs -sample -samples (703 OR 571) (VA OR Virginia)
java (intitle:resume OR inurl:resume) 75001..76155 (TX OR Texas)
```
**Finding resumes that don't say "resume" at all** (Cathey's technique, ~20% of the pool, much
higher false-positive rate — use only once the titled/URL-tagged pool is exhausted):
```
(objective OR summary) (experience OR history) education -job -jobs -sample
```
Cathey's own stated rule of thumb: the titled/URL-tagged search (`intitle:resume OR inurl:resume`)
gets ~80% of the viable pool for ~20% of the effort; the untitled search catches the remaining
~20% but costs disproportionately more time sorting false positives. Start with the first, only
go to the second if the role is hard enough to justify it.

**Same formula, aimed at a named individual instead of a role keyword** — confirmed directly by
Bliard in the group (2026-09), answering a headhunter's question about finding a specific,
already-identified person's CV: `ext:pdf | ext:doc | ext:docx inurl:cv|curriculum | intitle:cv|curriculum
<first and last name>`. Same structure as the role-keyword version above — swap the last term for
the candidate's name once you already know who you're looking for. Bliard also confirmed explicitly
that **`ext:` and `filetype:` are the same operator** — either spelling works, no behavioral
difference between them.

### Conference / event attendee lists (leaked spreadsheets, a different sourcing angle entirely)
```
filetype:xls "list of attendees" hr event
"Attendee Export" filetype:xls
```
Genuinely surfaces real spreadsheets with name/title/company/email/phone when an event organizer
published one publicly without meaning to leave it indexable. Hit rate depends entirely on
whether the target industry's events do this — worth a quick test, not a guaranteed source.

## Cross-functional techniques (use regardless of function — carry the most weight when no platform-specific target exists, e.g. product)

### Substack author-bio search
```
inurl:about "<role/function keyword>" site:substack.com
```
Confirmed working directly — e.g. `inurl:about "product manager" site:substack.com` surfaces real
individual PM newsletter about-pages (Product Manager Academy, Product Managers at Work, Product
Management IRL); the identical pattern with `"customer success"` or `"customer support"` also
surfaced real individual authors. **Why it works generally**: every Substack publication is its
own subdomain (`<publication>.substack.com`), so a single `site:substack.com` covers all of them
at once, and `inurl:about` lands specifically on the author-bio page rather than any article. Swap
the role keyword for whatever function/skill is in play — this isn't a product-specific trick,
it's a general "find people who write publicly about their own job" technique, and product,
customer support, and engineering leadership all confirmed working in testing. **Extended to sales
(2026-09)**: `inurl:about "sales" site:substack.com` surfaced real sales-focused publications
(Sales Society, Enterprise Sales Forum, UpTempo, and others) — though this particular test's top
results skewed toward publication homepages rather than a clean `/about` author-bio page, so
spot-check that the `inurl:about` constraint actually landed before relying on it the same way as
the product/CS examples, which did land cleanly on `/about`.

**A second use for this beyond platform-coverage: an unfilterable soft-trait proxy.** Dropping
`inurl:about` and searching `site:substack.com` plus a specific technical topic (e.g. `langchain
OR "agentic ai"`) surfaces *article* pages by currently-active writers on that exact subject —
confirmed in a live trial (2026-09) for an agentic-AI/LLM engineering role where the hiring
manager's #1 candidate-rejection reason was people who rode the AI hype without genuine,
self-directed depth in the topic. Someone publishing their own technical analysis of a
fast-moving specialization *right now* is real evidence of exactly that trait — a much stronger
signal than a resume line, and worth reading their actual writing before reaching out, not just
noting that it exists. Use this article-level variant when the brief names a specific
unfilterable trait (genuine curiosity, ability to explain clearly, real depth vs. hype-chasing)
rather than only when no dedicated platform exists for the function.

### ADPList mentor search
```
site:adplist.org/mentors "<role>" "<n>+ years"
```
Confirmed working — real named mentor profile pages surface directly (not a landing/index page).
ADPList's own categories span product, design (UX/UI/product design), software engineering, data
science, marketing, content, talent acquisition, and sales/BizDev — genuinely cross-functional,
not product-only. **Selection bias worth naming**: mentors are people motivated enough to
volunteer career-coaching time, which skews toward more senior/engaged profiles — a real signal
(these are often strong candidates), but not a representative sample of the whole function.

### Twitter/X bio search — confirmed still indexed (2026-09), despite the platform's history of locking down
```
site:x.com "software engineer" bio -status
```
Confirmed live (2026-09) — real individual profile pages (`x.com/<handle>`) surfaced directly,
with name + self-written bio text visible in the result title/snippet. Genuinely worth noting as a
surprise: X has restricted crawler/bot access before and is widely assumed to be a dead X-ray
target post-2023, but a direct test this session found current, real profiles still indexed.
**Don't treat this as permanent** — X's access policy toward search engines has changed more than
once and could tighten again at any time; if a query that worked recently suddenly returns
nothing, check whether X has changed its indexing policy again before assuming the operators are
wrong. Best used as a thought-leadership/visibility signal (who's actively posting about a
specific technical topic) the same way the Substack article-level search is used, rather than as a
primary directory the way GitHub or ResearchGate are.

## Not X-ray targets, despite sounding like they should be

Confirmed during research — don't promise a `site:` query against any of these without checking
first, and say plainly to Diane that they aren't X-ray-able rather than silently skipping them:

- **Slack and Discord communities** (Rands Leadership Slack, dbt Community Slack, Support Driven,
  CS Café, Customer Success Collective, Reactiflux, Python Discord, Women in Tech Slack, and
  similar) — join-required, not publicly indexed. Genuinely valuable as a sourcing channel, but
  the action is "join the community," not "build a query." Name the specific community if it fits
  the role, but be clear about which kind of recommendation it is.
- **Professional-association member directories** (IEEE, ACM checked directly) — both require a
  logged-in membership account; neither is publicly indexed despite being named repeatedly across
  sourcing material as if they were open directories. Don't extrapolate "a professional association
  exists for this credential" into "therefore there's a public directory to X-ray" — check the
  specific association's actual access model first.
- **Reddit** — usernames are pseudonymous. Useful for finding which subreddit a community lives in
  (a discovery step, worth doing manually), not for X-raying or identifying named individuals.
- **Handshake** (campus/early-career) — requires a school-affiliated login, not signed-out
  indexable.
- **RepVue** — confirmed live (2026-09): surfaces real, indexed pages, but they're company-level
  sales-org review pages (`repvue.com/companies/<name>`), not individual sales-rep candidate
  profiles. Same shape of finding as Wellfound: real market-intel value (which sales orgs are
  rated well), zero candidate-search value.
- **Bravado** (sales community) — confirmed live (2026-09): no indexed content surfaced at all for
  a `site:bravado.co` query. Treat as app-gated, not X-ray-able.
- **Welcome to the Jungle** (French job/employer-branding platform) — confirmed live (2026-09):
  only company pages and job listings surfaced, no individual candidate profile pages. Same
  pattern as Wellfound/RepVue — useful for researching which French companies are hiring and how
  they present themselves, not for finding candidates directly.
- **Viadeo** — France's own LinkedIn-era professional network. Confirmed defunct: liquidated after
  a failed international expansion, its China subsidiary wound down years earlier. Don't suggest
  it to Diane as a French-market alternative to LinkedIn/Xing — there's nothing left to X-ray.
- **dev.to** — tested twice live (2026-09) with two different anchor-phrase strategies
  (`"followers" "following"`, then `"Location" "Joined"`); neither surfaced individual profile
  pages. Root cause for the first: dev.to deliberately doesn't display follower/following counts
  publicly (confirmed by dev.to's own community discussion of this design choice), so that anchor
  never appears on a real page. Treat as unconfirmed/likely not working until a different anchor
  phrase is found and tested.

## Iteration & scaling tools (not Google operators, but named repeatedly across sources)

- **Data Miner** (Chrome extension) — has a pre-built "Google X-ray" recipe that scrapes a SERP
  of X-ray results straight into Excel (name, title, company, email if present, profile URL).
  Useful once a query is dialed in and you want the result set as a list, not one-by-one clicks.
- **Recruit'em, Loopster, and similar form-based X-ray builders** — generate the underlying
  `site:`/`intitle:`/`inurl:` string from a fill-in form (country, title, keywords, exclusions)
  across LinkedIn/GitHub/Xing/Stack Overflow/Twitter/Dribbble in one pass. Useful as a faster
  starting point than typing the operators by hand, especially for a first draft — but they don't
  teach the technique, so don't rely on them if a target site isn't one of their presets; fall
  back to building the query by hand from this cheatsheet.

## Realistic expectations (don't oversell this to yourself)

- **Google's boolean query length is capped around 32 words** — a very long, fully-elaborated
  string (every synonym, every exclusion) can silently get truncated or ignored past that point.
  If a long query returns suspiciously broad results, shorten it and check whether length was the
  cause before assuming the logic itself is wrong.
- **X-ray strength is entirely a function of how open the target platform still is.** LinkedIn's
  2024 public-profile redaction is the widely-cited example of a platform that used to be a great
  X-ray target and now barely is (see the Irina cheatsheet for what's left) — the same could
  happen to any platform on this list. If a query that should obviously work returns nothing,
  check by hand whether the platform still exposes that content to signed-out search at all
  before concluding your operators are wrong.
- This is a **complement to platform-native search**, not a replacement — GitHub's own search,
  Stack Overflow's own search, etc. often have filters X-ray can't replicate (GitHub's
  `followers:`, `location:` qualifiers used directly on github.com, for instance). Use X-ray when
  you specifically want to search *without* the platform's own UI (rate limits, paywalls, a
  search feature that's worse than Google's own indexing) — not reflexively for everything.


## Appendix — LinkedIn Google X-ray cross-reference (outside this skill's scope, kept here on request)

Everything in this appendix is LinkedIn-specific and belongs, per this file's own scope note above,
to the LinkedIn Boolean Search skill — it's duplicated here only because Diane asked for it
to live alongside the rest of Bliard's material rather than solely in Irina's files. Treat Irina's
skills as the primary, authoritative source for LinkedIn X-ray; this section is a copy, not a
replacement, and can drift out of date without that being caught here.

**`fr.linkedin.com` reflects the *poster's* account/IP locale, not the job's location.** A listing
under `site:fr.linkedin.com/jobs/view` tells you the person or system that published it is
associated with a France-based LinkedIn account — it is not a location filter on where the role
itself will actually be based. A `fr.linkedin.com` job could still be fully remote or based outside
France; don't present the subdomain as if it scopes the job's location, only who posted it.

**Job-posting states are three, not two, and only one of them is worth pursuing further:**
- **Fully gone** — the listing no longer resolves anywhere, removed from both Google's index and
  from LinkedIn itself. Unpublished/closed. Nothing left to recover this way.
- **Grey zone** — still surfaces in a Google X-ray result, but the LinkedIn page itself looks
  inactive when opened (no live apply flow, stale-looking). Genuinely ambiguous: could be a
  stale cache of a still-live posting, or a posting mid-takedown. Don't call it definitively live
  or definitively closed either way — say it's in the grey zone and let Diane decide whether it's
  worth a direct check.
- **Definitively taken away** — once a listing has been fully removed, there is no X-ray path to
  retrieve it. Don't promise recovery of a job Diane says has already disappeared for good.

**Three worked queries, run in Google itself (not LinkedIn's own search bar), confirmed to return
good results live:**
```
site:fr.linkedin.com/jobs/view (React OR "React.js") TypeScript (Storybook OR "design system") (Jest OR Cypress OR Tailwind) (Node.js OR Redis OR PostgreSQL OR AWS OR Docker OR Ansible)
site:fr.linkedin.com/jobs/view bedrock agentcore OR langchain OR llamaindex OR langgraph OR crewai OR autogen OR "semantic kernel" OR haystack OR dspy
site:fr.linkedin.com/in (Node.js TypeScript AWS Redis (Pulumi OR Ansible OR Terraform OR "infrastructure as code") (PostgreSQL OR "relational database" OR Postgres)
```
The first two target job postings, the third targets profiles — same `site:` pattern, different
path (`/jobs/view` vs `/in`).

**A job/title tracker via `intitle:`/`inurl:`, shared by Bliard as LinkedIn-oriented but in
principle generalizable to any job board — with a real, confirmed limitation:**
```
intitle:job|emploi|jobs|offre | inurl:job|emploi|jobs|offre intitle:directeur intitle:humaines
```
This only filters on the page's **title** (or its URL) — it does not do keyword-in-body filtering
the way a normal X-ray content search can. It narrows a result set by title pattern alone.
Confirmed limitation, not worked around yet: the only realistic use found so far is as a second
pass on top of data already scraped/collected some other way (filter a dataset you already have by
title), not as a standalone full-text search across job content.
