---
name: Vlastelica Intake Prep
description: Prepares Diane for an intake/kickoff meeting with a hiring manager that hasn't happened yet, starting from just a JD (no meeting notes exist at this point — that's the whole premise). Distilled from John Vlastelica's (CEO, Recruiting Toolbox) "Talent Advisor" framework, whose core stance is that the JD is not the starting point and should not be transcribed into questions — the recruiter is expected to arrive with homework already done (source-of-hire data, time-to-fill benchmarks, a draft target-candidate profile) and to challenge the JD's untested assumptions rather than take its requirements at face value. Output is three buckets: JD challenges, homework to do before the meeting, and alignment questions to bring into the meeting itself — never a straight JD-to-questions transcription. Use when Diane says things like "help me prep for this intake meeting," "I have a JD, what should I ask this hiring manager," or "sanity-check this JD before I meet the HM." Complements rather than duplicates two other things in this workspace: the `Intake-Meeting-Automation/` V1 Make scenario (which also turns a JD into HM questions, but as a fire-and-forget automation, not an interactive advisory pass) and the Irina LinkedIn skills (which advise on sourcing/Boolean search, not on the hiring-manager conversation) — if the ask is about sourcing strategy or a Boolean string, defer to Irina instead.
---

# Vlastelica Intake Prep — Pre-Intake Kickoff Advisor

Named after John Vlastelica, CEO of Recruiting Toolbox and originator of the "Talent Advisor"
framing of the recruiter role. This skill only covers the moment **before** an intake meeting
happens — the input is a JD (and maybe a role title, level, or one-line context from Diane), not
meeting notes. There are no meeting notes yet; that is the entire point of this skill. Once the
meeting has actually happened, the existing `Intake-Meeting-Automation/` V2 Make scenario takes
over (role extraction from the Gemini notes, sourcing brief, JD v2) — this skill doesn't touch
that side.

## The stance this skill enforces

Vlastelica's material is consistent on one point that shapes everything below: **the JD is not
the starting point, and an intake meeting is not "turn the JD into questions."** His own framing —
asking a hiring manager "where do you think we'd find this talent?" without having already done
homework is "so 2003." A recruiter operating as a Talent Advisor (vs. an order-taking
Transactional Recruiter) shows up with a draft plan and challenges the JD's assumptions, rather
than transcribing it into a checklist. Concretely, that means:

- Don't just reformat JD bullets into "tell me more about X" questions — that's exactly the
  order-taker behavior this skill exists to avoid.
- Some homework (source-of-hire, benchmarks, a draft candidate profile) belongs in Diane's prep
  *before* the meeting, not as questions asked *during* it.
- The biggest single time-waster in a hiring funnel is misalignment discovered too late (his
  "Ready-Aim-Fire" point) — so the questions that do get asked should target exactly the
  assumptions most likely to be wrong or untested, not generic coverage of the JD.

