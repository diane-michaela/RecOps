# LinkedIn Boolean Search Skill

A Claude Code skill, named after **Irina Shamaeva**, co-author of *Advanced LinkedIn Search
Techniques for Recruiters* (Shamaeva & Galley, Brain Gain Recruiting, 2024). **Advisor first,
Boolean-string builder second**: given a JD or intake-meeting brief, she leads with the
principles, cross-source contradictions, and judgment calls that matter for that specific role —
Boolean strings only get built once asked, as a separate step afterward.

Two account-tier-specific skills, both living here as the canonical source:

- **`Irina LinkedIn Lite/`** — tuned for Diane's own account (LinkedIn Recruiter Lite). No bulk
  CSV import, no character-limit cap to work around.
- **`Irina LinkedIn Recruiter/`** — for full LinkedIn Recruiter access (a teammate's account, or a
  future upgrade). Adds bulk CSV import and the native military-veteran filter.

Each subfolder is a complete skill (`SKILL.md` + its own `references/operators-cheatsheet.md`).
`.claude/skills/Irina LinkedIn Lite` and `.claude/skills/Irina LinkedIn Recruiter`
in the workspace root are **symlinks into this folder** — same pattern as `~/.claude/skills/PRD`
symlinking to `PRD/`. Edit the skill here; the symlink is what
makes it auto-trigger inside any Claude Code session in this workspace.

## What she does

Given a JD, intake notes, or both, she runs two phases:

**Phase A — Advisory pass (default, always runs first):**
1. Flags **contradictions between sources** — e.g. a JD requirement that the actual intake
   conversation explicitly downgraded or reinforced — quoting both sides and naming which one she'd
   lean toward and why, rather than silently picking one.
2. Names **unfilterable asks** — things LinkedIn Boolean search structurally cannot verify
   ("2-3 years in a specific sub-skill," soft skills, licensure) — and how each actually gets
   confirmed instead (an interview question, a portfolio read). For a "high performer" ask
   specifically, offers achievement keywords (`award OR winner OR "president's club"...`) as a
   partial proxy — free-text only, not LinkedIn's unindexed Honors & Awards field.
3. Flags **calculated-filter temptations** — where the brief's language (seniority, company size,
   department) would tempt the Seniority/Function/Company-size/-type selections, which hide
   50–80% of otherwise-matching profiles.
4. Names which **hidden operators** actually help this specific brief, not a rote list.
5. Notes if the role sits in a **fast-moving/self-titled space** where Keywords-field text matters
   more than Job-titles-field matching.
6. Surfaces **indirect-search opportunities** (feeder companies, external sources) if a
   keyword-only approach would under-cover the ask.
7. Ends with **open questions** for you, and states plainly that nothing so far is a Boolean
   string yet.

**Phase B — Builder (only when you explicitly ask for strings), building on Phase A's actual
decisions, not re-derived assumptions:**
1. Drafts a **targeted** (AND-heavy) and an **open-ended** (broad OR + NOT-exclusions) variant.
2. For an oversized result set, offers **concentric-circle NOT-stacking** (peel off one desired
   term per pass) or a **bottom-to-top** review order as additional levers, not just a narrower
   Boolean.
3. Layers in only the hidden operators Phase A flagged as relevant.
4. Labels every string with exactly which field to paste it into (Job titles / Company /
   Keywords).

## How to use it

Paste a JD or intake notes into a Claude Code session in this workspace — the matching skill
(Lite or Recruiter, based on which account is in play) triggers automatically and leads with the
advisory pass. To be explicit:

```
Use the Irina LinkedIn Lite skill on this JD:
[paste]
```

When you're ready for actual search strings, say so explicitly (e.g. "build the strings now,
using X for the AWS question") — that's what moves her into Phase B.

Optional add-ons, just ask: a diversity-sourcing keyword layer (including Greek-letter/
affinity-org OR-strings), or — if the role isn't findable on LinkedIn alone (redacted profile
fields, niche licensure) — the external-source cross-reference workflow described below.

## Where this came from

