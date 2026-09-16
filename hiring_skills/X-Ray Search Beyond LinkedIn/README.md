# X-Ray Search Beyond LinkedIn

A Claude Code skill for building Google X-ray search strings on the open web **outside
LinkedIn** — GitHub, Stack Overflow, Behance/Dribbble, Kaggle/ResearchGate, Xing, Meetup,
ADPList, Substack, Zendesk community, company team pages, and resumes/CVs floating anywhere on
the web. Named after **Benoit Bliard** (Search & Go), whose training specialty is exactly this,
plus **Glen Cathey** (Boolean Black Belt) and **Irina Shamaeva** (Boolean Strings) for
supplementary technique.

A `.claude/skills/` symlink in the workspace root points into this folder, same pattern
as the other Claude Code skills in this repo.

## Why this exists, and what it doesn't replace

The LinkedIn Boolean Search skill already covers LinkedIn Boolean and X-ray in depth,
including the 2024 public-profile-redaction workaround. This skill exists because "where else
besides LinkedIn" was a real gap — sourcing on GitHub, Stack Overflow, Behance, Kaggle, Meetup,
or the open web generally needed its own reference rather than being bolted onto the LinkedIn
skills or left to ad-hoc searching each time. If the ask is actually about LinkedIn, use Irina
instead — this skill defers to it explicitly rather than duplicating its content.

## Research process and source quality

Started from a ~50-URL reading list (general recruiting blogs, Medium posts, Substack
newsletters, YouTube videos, and bio pages for Bliard/Glen Cathey/Shally Steckerl), assessed in
two passes before drafting anything:

**Pass 1 — triage the original list.** Fetched every URL (WebFetch, with WebSearch as a fallback
for the ones that blocked bots — Medium and LinkedIn both did). For the 11 YouTube videos, titles
alone weren't enough to judge instructional depth, so `youtube-transcript-api` was pip-installed
and used to pull actual transcripts (with `.translate('en')` for the two that only had Russian
auto-captions) — a general technique worth reusing any time a research pass needs to assess
YouTube content, not just this one.

Result: a lot of the original 50 turned out to be low-value —
**Asanify/Taggd/Qandle** are the same templated HR-SaaS glossary boilerplate duplicated
near-verbatim across a dozen similar sites (Keka, FactoHR, Akrivia, Pazcare, Hono.ai...), zero
original content. **Pin.com and Lessie.ai** are real companies but their X-ray articles are
marketing funnels for their own AI-sourcing products, framing X-ray as "the old way" — usable for
a stray example, not a base to build on. Several Substack/Medium posts were off-topic (market
economics, layoffs, candidate-experience commentary) rather than technique. Bliard's own 4 URLs
were all bio/course-marketing pages with zero actual teaching content on them.

**Pass 2 — go find the real material.** This is what actually produced the skill content:

