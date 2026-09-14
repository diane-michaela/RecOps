# hiring_skills — Claude Code skills for sourcing & hiring

**Last updated:** 2026-09-14
**Owner:** Diane Rocher
**Type:** Claude Code skills (markdown, no framework/orchestration layer)

---

## What this is

Five Claude Code skills, each modeled on one real, named sourcing or hiring practitioner's
published work (exception on PRD): a book, transcripts from Youtube, a blog series, articles, a methodology — turned into a
reusable prompt that fires when the ask matches what it's good at.

**This is a shortcut, not a substitute.** Every skill here is a repackaging of public content a
real expert actually published, not original theory. Reading a skill's `SKILL.md` is not the same
as reading the book, watching the talk, or taking the course it's built from. If a skill's
guidance matters to a real hiring decision, go to the source it's named after — each folder's own
`README.md` links to it. Think of these as a small memo to help you get started, not a reason to
skip the real material.

## The five skills

<img width="735" height="917" alt="IMG_8181" src="https://github.com/user-attachments/assets/8d5abcb7-2b25-4e2f-96b2-c021fe89e8ac" />


### [PRD](./PRD) — Pierre-Richard DUPONT (Product Requirements Document)
Interviews you about a prompt, brief, or implementation-plan ask before you send it to an LLM —
catches a vague ask or an unverifiable spec before it turns into wasted work downstream. General
prompting discipline, not hiring-specific.

### [Vlastelica](./Vlastelica) — Intake Prep
Distilled from John Vlastelica's (CEO, Recruiting Toolbox) "Talent Advisor" framework. Fires
*before* an intake meeting happens, starting from just a JD — challenges the JD's untested
assumptions instead of transcribing it straight into hiring-manager questions.
Source: [Recruiting Toolbox](https://www.recruitingtoolbox.com/).

name: Vlastelica Intake Prep
description: 
  Prepares me for an intake meeting that hasn't happened yet, starting from just
  a JD. The JD is not the starting point, and never gets transcribed into questions...

Phase A - Challenge the JD (always run first)
Phase B - Homework to do before walking in
Phase C - Alignment questions to bring into the meeting

### [Fortin](./Fortin) — Market Mapping
Distilled from Pierre-André Fortin's (founder, Anara) published market-mapping method. Maps a
talent market — key employers, their ecosystem, how people move between them — before any
candidate-level sourcing starts.
Source: [Anara](https://anara.fr/).


name: Fortin Market Mapping
description: 
  Maps a talent market before any candidate-level sourcing starts. Named after
  Pierre-André Fortin, founder of Anara, whose published method is the direct source...

Phase A - Investigation: understand the sector before naming a single company
Phase B - Cartographie: map the companies and their ecosystem
Phase C - Flow Analysis: how people actually move between the mapped companies
Phase D - Choose the output: market picture or named-candidate handoff
Phase E - Talent Intelligence: package it as a decision-ready deliverable

### [Bliard](./Bliard) — X-Ray Search Beyond LinkedIn
Named after Benoit Bliard (Search & Go), supplemented by Glen Cathey (Boolean Black Belt) and
Irina Shamaeva (Boolean Strings). Builds Google X-ray search strings for sourcing outside
LinkedIn — GitHub, Stack Overflow, Behance, Kaggle, Meetup, company team pages, open-web resumes.

name: Agent Bliard
description: 
  Builds Google X-ray search strings for sourcing outside LinkedIn - GitHub,
  Stack Overflow, Behance, Kaggle, Meetup, company team pages, open-web resumes...

Phase A - Read the signals, then decide where to look
Phase B - Build the X-ray query for the chosen platform(s)
Phase C - Iterate and set realistic expectations

### [Irina](./Irina) — LinkedIn Boolean Search
Named after Irina Shamaeva, co-author (with David Galley) of *Advanced LinkedIn Search Techniques
for Recruiters*. Two tiers (Lite / Recruiter) turn a JD or intake brief into an advisor-first
LinkedIn Boolean search — tagging contradictions between the JD and the intake before ever
building a search string.

name: Irina (LinkedIn Recruiter Lite) - Sourcing Advisor
description: 
  Advisor first, builder second. Given a JD or intake notes, thinks out loud like
  an experienced sourcer before ever building a Boolean string...

Phase A - Advisory pass (always do this first)
Phase C - Further research angles (can fire before Phase B ever runs)
Phase B - Builder (only when explicitly asked for strings)

## Before you use one

- Each skill's own `README.md` has the full research trail: what was sourced from where, what
  turned out to be low-quality or unverifiable, what got corrected after live testing.
- These get corrected over time, not written once. If something looks wrong or outdated, that's
  expected — flag it rather than assuming the file is final.
- None of the named experts above reviewed or endorsed these skills. They're built *from* their
  public material, not *with* them.