This skill also draws on a second source: Diane's own working template,
`references/intake-meeting-playbook.md` ("Intake Meeting: 45-Minute Playbook," her personal Notion
doc) — a first-party source, not Vlastelica material. Where the two agree, treat it as
corroboration. Where the playbook covers something Vlastelica's material doesn't (team/culture fit,
process logistics, closing the conversation), that content is folded into Phase C below. Its
Sourcing section (#8) is deliberately *not* folded in — that's Irina/Bliard/Fortin territory, not a
hiring-manager-alignment question.

## Phase A — Challenge the JD (always run first)

Read the JD (and whatever else Diane gives — role title, level, team, prior similar JDs) and
produce a short challenge pass. Skip a section if it's genuinely empty rather than padding it.

1. **Padded or untested "must-haves."** For every requirement that reads like a proxy credential
   rather than a predictor of success (a specific pedigree school/company, an arbitrary years-of-
   experience number, a long tool list) ask out loud: is this actually predictive, or just
   trainable/nice-to-have dressed up as mandatory? Name each one specifically — don't issue a
   blanket "some of these might be soft" disclaimer.
2. **Stale or boilerplate language.** Flag sections that read like they were copy-pasted from a
   template or a previous req and likely don't reflect this specific need (generic "fast-paced
   environment" filler, a responsibilities list that doesn't obviously map to an actual team gap).
3. **The business problem behind the role.** Check whether the JD names an actual outcome/problem
   ("we're losing deals because implementation takes too long") or only a task/skill list. If it's
   only the latter, that gap becomes the single most important question for Phase C — the JD
   alone cannot answer it. The playbook's own framing is a good test to apply here: could Diane
   explain this role to a friend at dinner using only what's in the JD? If not, name specifically
   what's missing — that's usually the part of the job that never makes it onto a JD at all.
4. **If a prior JD version, intake-automation output, or informal notes are also given** (this
   will be rare, since this skill fires pre-meeting), tag each requirement reinforced / downgraded
   / untouched the way the Irina skills do for JD-vs-intake contradictions — don't silently bucket
   a requirement that was never actually revisited as if it were confirmed.

## Phase B — Homework to do before walking in

List concretely what to pull **before** the meeting, not questions to ask in it. Point at where in
this workspace each item actually comes from rather than leaving it generic:

- **Source-of-hire for comparable past roles** — where similar hires actually came from (referral,
  sourced, inbound), pulled from TeamTailor data (`Teamtailor_quaterly_extraction/` or a live query
  against the Candidate Index) rather than guessed.
- **Time-to-fill benchmark** for this role's function/level, same source — and where possible, a
  time-*in-stage* breakdown (not just the aggregate number), so it's clear which specific stage
  historically eats the time, rather than a single undifferentiated figure.
- **Where this req sits relative to the "real" clock.** Recruiters and hiring managers tend to
  start the time-to-fill clock on different days — the recruiter from req approval, the HM from
  whenever the actual need arose (a resignation, a headcount conversation). If there's a known,
  predictable pattern behind this opening (seasonal turnover, a post-bonus exit wave), note it as
  a reason this req should arguably have opened earlier — worth naming, not just accepting the
  clock start date as given.
- **A draft target-candidate profile** — a first-pass sketch (not a blank slate) of who this role
  probably targets, based on comparable current team members or past successful hires. This is
  the natural handoff point to the Irina LinkedIn skills if Diane wants an actual sourcing/Boolean
  pass built from that draft — flag it as an option, don't build it here.
- **Comp/leveling context**, if available, so the meeting isn't the first time a mismatch between
  the JD's ask and the budgeted level surfaces.

Be explicit that this bucket is Diane's prep work, distinct from Phase C's in-meeting questions —
don't blur the two into one list.

## Phase C — Alignment questions to bring into the meeting

Questions should target the specific gaps and assumptions Phase A surfaced, not generic JD
coverage. Each bullet below is one idea — don't merge several into one point when relaying these to
Diane; a fast pre-meeting checklist beats a paragraph to study.

**Always relevant:**

- **Success criteria beyond the JD** — what does great look like at 6 months, what's the cost of
  a bad hire in this seat, what would make you pass on someone who looks strong on paper.
- **Direct tests of each padded/untested requirement from Phase A** — ask the HM straight out
  whether it's trainable or truly non-negotiable, rather than silently deciding for them. When the
  role matches a function covered in `references/intake-meeting-playbook.md` §4 (tech, product,
  revenue/growth/marketing/customer enablement), pull that function's specific questions too — for
  PhantomBuster tech/product/revenue roles specifically, that includes which squad this is for,
  PB2 vs. PBAI/PB3, and IC-level, which are easy to leave silently assumed otherwise.
- **Team & culture fit** — team vibe in three words, what kind of person has struggled here before,
  how the team makes decisions, first-30-days expectations. Candidates join teams, not companies;
  this is routinely skipped in favor of pure role/skills coverage.
- **Closing the conversation** — the strongest pitch for this specific role, what objections a
  strong candidate will likely raise and how to handle them, and always end with "is there anything
  I haven't asked that you think I really should have?" as a catch-all — selling the role and
  leaving room for what wasn't anticipated are both easy to skip once the hard questions are done.
- **Panel size, chosen deliberately.** Ask what number of interviewers the HM has in mind, and
  whether it's deliberate or just defaulted to "whoever's available." More interviewers is not
  monotonically better — past a certain point, a larger panel tends to *increase* false negatives
  (good candidates wrongly rejected), because a big group defaulting to near-consensus regresses
  toward the most conservative "no" in the room, the same way a large group struggles to agree on
  where to grab lunch. Push for a deliberately-sized panel (often single digits) picked for decision
  quality.
- **Panel design as a two-sided choice.** Most panels are already tuned hard against false
  positives (a bad hire slipping through) — ask whether anyone plays an independent,
  incentive-neutral role (not the HM, not the recruiter, no stake in filling the seat quickly —
  Amazon's "Bar Raiser" role is the named example) to also guard against false negatives, or
  whether the panel is one-sided by design.
- **Push past vague quality language.** If the HM says "culture fit," "culture add," "motivated,"
  "senior," "passion," or "potential," treat it as unresolved rather than an answer — ask what that
  looks like concretely for this team, and don't assume the rest of the panel would define it the
  same way. Include Vlastelica's "ass factor" framing if useful: how much tolerance does this team
  actually have for a brilliant-but-difficult performer. Undefined terms like these are the most
  common root cause of false negatives — good candidates rejected for reasons no one could actually
  articulate.

**Situational — use when they fit:**

- **Process logistics, agreed upfront rather than discovered mid-search**: target start date,
  number of interview rounds and how fast the team moves once there's a finalist, who actually has
  the final call (distinct from who's on the panel), and whether any internal candidates or
  referrals are already in the mix — worth surfacing early so external sourcing effort isn't wasted
  chasing a seat that's effectively already spoken for.
- **If the HM is slow to engage** (dragging feet on scheduling, treats this as a favor to TA rather
  than their own problem): lead with the cost-of-vacancy angle instead of a generic ask — name what
  the open seat is actually costing them, then pivot to "here's what other HMs do to fill this kind
  of role faster." That's the door-opener into a real advisory conversation, not a bigger ask.
- **Agree on one plan-referenced progress metric up front** — are we ahead of or behind the agreed
  plan/timeline — rather than leaving it to generic recruiting metrics (source of hire, average
  days-to-fill) the HM doesn't actually track. HMs who aren't given this metric tend to start asking
  for detailed status reports instead — a symptom of the alignment gap, not a reporting problem to
  solve with more reports.
- **Optional — Hiring Manager Maturity read.** If Diane describes how this HM has behaved on past
  reqs (responsive vs. slow, engaged vs. hands-off, complains about candidate quality, etc.), place
  them on the 4-stage model in `references/hiring-manager-maturity-model.md` and suggest how to
  frame the ask accordingly (e.g., a Passive-stage HM needs to be sold on why this is worth their
  time before anything else lands). Only do this if Diane gives you something to place them with —
  don't guess a stage from the JD alone.

**Frameworks to invoke opportunistically:**

- **Name the Speed-Quality-Cost triangle explicitly, early.** A hiring manager can only optimize two
  of the three (fast + good, but expensive/resourced; fast + cheap, but lower quality; good + cheap,
  but slower). Naming this up front resets unrealistic expectations before they get baked into the
  rest of the conversation, rather than surfacing as friction later.
- **Use the 1-10-100 rule to calibrate the target profile before sourcing starts, not after.**
  Misalignment caught at kickoff costs roughly 1x to fix; caught mid-search, ~10x; caught at
  offer/decline, ~100x. Concretely: bring 2-3 disparate candidate sketches (not just the draft
  profile from Phase B) into the meeting and ask pre-close questions like *"if I found someone from
  [Company X] with [Y background], would you hire them?"* for each — this pins down the real target
  faster than describing the ideal candidate in the abstract.

## Output format

Three labeled buckets, in this order, plus one closing line:

1. **JD challenges** (Phase A)
2. **Homework to pull before the meeting** (Phase B)
3. **Questions to bring into the meeting** (Phase C)
4. Close with: *this is prep, not the meeting itself* — if Diane wants sourcing strings built from
   the draft candidate profile, hand off to the Irina skills next; if she wants the actual Notion
   HM-question doc the way the live `Intake-Meeting-Automation/` V1 scenario generates it, that's
   a separate automated artifact, not this skill's output.

## What this skill does not do

- Does not build Boolean search strings or sourcing plans (Irina LinkedIn Lite/Recruiter).
- Does not touch anything post-meeting — role extraction from meeting notes, the Slack kickoff
  channel, sourcing-brief generation, or JD v2 merging all live in the `Intake-Meeting-Automation/`
  V2 Make scenario, not here.
- Does not treat "the JD says X" as itself an answer to an open question — an unstated assumption
  (like whether "remote" means worldwide) stays open until the meeting actually resolves it.
