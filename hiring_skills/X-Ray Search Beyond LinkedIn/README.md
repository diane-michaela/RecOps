# X-Ray Search Beyond LinkedIn

A Claude Code skill for building Google X-ray search strings on the open web **outside
LinkedIn** — GitHub, Stack Overflow, Behance/Dribbble, Kaggle/ResearchGate, Xing, Meetup,
ADPList, Substack, Zendesk community, company team pages, and resumes/CVs floating anywhere on
the web. Named after **Benoit Bliard** (Search & Go), whose training specialty is exactly this,
plus **Glen Cathey** (Boolean Black Belt) and **Irina Shamaeva** (Boolean Strings) for
supplementary technique.

`.claude/skills/Agent Bliard` in the workspace root is a symlink into this folder, same
pattern as `Irina LinkedIn Lite`/`Irina LinkedIn Recruiter` and `Vlastelica Intake Prep`.

## Why this exists, and what it doesn't replace

The Irina LinkedIn Lite/Recruiter skills already cover LinkedIn Boolean and X-ray in depth,
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

**Not found / stayed thin despite trying:** the nammooo Medium article ("Ingenious way to do
X-Ray Sourcing," claimed 50+ sites / 150+ URL patterns) — Medium blocks bots, no working mirror
found (freedium.cfd didn't resolve). Not load-bearing for the skill as shipped since the platform
list and query bank were independently corroborated elsewhere, but worth a manual read later if
Diane has Medium access herself — it may extend the platform-specific query bank further.

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

## Files

- `SKILL.md` — the skill definition Claude Code reads when this fires.
- `references/target-sites-and-operators.md` — the full operator table, Bliard's 4-step method,
  the platform-specific query bank (GitHub, Stack Overflow, Behance/Dribbble, Kaggle/ResearchGate,
  Xing, Meetup, Wellfound, Zendesk community, company team pages, resumes/CVs, conference
  attendee lists), the cross-functional techniques (Substack author-bio search, ADPList), and the
  "not X-ray targets" section (Slack/Discord, IEEE/ACM, Reddit, Handshake).
- `README.md` — this file.

`.claude/skills/Agent Bliard` in the workspace root is a symlink to this folder — that's what
Claude Code actually loads.