- **Benoit Bliard's own 3-part "Google Search" series** — found republished in full on
  sourceurs.be (a Belgian sourcing blog), matching the exact part titles ("les opérateurs de
  Google," "comment chercher dans un site," "chercher partout sur le web") that a French
  tech-recruiter resource list (helenely.com) named as his series. This is Bliard's actual
  methodology, not a bio page about him — the hypothesis-first stance and the 4-step
  site-search method in Phase A/B of the skill both come directly from it.
- **Glen Cathey's "How to Find Resumes on the Internet with Google"** — found on both ere.net and
  the original booleanblackbelt.com. The resume `intitle:`/`inurl:` targeting, the exclusion list,
  the area-code/zip-radius geographic trick, and the 80/20 titled-vs-untitled rule all come from
  this one article.
- **Irina Shamaeva's Boolean Strings target-site list** (booleanstringsai.wordpress.com) —
  confirmed the full platform roster worth covering (LinkedIn, Twitter, Xing, AngelList,
  About.me, Upwork, Stack Overflow, GitHub, Behance, Dribbble, Kaggle, Google Scholar,
  ResearchGate), though it pointed to a query-builder tool rather than showing raw strings itself.
- **A cluster of corroborating recruiter blogs** (firmbee.com, amazinghiring.com,
  redirecruit.com, herohunt.ai, hirezapp.com, Workable's Meetup tutorial) supplied the actual
  copy-paste query strings per platform in the cheatsheet — cross-checked against each other since
  no single one was authoritative enough to trust alone.
- **YouTube, after transcripts**: a handful were genuinely useful once actually read — concrete
  `site:stackoverflow.com/users` and `filetype:xls "list of attendees"` examples, plus
  confirmation of Tumblr and Meetup as X-ray targets that didn't otherwise surface. Several others
  turned out to be tool-marketing walkthroughs (Recruit'em, assorted "AI boolean generator" tools)
  — still useful for confirming which platforms matter, credited as such in the cheatsheet, not
  treated as technique sources in their own right.

**Found on a later pass, previously thin:** the nammooo Medium article ("Ingenious way to do
X-Ray Sourcing") — unreachable in the original research pass (Medium blocks bots, no working
mirror found at the time). Recovered directly in the Pass 4 research session (2026-09) once the
exact article URL was in hand. Contributed three genuinely new operators not previously in the
cheatsheet — `AROUND(n)` (proximity), `related:` (similar-site discovery), and `allintitle:`
(strict multi-term title match) — now folded into the core operators table. Its platform-specific
claims (GitHub, Stack Overflow, Twitter) didn't add anything beyond what Pass 4's own live testing
already covered.

**Pass 3 — Diane pushed back on Phase A being too shallow.** The original Phase A was a flat
"if function X then platform Y" list — reasonable for engineering/design/data, where a dedicated
platform obviously exists, but it broke down for functions like product and customer support that
don't have one. Diane's specific ask: read *every* signal in a JD/intake doc (not just the title),
and go find where functions without an obvious platform actually leave public traces. This
research pass changed the skill in three ways:

- **Found two genuinely cross-functional techniques**, not tied to any one platform: a
  **Substack author-bio search** (`inurl:about "<role>" site:substack.com` — works because every
  Substack publication is its own subdomain, confirmed working for product, customer success/
  support, *and* engineering-leadership writers alike in direct testing) and an **ADPList mentor
  search** (`site:adplist.org/mentors "<role>" "<n>+ years"` — ADPList spans product, design,
  engineering, data, marketing, sales; confirmed real profile pages surface directly, not an
  index page). These now carry most of the weight for product specifically, since Product Hunt —
  the obvious guess — did **not** turn up a confirmed indexed profile pattern in testing.
- **Found a real customer-support-specific source**: Zendesk's own community forum has public,
  indexed profile pages (`site:support.zendesk.com/hc/*/profiles/`) once a user makes a public
  post — confirmed directly, individual named profiles surfaced. Scoped caveat documented in the
  cheatsheet: this is Zendesk-community-specific, skewed toward practitioners/admins engaged
  enough to post, not the whole function.
- **Found real negative results worth documenting, not just positive ones.** Wellfound/AngelList
  X-rays company and job pages but confirmed *not* candidate profiles (corrected from the original
  draft's vaguer "named repeatedly, untested" note). IEEE and ACM's member directories are both
  gated behind a login despite being named across sourcing material as if they were open. Slack
  and Discord communities (Rands Leadership, dbt Community, Support Driven, CS Café, Reactiflux,
  and others) are real, relevant, and completely un-X-ray-able — join-required, not indexed.
  Reddit is pseudonymous — a discovery tool for finding the right subreddit, not a way to identify
  named individuals. All of this is now in the cheatsheet's own "Not X-ray targets" section so the
  skill doesn't quietly imply every plausible-sounding community is a query away.

Phase A in `SKILL.md` was rewritten around this: a signal-extraction table (function, credential,
named tool, seniority language, known target companies) feeding a function→platform table that
explicitly marks confidence per platform, rather than one flat bullet list treating a confirmed
pattern (GitHub) and an untested guess (Product Hunt) with the same authority.

**Pass 4 — live-testing pass to firm up unconfirmed claims and extend coverage (2026-09).**
Diane's ask this round was explicit: verify what Pass 2/3 had flagged as untested or thin, *and*
extend coverage to new platforms/functions, treating both as equally worth doing rather than
picking one. Method: run the actual flagged (or candidate) query live via search, the same
"confirmed live" standard already used elsewhere in this skill, rather than reasoning about
whether a platform *should* be indexable.

Confirmed corrections to previously-unconfirmed or overconfident claims:
- **Stack Overflow's bare-profile search** — failed a third independent live trial
  (`site:stackoverflow.com/users devops france`, zero `/users/` results). Upgraded from
  "unverified" to a **confirmed negative** — stop suggesting this template.
- **Product Hunt maker profiles** — failed live (`site:producthunt.com/@ "product manager"`,
  zero individual profiles). Also upgraded from "untested guess" to **confirmed negative**.
- **GitHub's `language:`/`location:`/`followers:` native-search syntax** — confirmed NOT working
  as literal Google-indexed text. `intitle:"at master"` *is* real indexed text, but it's a
  repo-file-path title, not a profile-page title — corrected the cheatsheet's framing of both.
- **Kaggle** — upgraded from "thinner example, treat as a starting point" to a confirmed working
  technique, once reframed the same way as GitHub: search notebook/discussion/dataset pages (which
  carry the username in the URL and an expertise-tier label in the title), not the bare profile
  root (which is bot-gated).
- **ResearchGate** — upgraded from "thinner example" to the **strongest-confirmed** academic
  target in the cheatsheet — profile titles alone already carry name + role + institution.
- **Xing** — downgraded. Previously assumed to work like LinkedIn; two independent live tests
  found zero individual profile pages. This is the one correction this pass made in the
  *pessimistic* direction — worth calling out since most of this pass's corrections went the other
  way.
- **The nammooo Medium article** — recovered (see above), contributed `AROUND()`, `related:`,
  `allintitle:` to the core operators table.

New platforms/techniques added, all confirmed live (2026-09):
- **GitLab** — real individual profiles surfaced directly from a plain keyword search, no strong
  anchor phrase needed. Added as a developer-sourcing target alongside GitHub.
- **ORCID** — real individual researcher pages surfaced directly. Added alongside Google
  Scholar/ResearchGate for academic/research sourcing.
- **Twitter/X bio search** — surprising positive: real profile pages with bios still surface via
  `site:x.com`, despite X's reputation (and past history) of blocking crawlers. Added as a third
  cross-functional technique, with an explicit caution that this could change again.
- **Substack, extended to sales** — `inurl:about "sales" site:substack.com` surfaced real
  sales-focused newsletters, extending the existing product/CS/engineering-leadership confirmation
  to a fourth function. Noted with a caveat: this particular test's results skewed toward
  publication homepages rather than a clean author-bio `/about` page, unlike the cleaner
  product/CS hits — spot-check before relying on it the same way.

New negative findings (real platforms, confirmed not usable as candidate-profile X-ray targets),
added to the cheatsheet's "Not X-ray targets" section:
- **RepVue** — real indexed pages, but company-level sales-org reviews, not candidate profiles.
- **Bravado** — didn't surface at all; app-gated.
- **Welcome to the Jungle** — company/job pages only, no candidate profiles. Directly relevant
  given Diane sources from France.
- **Viadeo** — confirmed defunct (liquidated after a failed international expansion); not a live
  French-market alternative to LinkedIn/Xing.
- **dev.to** — two different anchor-phrase attempts both failed; root cause traced to dev.to
  deliberately not displaying follower/following counts publicly, which likely also explains why
  other structural anchors haven't surfaced individual profiles either.

This pass also added a **Sales/Marketing** row to the function table, alongside Product, since
both hit the same "no dedicated confirmed platform" shape and both sales-specific platforms tested
(RepVue, Bravado) failed as candidate sources — they lean on the same cross-functional techniques
(Substack, ADPList) that already carry Product.

## Files

- `SKILL.md` — the skill definition Claude Code reads when this fires.
- `references/target-sites-and-operators.md` — the full operator table, Bliard's 4-step method,
  the platform-specific query bank (GitHub, Stack Overflow, Behance/Dribbble, Kaggle/ResearchGate,
  Xing, Meetup, Wellfound, Zendesk community, company team pages, resumes/CVs, conference
  attendee lists), the cross-functional techniques (Substack author-bio search, ADPList), and the
  "not X-ray targets" section (Slack/Discord, IEEE/ACM, Reddit, Handshake).
- `README.md` — this file.

A `.claude/skills/` symlink in the workspace root points to this folder — that's what
Claude Code actually loads.
