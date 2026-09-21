# Market Mapping — Cartographier un marché

Bonjour bonjour! and welcome to my space :)
Here is a Claude Code skill for mapping a talent market (key employers, their ecosystem, and how people
move between them) **before** candidate-level sourcing starts. Named after **Pierre-André Fortin**,
founder of **Anara** (Paris headhunting cabinet, est. 2018), whose published method is the direct
source.

A `.claude/skills/` symlink in the workspace root points into this folder, same pattern as the
other Claude Code skills in this repo.

## Why this exists, and what it doesn't replace

LinkedIn Boolean Search and X-Ray Search Beyond LinkedIn both assume you already know who/what
you're searching for — they turn a target profile into a boolean or X-ray string. Market mapping
is the layer *before* that: figuring out which companies even have the people you want, and how
talent moves between them, so the sourcing plan starts from evidence instead of a guessed
competitor list. This skill produces a company list and a market/flow read; it hands off to
LinkedIn Boolean Search or X-Ray Search Beyond LinkedIn once it's time to build an actual search
query, rather than duplicating that.

## Research process and source quality

**Pass 1 — broad landscape (English + French podcasts, articles, people).** Turned up the general
talent-mapping/market-mapping content ecosystem: Matt Alder (*Recruiting Future*), Johnny Campbell
(SocialTalent, *Hiring Excellence*), Glen Cathey/Irina Shamaeva/Shally Steckerl (sourcing-community
names already covered by the X-Ray Search Beyond LinkedIn skill), and French podcasts (*Entre recruteurs*, *Le
Meilleur du Recrutement*, *Tam Tam*, *Le Barbu qui parle RH*, *Dear Talent*). None of these turned
out to be primary methodology sources for market mapping specifically — mostly general recruiting/
sourcing content that touches the topic in passing.

**Pass 2 — resolving Anara and pulling the actual methodology.** Once anara.fr was confirmed as the
real source, fetched Fortin's own article
([Market Mapping : Révéler les Talents Invisibles](https://anara.fr/market-mapping-reveler-les-talents-invisibles/))
and training page ([Formation Market Mapping](https://anara.fr/formation-market-mapping/)) directly
— this is genuine first-party teaching content (the 4-phase method, the "Fifth Element" technique,
the Veeva/pharma case study with real before/after numbers), not a bio or marketing page. This is
now the skill's backbone.

**Pass 3 — cross-referencing English-language material for a fuller picture.**

Pierre-André ib a Master when it comes to Market Mapping but it was important to crosscheck with other papers, articles from others to make my skill more robust. 

- **SocialTalent glossary** ([Market Mapping](https://www.socialtalent.com/glossary/market-mapping),
  [Talent Mapping](https://www.socialtalent.com/glossary/talent-mapping)) — the clearest available
  statement of the market-vs-talent-mapping distinction (aggregate picture vs. named-candidate
  list), including the four-dimension framework (supply/demand/compensation/competitive dynamics).
  Credible: part of a paid, established sourcing-training curriculum (Licensed Master Sourcer), not
  a marketing funnel.
- **Toby Culshaw**, book *Talent Intelligence* (Kogan Page, 2022) + *Talent Intelligence Collective
  Podcast* — the closest English-language canonical text on the discipline as a whole. Broader
  scope than sourcing alone (workforce planning, business framing) — used here for the
  "decision-ready deliverable" framing in Phase E, not for tactical technique.
- **Stratigens** (Alison Ettridge, acquired by Lightcast 2024) — a genuine labor-market-data vendor
  in this space, cited for the concept, not mined for proprietary technique (their actual method is
  behind a paid data platform).
- **SourceCon archive** — practitioner-community talks on talent mapping (Natalya Kazim among
  contributors); corroborates that this is an established sourcing-community topic, not just an
  Anara-specific framing.
- **Intellerati / The Good Search** (executive search research lab) — the older retained-search
  "name generation" tradition (org-chart building, verified via press releases/filings, inferred
  from title levels). Genuinely different lineage from the sourcing-community material above —
  included as an alternate Cartographie technique for when target companies are already named,
  rather than folded into Fortin's method as if it were the same thing.

  Hopefully, that skill will continue to get more robustness by me adding articles and new upcoming roles will help me to test and enrich that skill. It doesn't replace that French dude master peaces you will find in his website and through LinkedIn articles/ contents. 

**Flagged as low original value, not used as a source:** a cluster of near-identical "Market
Mapping 101 / 5 steps" SEO articles (QX Global Group, MightyRecruiter, Floodgate Medical, Venn,
Beeskneeshire, Loxo, Recruiterflow, Multirecruit) that repeat the same generic step list almost
verbatim across sites — the same pattern the X-Ray Search Beyond LinkedIn research flagged in
HR-SaaS glossary boilerplate (Asanify/Taggd/Qandle). Useful only as confirmation that "market
mapping" is a widely-recognized term, not as methodology. Also flagged: the YouTube video *"Market
Mapping Secrets TOP Recruiters Use to Find Hidden Talent"* is sponsored content for a
market-mapping SaaS tool (MarketMapr/RecMapper) — watchable for technique ideas, treated as vendor
marketing rather than methodology authority, same caveat the X-Ray Search Beyond LinkedIn research
applied to Pin.com/Lessie.ai.

## Pass 4 — 2026 YouTube sourcing-automation sweep (2026-09-21)

Not new methodology research on its own — a background research agent verified upload dates and
screened ~340 videos across 8 sourcing topics for 2026-published, technique-bearing content (same
sweep that contributed to the X-Ray Search Beyond LinkedIn skill). Three videos corroborated and
sharpened this skill rather than changing its structure:

- **Metaview — [The Talent Map Method: Finding Talent Everyone Else Misses](https://www.youtube.com/watch?v=CaOD-cLODH8)**
  (2026-07-29, 58-min webinar). Frames market mapping as three lenses — competitor landscape,
  talent density, ICP calibration — landing on the same shape as Fortin's method independently.
  Source for the new ICP-calibration step added to Phase A.
- **Recruise — [How GCC Hiring Works: Building a Talent Availability Map](https://www.youtube.com/watch?v=bBaWri_7wWo)**
  (2026-05-27). A 5-step framework with a real worked case (40 roles wanted vs. ~15 people
  in-market). Source for stating supply/demand as an explicit gap number in Phase D's output,
  added as a second worked example in `references/market-mapping-method.md`.
- **Talent Sourcer AI — [AI for market mapping with Claude, Codex, and ChatGPT](https://www.youtube.com/watch?v=EnBhUFut1sQ)**
  (2026-07-02, 31-min webinar). Hands-on build of a company/market map using an LLM plus a
  web-search tool in ~30 minutes. Confirms the method is executable in a single Claude session
  rather than requiring dedicated market-intelligence software — validated the existing approach,
  didn't change it.

All three are independent corroboration of Fortin's structure, not a competing method — the two
content changes (ICP calibration, gap framing) make explicit two things Fortin's own material and
the SocialTalent four-dimension framework already assumed but didn't spell out as
deliverable-shaping steps.

## Files

- `SKILL.md` — the skill definition Claude Code reads when this fires.
- `references/market-mapping-method.md` — Fortin's 4-phase method, the Veeva worked example, his
  training curriculum, SocialTalent's market-vs-talent-mapping distinction and four dimensions, the
  executive-search name-generation technique, realistic expectations, and a further-reading list.
- `README.md` — this file.

A `.claude/skills/` symlink in the workspace root points to this folder — that's what Claude Code
actually loads.
