# Make Automation — Intake Meeting Workflow
**Last updated:** August 2026
**Owner:** Diane Rocher
**Stack:** Google Drive · Google Calendar · Anthropic Claude · Notion · Slack

---

## Overview

One Make scenario, single trigger, three parallel routes. This replaces an earlier
two-scenario design (a core-automation scenario plus a separate JD-enrichment scenario,
with a Teamtailor draft-job step) that was scrapped — there is no Teamtailor module in
the live automation.

Two builds ran side by side for a few weeks to compare approaches; the V2 build below won
and is now the only active one. The other has been deactivated and is kept around for
reference only.

**Status:** Active, in production.

---

## Trigger — Google Drive: watch files in a folder

| Field | Value |
|---|---|
| Connection | Your Google account |
| Drive | My Drive |
| Folder | `/Intake Meetings` |
| Watch | New files only |
| MIME type | `document` |
| Max files returned | 1 |
| Scheduler | Every 15 minutes |

### Filter — Intake Meeting

| Field | Value |
|---|---|
| Condition | File Name · Contains (case insensitive) · `Intake Meeting` |

---

## Module — Google Drive: get the meeting summary

Downloads the triggering file as **markdown** (Gemini's own "Notes by Gemini" export —
this preserves headings/formatting that plain text export loses).

---

## Module — sibling transcript lookup

A second Drive file — the full meeting transcript — usually lands next to the summary,
named the same way but with "Transcript" instead of "Notes by Gemini". Three chained
modules find and fetch it, tolerating its absence:

1. **Google Drive: make an API call** — `GET /v3/files` with a query matching
   `name contains '<base filename>' and name contains 'Transcript'` in the same folder.
   On error, resumes with `{"files": []}`.
2. **Regexp: parser** — extracts the file ID from the response body.
3. **Google Drive: get a file** — downloads that file as plain text. On error (no
   transcript found), resumes with empty `data`.

---

## Module — Anthropic Claude: extraction

| Field | Value |
|---|---|
| Model | `claude-haiku-4-5-20251001` |
| Max tokens | `800` |

Extracts role data as JSON from the Gemini summary, with the full transcript passed
alongside as a tie-breaker ("if the two disagree on any detail, trust the transcript").

Fields extracted: `role`, `role_slug`, `department`, `seniority`, `hm_name`, `hm_email`,
`skills`, `team`, `project_context`, `key_responsibilities`, `summary`.

Two fields get extra prompt engineering because they drive downstream routing logic:

- **`hm_name`** — explicit disambiguation rule: when multiple non-recruiter attendees
  could plausibly be the HM (e.g. their manager or a skip-level exec also joined), pick
  whoever owns the day-to-day of the team the role reports into, not whoever is most
  senior or talks the most.
- **`hm_email`** — looked up from the attendee list's `[Full Name](mailto:...)` links in
  the transcript, explicitly excluding the recruiter's own email. Used later to (a) find
  and invite the right person to Slack, and (b) confirm which calendar event is the real
  intake meeting.

---

## Module — JSON: parse JSON

Parses the extraction output into the fields above for use in every downstream module.

---

## Module — Anthropic Claude: TA screening kit

| Field | Value |
|---|---|
| Model | `claude-haiku-4-5-20251001` |
| Max tokens | `800` |

Generates an 11-line structured output: 4 must-have skills, a 100–150 word project
context paragraph, 3 screening questions, 2 red flags, and a closing recommendation.
Output is a strict one-value-per-line format (no quotes, no backslashes) so it can be
split and dropped straight into Notion blocks downstream.

---

## Router — 3 parallel routes

### Route 1 — Slack channel + sourcing brief

| Step | Module | Notes |
|---|---|---|
| 1 | Slack: make an API call (`/conversations.create`) | Private channel `hiring-<role_slug>`, stripped of `-notes-by-gemini` suffix artifacts |
| 2 | Filter: channel created | Guards the rest of the route |
| 3 | Slack: make an API call (`/conversations.invite`) | Invites the hardcoded recruiting-team Slack ID |
| 4 | Slack: create message | Welcome message, posted as bot "Hiring-Robot" (`:wall-e:`), links to the Hiring Process Guide and TeamTailor Playbook Notion pages |
| 5 | Slack: create message | Role recap — HM, team, project context, must-have skills, screening questions, red flags (all pulled from the TA screening kit output) |
| 6 | Anthropic Claude — sourcing brief | `claude-sonnet-4-5`, with the `web_search` tool (max 5 uses). See below. |
| 7 | Slack: create message | Posts the sourcing brief as a **threaded reply** under the role-recap message |
| 8 | Slack: list users in workspace | Limit 500 |
| 9 | Filter: HM name match | Case/accent-normalized match of `hm_name` against each workspace user's real name |
| 10 | Slack: make an API call (`/conversations.invite`) | Invites the matched HM automatically — no manual invite step anymore |