Distilled from *Advanced LinkedIn Search Techniques for Recruiters*. Full reading notes:
`linkedin-advanced-search-techniques-ebook.md` in the RecOps Obsidian wiki
(`LLM-wiki-vault/2026/wiki/insights/`). That page is the fuller writeup and source of truth if
this README and the skill files ever drift.

---

## All the data

### Hidden operators (Recruiter / Recruiter Lite — confirmed on both)

Format `<operator>:<value>`, entered in the **Job Title** or **Company** field only.

| Operator | Searches | Values | LinkedIn-calculated (missing-data risk)? |
|---|---|---|---|
| `headline:` | keywords in headline | text | no |
| `summary:` | keywords in About | text | no |
| `skills:` | **self-entered only** skills | text | no |
| `spokenlanguage:` | language proficiency | text | no |
| `startyear:` / `endyear:` | school attendance years | year | no |
| `industry:` | industry | Industry Codes | no |
| `companytype:` | company type | see below | no |
| `companysize:` | company size | see below | **yes** |
| `seniority:` | seniority | see below | **yes** |
| `profilelanguage:` | profile UI language | 2-letter code | no |
| `functions:` | job function | see below | **yes** |
| `yoe:` / `yoecc:` / `yoepos:` | years of experience / at current co / in position | 0–100 | **yes** |
| `fieldsofstudy:` | field of study | FoS codes | no |
| `schoolid:` | specific school | school codes | no |

Combo examples: `headline:"open to work" OR headline:looking`, `summary:managed summary:budget
summary:teams`, `functions:11 functions:12` (Healthcare + HR), `NOT seniority:5` (exclude
Managers), `financial NOT industry:43` (keyword without the industry).

**`skills:` vs. the Skills-and-Assessments dialog filter are not the same search.** LinkedIn
"infers" skills for the dialog filter from resume text, whole-profile text, and even
connections' skills — confirmed directly by LinkedIn Engineering to the book's authors. That
filter matches ~20%+ more profiles than the ones with an actual keyword hit, including people
with zero self-entered skills. Default to `skills:` for precision.

### Why to avoid calculated-filter selections as a primary cut

Activating any of these — via the dialog OR the corresponding hidden operator — hides a large,
inconsistent share of otherwise-matching profiles, because LinkedIn frequently fails to assign
the value even when the underlying data is on the profile:

- No company size assigned: ~78% of profiles
- No company type assigned: ~72%
- No seniority assigned: ~52%
- No function assigned: ~58%

Stacking two or more of these selections can cut a result set to ~15% of the true matching
population. Prefer text/title-synonym search over these selections; use them only as an
explicitly-flagged coarse pre-filter on an oversized result set, never silently.

Two related traps:
- **Unclosed "Present" positions** inflate company/title headcounts — members who forget to
  close an old role get matched on every "current" job they've ever listed.
- **Company-selection search misses real employees** even with an unambiguous company on the
  profile — text search for the company name catches people the selection filter drops.

### Boolean character-limit workaround (Premium/Basic accounts only — not Recruiter or Lite)

Premium/Basic caps around 5–7 total `AND`/`OR`/`NOT` operators per query, failing silently with
"no results found." **Neither Recruiter nor Recruiter Lite has this cap.** Fix, if ever needed on
a Premium/Basic account: after each operator, open a parenthesis right after it, close it after
the term it governs:

```
Mary OR Emma OR Sophia OR Linda        →   Mary OR(Emma) OR(Sophia) OR(Linda)
(Walmart OR Amazon OR Apple)           →   (Walmart OR(Amazon) OR(Apple))
```

Same pattern for `AND(...)` / `NOT(...)`.

### Code tables

**Company size** (`companysize:X`, capitalize the letter): A=1, B=2-10, C=11-50, D=51-200,
E=201-500, F=501-1000, G=1001-5000, H=5001-10000, I=10000+

**Company type** (`companytype:X`): C=Public, D=Educational, E=Self-Employed, G=Government,
N=Non-Profit, O=Self Owned, P=Privately Held, S=Partnership

**Seniority** (`seniority:N`): 1=Unpaid, 2=Training, 3=Entry, 4=Senior, 5=Manager, 6=Director,
7=VP, 8=CxO, 9=Partner, 10=Owner

