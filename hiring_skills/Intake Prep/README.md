# Intake Prep — Pre-Intake Kickoff Advisor

I love that guy! And the below would never replace YOU watching his videos. 
Here is a Claude Code skill, named after **John Vlastelica**, CEO of Recruiting Toolbox and originator of
the "Talent Advisor" framing of the recruiter role. Given a JD — before any intake meeting has
happened — it challenges the JD's assumptions, lists homework to pull beforehand, and drafts the
alignment questions to bring into the meeting, rather than mechanically turning JD bullets into a
question list.

A `.claude/skills/` symlink in the workspace root points into this folder, same pattern as the
other Claude Code skills in this repo.

## Why this exists, and what it doesn't replace

My workspace already has `Intake-Meeting-Automation/`, a Make.com pipeline:
- **V1** also goes JD → Claude-generated hiring-manager questions, but as a fire-and-forget
  automation triggered off a calendar event, with no advisory/challenge pass — it doesn't push
  back on the JD, just generates questions from it.
- **V2** runs *after* the intake meeting (triggered by the Gemini meeting-notes doc), extracting
  role data, building a sourcing brief, and merging a JD v2.

This skill sits interactively, before either of those: a manual, conversational pass for when
I want to actually think through a JD before the meeting exists on a calendar, or want a
second opinion before trusting V1's auto-generated questions. It does not touch sourcing strategy
(that's the LinkedIn Boolean Search / X-Ray Search Beyond LinkedIn skills) or anything post-meeting
(that's V2).

## Where this came from, and where it's thin

Distilled from John Vlastelica's Recruiting Toolbox material. Full bibliography (mostly youtube transcripts), access notes, and
extracted frameworks now live in the RecOps Obsidian wiki:
`john-vlastelica-talent-advisor-sources.md` (`LLM-wiki-vault/2026/wiki/insights/`) — that page is
the fuller writeup and source of truth if this README and the skill files ever drift, same pattern
as the LinkedIn Boolean Search skill's ebook note. It cross-links a pre-existing wiki page,
`influencing-hiring-managers-recruitingtoolbox.md`, covering Vlastelica's 4-step influencing
framework (Speed-Quality-Cost triangle, the 1-10-100 calibration rule, the "ass factor," pre-close
candidate-profile questions) — that framework is now folded directly into Phase C above.

Most of the original ~50-source list turned out to be **inaccessible** via automated fetching:
YouTube videos have no fetchable transcripts, and the go.recruitingtoolbox.com webinar/conference
pages are email-gated landing pages with no real content behind them for a fetch. Podcasts were
initially assumed dead/audio-only — that assumption was wrong for at least one (Ep 247,
recruitingfuture.com — the fetch failed, likely a JS-rendered page, but the transcript exists and
was retrieved manually; see the 2026-09-13 update below). What actually came through, and shaped
this skill:

- `recruitingtoolbox.com/stop-calling-it-an-intake/` (+ its ERE.net mirror) — the "intake is not a
  form" stance.
- `recruitingtoolbox.com/resources/how-to-be-a-talent-advisor/`,
  `recruitingtoolbox.com/what-is-a-talent-advisor/` — Talent Advisor vs. Transactional Recruiter
  framing.
- `recruitingtoolbox.com/recruiters-need-hiring-managers-to-step-up/`,
  `recruitingtoolbox.com/corporate-recruiters-who-is-your-customer/` (+ ERE mirror).
- `blog.recruitingtoolbox.com/blog/help-our-hiring-managers-move-from-known-to-unknown` — pedigree
  proxies vs. real evaluation rigor.
- `blog.recruitingtoolbox.com/blog/ready-fire-aim` — the alignment-before-sourcing point.
- `blog.recruitingtoolbox.com/blog/the-t-shaped-ta-leader`,
  `blog.recruitingtoolbox.com/blog/we-need-to-do-the-reps-to-get-better-as-talent-advisors`,
  `blog.recruitingtoolbox.com/blog/are-you-building-a-recruiting-machine`,
  `blog.recruitingtoolbox.com/blog/hold-still-while-i-talent-advise-you`,
  `blog.recruitingtoolbox.com/blog/the-5-biggest-lessons-i-learned-from-my-smartest-hiring-managers`
  — supporting material, not directly encoded into the skill's steps. (Corrected 2026-09-13: the
  "5 biggest lessons" post was actually read in the original research pass but got dropped from
  this list by mistake.)
- The **Hiring Manager Maturity Model** white paper — the one source that came through in full
  (found as a direct PDF, not via its gated landing page). Encoded in full in
  `references/hiring-manager-maturity-model.md`.

**Not found, despite being named directly in the source list**: the actual content of "Seven
Critical Conversations" (landing page names the session, but the seven conversations themselves
live behind a gated video/slide deck) and the Talent Advisor Diagnostic Tool's actual questions
(landing page only). If either surfaces later (a transcript, a shared PDF), it likely strengthens
Phase C and is worth folding in.

**Update 2026-09-13**: confirmed no transcript/captions tool exists in this environment — YouTube
stays unreadable by default. I manually pasted the transcript for one video ("How to be a
strategic talent acquisition pro," Talent Connect 2019), which added the time-in-stage benchmarking
note (Phase B), the panel-size/false-negatives point and the cost-of-vacancy conversation opener
(both Phase C). She then pasted three podcast transcripts (SoundCloud's "How to Engage Hiring
Managers," How I Hire's Amazon Bar Raiser episode, and Recruiting Future Ep 247), which further
enriched Phase C: the "employees vs. plan" progress-metric framing (success-criteria bullet), the
Bar Raiser/false-positive counterpart to the panel-size point, and more named terms
(seniority/passion/potential, alongside culture fit and the ass factor) in the vague-quality-
language bullet. Full summaries and the remaining unread list in
`john-vlastelica-talent-advisor-sources.md` (RecOps wiki).

**Update 2026-09-13 (second)**: 
- pip install youtube-transcript-api helped to fetch youtube transcript with no manual effort
- I added a first-party source alongside Vlastelica's material — my
own "Intake Meeting: 45-Minute Playbook" (my personal Notion template), saved in full at
`references/intake-meeting-playbook.md`. Comparing it against the skill surfaced real gaps: team/
culture-fit questions, process logistics (start date, rounds/speed, who has final call, internal
candidates already in the mix), and a closing section (pitch, likely objections, a catch-all "what
haven't I asked") were all missing and are now in Phase C. The playbook's function-specific
sub-questions (§4) — including PhantomBuster-specific squad/PB2-vs-PBAI/IC-level questions for
tech/product/revenue roles — are now pulled into the padded-requirement-testing bullet when
relevant. Its Sourcing section (§8) was deliberately left out of the skill — that's LinkedIn
Boolean Search / X-Ray Search Beyond LinkedIn / Market Mapping territory.

## Files

- `SKILL.md` — the skill definition Claude Code reads when this fires.
- `references/hiring-manager-maturity-model.md` — full 4-stage model + diagnostic, used by Phase
  C's optional HM-calibration step.
- `references/intake-meeting-playbook.md` — Diane's own intake-meeting template, first-party
  source, re-fetch from Notion if it's ever updated there.
- `README.md` — this file.

A `.claude/skills/` symlink in the workspace root points to this folder — that's what Claude Code
actually loads.