**Sourcing brief prompt (module 6):** asks Claude to ground a Slack-mrkdwn-formatted
brief in live web search — LinkedIn Recruiter boolean string, Google X-ray string,
GitHub string (if relevant), a deduplicated keyword list, tech-stack alternatives, and
3 likely feeder companies with reasoning, each web-sourced claim cited inline. Boolean
strings default their location filter to France unless the transcript names another
country. Output capped at ~300 words, no literal quotes/backslashes.

### Route 2 — Notion: TA Screening Kit page

| Step | Module | Notes |
|---|---|---|
| 1 | Notion: create a page | Title `<role> — TA Screening Kit`, under a fixed parent page |
| 2 | Notion: make an API call (`PATCH /v1/blocks/{page_id}/children`) | Populates Must-have skills, Project context, Screening questions, Red flags — each field sliced out of the TA screening kit output by line number |
| 3 | Slack: create message | Announces the new page in a fixed team channel, as "Hiring-Robot" |

### Route 3 — Notion: JD v2 (enriched JD + diff)

| Step | Module | Notes |
|---|---|---|
| 1 | Google Calendar: search events | Query `Intake Meeting`, today's date range only |
| 2 | Filter: correct meeting matched | Requires a non-empty event **and** that the event's attendee list contains `hm_email` — this is what makes the match reliable instead of guessing by time window |
| 3 | Regexp: parser | Extracts the Notion page ID (32-char hex) from the event description. On no match, resumes with empty capture |
| 4 | Notion: make an API call (`GET /v1/blocks/{page_id}/children`) | Fetches the HM's original JD (JDv1). On error, resumes with empty body |
| 5 | Anthropic Claude — JD v2 | `claude-haiku-4-5`, 16-line structured output (see below) |
| 6 | Notion: create a page | Title `<role> — JD v2`, under a fixed parent page |
| 7 | Notion: make an API call (`PATCH .../children`) | Populates About the role, What you'll do, What we're looking for, Team & context, **Changes vs. JDv1**, **Watch out — possible incoherencies** |
| 8 | Slack: create message | Announces the new JD v2 page in the same fixed team channel |

**JD v2 prompt (module 5):** rewrites the JD from intake-meeting data plus JDv1 content,
explicitly told to ignore generic boilerplate sections (About Us, Benefits, Hiring
Process) if present, and to focus comparison on role-specific content only. Beyond the
11 JD-content lines, it adds:
- up to 3 concrete "changes vs. JDv1" bullets (or "No significant changes" / "None"),
- up to 2 "possible incoherencies" — things the HM said in the meeting that conflict
  with or are missing from the original JD, worth double-checking before publishing.

---

## What this automation produces, per intake meeting

| Output | Where |
|---|---|
| Private Slack channel | `hiring-<role_slug>` — recruiting team + auto-detected HM invited |
| Sourcing & market intelligence brief | Threaded reply under the role recap, web-search-grounded |
| TA Screening Kit | Notion page — skills, context, screening questions, red flags |
| JD v2 | Notion page — enriched JD + diff vs. JDv1 + incoherency flags |

No Teamtailor job draft is created by this automation.

---

## Known rough edges (as of last update)

- The sibling-transcript lookup and the calendar-event match both depend on naming/
  attendee conventions holding (file named consistently, HM's email actually present in
  the calendar invite's attendee list) — when either breaks, the route resumes with an
  empty fallback rather than failing loudly, so check manually if a JD v2 or transcript-
  enriched extraction seems thinner than expected.
- The HM auto-invite (Route 1, step 9) matches on normalized display name — a Slack
  profile using a nickname or different name format than the calendar/transcript will
  silently fail to match, same as the JD v2 route's `hm_email` attendee check.

---

## Keys and IDs to collect before rebuilding this from scratch

| What | Where to find it |
|---|---|
| Anthropic API key | console.anthropic.com → API keys |
| Google Drive intake folder ID | Open the folder in Drive → copy the ID from the URL |
| Notion "TA Screening Kit" parent page ID | Open the page in Notion → `...` → Copy link → last string in URL |
| Notion "JD v2" parent page ID | Same as above, for the JD v2 parent page |
| Your recruiting-team Slack ID(s) | Slack → profile → `...` → Copy member ID |
| Fixed Slack announcements channel ID | Slack → channel details → Copy channel ID |