**Job function** (`functions:N`): 1=Accounting, 2=Administrative, 3=Arts&Design, 4=BizDev,
5=Community/Social Services, 6=Consulting, 7=Education, 8=Engineering, 9=Entrepreneurship,
10=Finance, 11=Healthcare, 12=HR, 13=IT, 14=Legal, 15=Marketing, 16=Media/Comms,
17=Military/Protective Services, 18=Operations, 19=Product Mgmt, 20=Program/Project Mgmt,
21=Purchasing, 22=QA, 23=Real Estate, 24=Research, 25=Sales, 26=Customer Success/Support

### Diversity-sourcing keyword patterns (no native LinkedIn filters exist, except one)

All of these are indirect keyword heuristics, best combined, never a certainty about any one
profile:

- **Self-identified women**: pronoun-taggers commonly put `she/her` in the **Last Name** field
  (search `she AND(her OR(hers) OR(they))` as last name); an OR-string of common US female first
  names covers roughly half of US women members; women-only colleges as an OR-string (expect some
  false positives — several now admit men); women-centered associations (e.g. WITI); non-English
  profiles may need a gendered job-title variant (German `managerin` for a female manager).
- **Hispanic/Latino surnames**: OR-string of common Hispanic surnames (Garcia, Rodriguez,
  Martinez, Hernandez, ...) — pair with a Spanish-language cue to cut false positives, since many
  of these surnames aren't exclusively Hispanic.
- **HBCU / PBI / HSI / AANAPISI / ANNH / TCU** school-name OR-strings, or LinkedIn's per-school
  Alumni Search tool directly (supports skill filtering).
- **Affinity/professional associations** as keywords: e.g. `NABJ OR "National Association of
  Black Journalists"`, `"national society of hispanic mbas" OR NSHMBA OR prospanica`.
- **Military/veteran**: the one native diversity filter LinkedIn actually offers, in full
  Recruiter only. On Lite, fall back to an exhaustive OR-string of US Army/Navy/Air Force/
  Marines/Coast Guard/National Guard plus common abbreviations.
- **`she her "verified achievement"`** (Post Search, not profile search) — catches self-identified
  women who just had Credly auto-post a new certification, often before it's added to their
  profile at all.
- **General indirect-search pattern**, reusable beyond diversity: when the target credential/trait
  isn't stated on profiles (security clearance, a niche license), search what correlates instead
  — cleared-employer names, licensing-school lists, expat patterns (school in country A + location
  in country B).

### X-Ray after the 2024 public-profile redaction

Since early 2024, public (signed-out, Google-indexed) LinkedIn profiles no longer expose current
job title, headline, most of About, Experience, or Education, regardless of the member's own
privacy settings. `site:linkedin.com/in intitle:"company" "location"` style X-Ray now reliably
yields only **current company + location** — everything else needs enrichment after the fact:

1. X-Ray on what's still exposed (company + location; job title/skills sometimes leak via
   "People also viewed").
2. Bulk-scrape the result URLs.
3. Bulk-upload those URLs into a contact-finder (SalesQL / SeekOut / Phantombuster) for full
   profile + contact enrichment.
4. Filter the enriched spreadsheet, confirm remaining candidates on LinkedIn directly.

### Mini-People Aggregator (cross-referencing an external source into LinkedIn)

For roles where LinkedIn's own keyword search won't find the credential (niche licensure,
GitHub-native skills, association-only membership):

1. Find the external source: license registry, GitHub `language:`/`location:` search,
   association member directory, or a `filetype:xlsx`/`filetype:pdf` contact-list Google dork.
2. Collect identifiers — email or profile URL = guaranteed match; name-only = narrow with
   location/industry to compensate for ambiguity.
3. Cross-reference:
   - **Full Recruiter**: **Project Settings → Bulk importing**, a 3-column CSV (first name,
     last name, email — placeholders like `a`/`b` are fine for the name columns, since a matched
     profile's real name overrides them, and an unmatched row keeping the placeholder *is* the
     "no match" signal).
   - **Recruiter Lite** (no native bulk import): bulk-upload the list into a third-party
     contact-enrichment tool instead (SalesQL / ContactOut / SeekOut all accept bulk profile-URL
     or email upload), or — for small batches — search each person by exact first + last name,
     which reveals a full out-of-network profile regardless of account tier.
4. Filter matched profiles, message referencing the actual source ("saw your GitHub, mostly
   Ruby") rather than a generic opener — and note that competitors sourcing the same role purely
   on LinkedIn won't have found these people either. Existing workspace tooling to reuse rather
   than rebuild: `github_extraction/lisp.py` for the GitHub half, or the PhantomBuster pipeline
   for enrichment.

### Additional sourcing hacks (from Irina Shamaeva's Boolean Strings blog — beyond the book)

The book (Oct 2024) doesn't cover everything on her blog, booleanstrings.com. Checked directly
against the book — these four add real value beyond it:

- **Target past roles, not just current ones**: search Keywords for `"[Past Title] at [Past
  Company]"`, exclude current employees of that company via `NOT`/"Doesn't have" on Company
  (not the title) — surfaces people with that exact past-role history who've since moved on.
  Combine multiple past-role signals ("two pairs": past role at Company A + past role at Company
  B) when one employer alone isn't distinctive enough.
- **Company-size workaround**, for when size genuinely must be a hard filter: Google `"51-200
  employees" site:linkedin.com/company "location" "industry"`, switch to Images, filter to
  ~200×200px results (LinkedIn's logo size) to isolate matching company logos, reverse-image-
  search each logo, then X-ray its employees. Fragile/manual — last resort only. Same trick works
  for school-alumni X-raying.
- **Bulk email→LinkedIn-URL tools**: add **Clearbit** to the SalesQL/ContactOut/SeekOut list. For
  **Recruiter Lite specifically**, check the free option first — a colleague with full Recruiter
  can add you as a **Hiring Manager** on one of their Projects, which includes bulk email upload
  at no cost to either side, before reaching for a paid tool.
- **GitHub via Google X-Ray**: `site:github.com inurl:tab=repositories <language> <technology>`
  as an alternative to GitHub's own search API. Drop redundant terms a technology already implies
  (`Java` alone covers backend; skip `backend OR server`). GitHub removed public emails from
  profiles, so the classic email-discovery variant of this X-ray no longer works — pair with the
  Mini-People Aggregator's bulk-enrichment step instead.
- **Don't trust LinkedIn's own "Collaborative Articles" AI** for sourcing guidance — it sometimes
  generates tangential or flatly wrong content on Boolean/sourcing topics.

### Additional sourcing hacks (from Glen Cathey / Boolean Black Belt — beyond the book)

Checked against the book directly (Sept 2026), including Cathey's original 2014 Talent Connect
London deck ("Become a LinkedIn Search Ninja," recovered via its SlideShare mirror since the
YouTube upload has no transcript) and a 2017 LinkedIn Talent Solutions blog post that repackaged
the same 2014 material. Three techniques are genuinely additive; two are already covered above
under different names; one was checked and rejected:

- **Search bottom-to-top, not just top-down**: LinkedIn's ranking surfaces the same "easy to
  find" candidates to every recruiter running a similar search — paging to the back of a large
  result set surfaces people competitors never reach.
- **Concentric-circle NOT-stacking** ("Probabilistic Search," Cathey's own term, 2014): for one
  required criterion plus several desired ones, run the full AND first, then peel off one desired
  term per pass (`...AND NOT Q5`, then `...AND NOT Q4 AND NOT Q5`, etc.) so each pass returns a
  fresh, non-overlapping batch instead of re-surfacing the same top matches.
- **Achievement/high-performer keywords** (`award OR winner OR "president's club" OR "top
  producer" OR ranked OR exceeded`) as a proxy for high performers, independent of title/skill
  match. Caveat: this only catches free-text mentions in About/Experience — it does **not**
  retrieve LinkedIn's structured Honors & Awards section, which the book confirms is never
  indexed. Don't present it as "searching someone's awards."
- **Greek-letter/affinity-org OR-strings**, extending the book's diversity chapter (which covers
  HBCU/PBI/HSI/AANAPISI/ANNH/TCU lists, women's colleges, and NABJ/NSHMBA-style associations) with
  sororities, historically Black fraternities, Latino Greek orgs, Asian-American fraternities, and
  LGBTQ+ campus orgs as their own category. Same false-positive caveat as women's colleges.
- **Already covered, different name**: Cathey's "dark matter" candidates (people who skip the
  expected terminology) is the same mechanic as this skill's Targeted/Open-ended split, just
  named differently — he coined it in the 2014 talk; the 2017 LinkedIn blog post repackaged it
  without crediting the original.
- **Checked and rejected**: "target text-poor/incomplete profiles" (2017 blog claim that sparse
  profiles belong to selectively-private high performers) — anecdotal, and cuts against the
  book's own finding that sparse profiles are usually just stale or abandoned, not deliberate.

### Additional sourcing hacks (from a second, untitled Glen Cathey talk transcript — beyond the 2014 deck)

Diane pasted a separate, longer conference-talk transcript directly (title/venue/date unconfirmed,
no source URL given) — distinct from the 2014 "Search Ninja" deck above. It cuts off mid-way
through the diversity-sourcing section (50,000-character paste limit), so this list reflects only
what's confirmed from the surviving text; the "5 levels of talent mining" framework it references
and the tail end of the diversity methodology aren't documented anywhere here because the
transcript never reached them.

- **Iterative search** ("candlelight → flashlight → floodlight"): search a single seed term, read
  10-15 results for terms that are *not* highlighted but clearly related, fold those into a
  broader OR-string, repeat. Counterintuitively broadens the result set each round rather than
  narrowing it, since each pass adds a genuine synonym rather than a stricter filter.
- **Implicit search via employer inference**: search for people who *do* state a skill under a
  given title, collect the companies they work at, then search that same title at those companies
  with the skill keyword dropped — infers the skill from employer context for people who never
  wrote it down themselves. Now built into Phase B of both skill variants as its own named
  technique (see their `SKILL.md`/cheatsheet).
- **Strategic exclusion**: deliberately search a title/keyword cluster while dropping the single
  "obvious" required term (his example: software-engineer titles minus "Java") to surface people
  who under-describe their own stack, sometimes on purpose. Also now in both skills' Phase B.
- **`^p` → `" OR "` Word find-and-replace trick**: paste a spreadsheet column (companies, schools,
  names) into Word, find-and-replace the paragraph mark for `" OR "`, fix the two ends by hand —
  turns a long list into a Boolean OR-string in seconds without typing it out. Purely mechanical,
  useful regardless of account tier.
- **Pronoun search in Recommendations text, not the Last Name field**: distinct from this skill's
  existing "she/her self-tagged in Last Name" convention (above) — Cathey's version searches
  Keywords for `her`/`she`, on the logic that only a colleague *writing a recommendation about* a
  woman would use those pronouns, catching self-identified women who never tagged their own name.
  Older/blunter than the Last Name convention (more false positives from any profile mentioning
  "her"/"she" in any context) but a genuinely different mechanism worth keeping alongside it, not
  instead of it.
- **Talent mapping as a stated deliverable**: when a search returns hundreds of results you can't
  fully review today, frame working through all of them over weeks/months as a real deliverable to
  the hiring manager ("mapped all 600, took two months, now I know the full pool") rather than
  silently discarding everyone past the first screen. Same root problem as this skill's
  concentric-circle/bottom-to-top techniques, framed as a process/expectations point instead of a
  search mechanic.
- **Not yet incorporated — needs the rest of the transcript**: the "five levels of talent mining"
  framework (named but never explained before the transcript cuts off) and the full first-name-list
  methodology for gender-diversity sourcing (top-100-names-by-decade compiled via census/SSA data,
  claimed ~67% coverage of UK women) — don't treat either as documented until the missing text
  arrives.

## Files

- `Irina LinkedIn Lite/SKILL.md` — the Recruiter Lite skill definition (frontmatter + operating
  instructions Claude Code reads when this skill fires), plus its own
  `references/operators-cheatsheet.md`.
- `Irina LinkedIn Recruiter/SKILL.md` — the full-Recruiter skill definition, same structure.
- `README.md` — this file.

`.claude/skills/Irina LinkedIn Lite` and `.claude/skills/Irina LinkedIn Recruiter` in the
workspace root are symlinks to the two subfolders above — that's what Claude Code actually
loads.
