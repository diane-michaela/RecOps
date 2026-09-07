# Intake Meeting — Pre-Meeting Prep + Post-Meeting Processing

**Last updated:** 2026-09-07
**Owner:** Diane Rocher
**Stack:** Make.com · Google Drive · Google Calendar · Anthropic Claude · Notion · Slack · Airtable

---

## Overview

Two independent Make scenarios that bookend the same real-world event — an intake
meeting between a recruiter and a hiring manager — on either side of it:

- **Pre-Intake — Prep Question** fires when an "Intake Meeting" calendar event carrying
  a linked JD is created, and prepares AI-generated, JD-specific challenge questions
  plus a full meeting agenda in Notion *before* the meeting happens.
- **Intake Meeting automation V2** fires once the meeting's notes/recording land in
  Drive, and does all the *post*-meeting processing: extracting structured role data,
  standing up a Slack channel, generating a sourcing brief, and publishing a TA
  Screening Kit and an enriched JD v2 to Notion.

They are **not chained to each other** — no shared data store, webhook, or "Run a
scenario" link. Each is a standalone trigger reacting to a different artifact of the
same meeting (the calendar invite vs. the meeting notes file).

```
   JD linked in an "Intake Meeting" calendar invite
                     │
                     ▼
   ┌─────────────────────────────────────┐
   │  Pre-Intake — Prep Question           │   webhook-triggered
   │  1 Extract JD id from invite          │
   │  2 Fetch JD from Notion               │
   │  3 Claude: 7 JD-specific challenge     │
   │    questions                           │
   │  4 Build full 9-section agenda page    │
   │  5 Create + populate Notion page       │
   │  6 Slack: announce                     │
   │  7 Update calendar invite w/ page link │
   └─────────────────────────────────────┘

                (meeting happens — no link between the two scenarios)

   Meeting notes / recording lands in Drive
                     │
                     ▼
   ┌───────────────────────────────────────────┐
   │  Intake Meeting automation V2                │   webhook-triggered
   │  Main chain: fetch notes + transcript,       │
   │  Claude extraction → parsed role fields →    │
   │  Claude TA screening kit → 3-way router      │
   │                                                │
   │  Route 1: Slack channel + sourcing brief      │
   │           + pipeline cross-checks (Airtable)  │
   │  Route 2: Notion — TA Screening Kit page      │
   │  Route 3: Notion — JD v2 (merged + changelog) │
   └───────────────────────────────────────────┘
```

---

## Scenario 1 — Pre-Intake — Prep Question

| Field | Value |
|---|---|
| Trigger | Inbound webhook, fired immediately (not a schedule) |
| Blueprint | [`blueprints/pre-intake-prep-questions.blueprint.json`](blueprints/pre-intake-prep-questions.blueprint.json) |

The webhook's caller isn't part of this blueprint — based on the payload shape
(`eventId`, `description`, `summary`) it's fed by something watching Google Calendar for
new/updated events, most likely a calendar push-notification relay set up outside this
scenario.

<img width="1015" height="223" alt="pre-intake" src="https://github.com/user-attachments/assets/de1d703c-c5c2-48a1-89c6-4b8f3507134a" />


### What it does

1. **regexp:Parser** extracts a Notion page id from the calendar event's description,
   gated by a filter that also checks the description doesn't already contain
   `"Intake questions:"` — this is the idempotency guard against reprocessing the same
   event.
2. **notion:makeApiCall** (×2) fetches the linked JD's title and full block content.
3. **anthropic-claude:createAMessage** (`claude-haiku-4-5`) reads the JD and generates
   exactly 7 lines of challenge questions the recruiter should ask the hiring manager —
   explicitly instructed to find inconsistencies (title vs. mission vs. stack vs.
   day-to-day) rather than ask generic questions, and to never overlap with the
   standard agenda's own questions.
4. **json:TransformToJSON** merges those AI-generated questions into a fixed 9-section
   Notion page template (Start with the Why, The Team, Role & Scope, Role-specific —
   challenge the JD, Must-Have vs. Nice-to-Have, How We'll Work Together, Interview
   Panel, Sourcing, Closing).
5. **notion:createAPage1** + **notion:makeApiCall** create and populate the page.
6. **slack:CreateMessage** announces the new page.
7. **google-calendar:updateAnEvent** rewrites the event's description to insert a
   `📋 Intake questions: <link>` line — this both delivers the link on the invite itself
   and plants the marker step 1's filter checks for next time.

### Module-by-module

| # | Module | Input | Output | Necessity |
|---|---|---|---|---|
| 1 | `gateway:CustomWebHook` — trigger | External payload: `eventId`, `description`, `summary` | One bundle per webhook call | **Essential.** Entry point — nothing runs without it. |
| 2 | `regexp:Parser` — extract JD page id, filter "has JD link, not yet processed" | Event `description` | `$1` = 32-char hex Notion page id (empty on no match, via `onerror`) | **Essential.** Determines which JD to process; the filter is the idempotency guard against reprocessing an already-handled invite. |
| 3 | `notion:makeApiCall` GET page, filter "JD id extracted" | `$1` from step 2 | JD page metadata `body` (empty on error) | **Supports step 4** — feeds the title fallback; non-fatal if it fails. |
| 4 | `regexp:Parser` — extract plain-text title | Step 3's `body` | JD title (or empty) | **Soft.** Naming fallback only — the page title and Slack message fall back to the calendar event's own `summary` if this is empty. |
| 5 | `notion:makeApiCall` GET block children | `$1` from step 2 | Full JD block content `body` (empty on error) | **Essential.** This is the actual JD text the Claude prompt reasons over. |
| 6 | `json:TransformToJSON` | Step 5's `body` | Parsed JSON of the JD blocks | **Essential.** Normalizes the raw Notion response for the prompt. |
| 7 | `anthropic-claude:createAMessage` (`claude-haiku-4-5`, 600 tokens, temp 0) | The JD JSON from step 6 | 7 lines: 5 must-ask + 2 ask-if-relevant challenge questions | **Essential — the core value-add.** This is what makes the prep material specific to this JD instead of generic. |
| 8 | `json:TransformToJSON` — build page body | Static 9-section template + step 7's questions split by newline | Full Notion page-body JSON | **Essential.** Combines the static agenda with the AI output into one API-ready payload. |
| 9 | `notion:createAPage1` | Title (JD title, falls back to calendar `summary`) | New page `id`, `url` | **Essential.** Creates the deliverable's container. |
| 10 | `notion:makeApiCall` PATCH children | Step 8's body → step 9's page id | Populated page | **Essential.** Without this the page stays blank. |
| 11 | `slack:CreateMessage` | New page `url`, role name | Posted message | **Essential — the deliverable.** Surfaces the prep doc to the team. |
| 12 | `google-calendar:updateAnEvent` | `eventId`, rebuilt `description` inserting the page link | Updated event (silently skipped on error) | **Essential idempotency guard + deliverable.** Puts the link directly on the invite, and writing `"Intake questions:"` into the description is exactly what step 2's filter checks for to avoid reprocessing. |

---

## Scenario 2 — Intake Meeting automation V2

| Field | Value |
|---|---|
| Trigger | Inbound webhook, fired immediately (not a schedule) |
| Blueprint | [`blueprints/intake-meeting-automation.blueprint.json`](blueprints/intake-meeting-automation.blueprint.json) |
| Local script copy | [`scripts/01_search_string_generator.py`](scripts/01_search_string_generator.py) |

**Note:** an earlier revision of this automation polled a Google Drive folder every 15
minutes. The live scenario has since moved to an instant webhook trigger, and Route 1
has grown a deterministic search-string generator and two Airtable pipeline
cross-checks along the way — this README reflects the current, live blueprint.

<img width="1038" height="384" alt="intake-meeting" src="https://github.com/user-attachments/assets/8c7c0d6f-21b8-40db-980d-b032a5fd13de" />


### What it does, end to end

When a new "Intake Meeting" Google Meet summary doc lands (via webhook), the scenario
pulls the Gemini summary and, if present, the raw transcript, then uses Claude to
extract structured role data (title, HM name/email, skills, team, responsibilities)
with the transcript as a tie-breaker. A second Claude call turns that into an 11-line
TA screening kit (must-haves, screening questions, red flags). From there it fans into
three parallel routes: **(1)** create a private Slack channel, post a welcome message
and role recap, generate a web-search-grounded sourcing brief (job titles, boolean
keywords, GitHub keywords, tech-stack alternatives, market intel) plus a deterministic
Meetup search string and Airtable formula, auto-invite the matched hiring manager, and
cross-check Airtable for candidates already in the pipeline or already sourced for
similar roles; **(2)** publish the TA screening kit as a Notion page; **(3)** find the
matching calendar event and its linked JD v1 page, have Claude produce a full **merged**
JD v2 — the original's boilerplate sections copied verbatim, its role-specific sections
(responsibilities, requirements, team, seniority, tech stack) updated to match the
intake meeting — plus a **"What has been changed"** changelog and a **"Watch out —
possible incoherencies"** callout section, and publish that too. This replaced an
earlier design that only appended a suggested-changes list below a verbatim copy of
the original JD; the current version actually applies the changes into the JD body.
End state: one Slack channel, one sourcing brief, one TA Screening Kit page, and one
JD v2 page per intake meeting.

### Main chain (before the router)

<img width="572" height="215" alt="common-branch" src="https://github.com/user-attachments/assets/9588090f-a397-4431-bfcb-3744cfdc22c4" />


| # | Module | Input | Output | Necessity |
|---|---|---|---|---|
| 1 | `gateway:CustomWebHook` — trigger | External webhook payload | `fileId`, `fileName` | **Essential.** Entry point. |
| 2 | `google-drive:getAFile` — download as markdown, filter `fileName` contains "Intake Meeting" | `fileId` from step 1 | Gemini summary text | **Essential.** Guards against firing on unrelated files; primary data source. |
| 3 | `google-drive:makeApiCall` — sibling transcript lookup (resumes `{"files": []}` on error) | Base filename from step 1 | Raw Drive API search response | **Optional/robustness.** Best-effort; degrades gracefully. |
| 4 | `regexp:Parser` — extract transcript file id (`continueWhenNoRes: true`) | Step 3's response | Transcript file id (or none) | **Optional/robustness.** Part of the same graceful-fallback chain. |
| 5 | `google-drive:getAFile` — download transcript as text (resumes empty on error) | Transcript file id | Transcript text (or empty) | **Nice-to-have.** Improves extraction accuracy, especially `hm_email`; not required. |
| 6 | `anthropic-claude:createAMessage` — extraction (`claude-haiku-4-5`, 800 tokens, temp 0) | Summary (step 2) + transcript (step 5, or "Not available") | JSON: `role`, `role_slug`, `department`, `seniority`, `hm_name`, `hm_email`, `skills`, `team`, `project_context`, `key_responsibilities`, `summary` | **Essential.** The single source of structured data every downstream route depends on. |
| 7 | `json:ParseJSON` | Step 6's text response (```json fencing stripped) | Named fields used throughout the rest of the scenario | **Essential.** Converts free text into usable pills. |
| 8 | `anthropic-claude:createAMessage` — TA screening kit (`claude-haiku-4-5`, 800 tokens, temp 0) | Parsed fields from step 7 | 11-line output: 4 skills, project-context paragraph, 3 questions, 2 red flags, closing line | **Essential.** Feeds both the Slack role recap and the Notion TA Screening Kit page. |
| 9 | `builtin:BasicRouter` — 3-way split | — | Fans into Routes 1, 2, 3 (parallel) | **Essential.** The structural fan-out point. |

### Route 1 — Slack channel, sourcing brief, and pipeline cross-checks

<img width="1200" height="291" alt="routeA" src="https://github.com/user-attachments/assets/fe1aed6a-6416-40bb-a951-089d1ded84ab" />


| # | Module | Input | Output | Necessity |
|---|---|---|---|---|
| 1 | `slack:MakeAPICall` — create private channel (resumes empty on error) | Role slug + date | New channel id | **Essential.** Creates the hub everything else in this route posts into. |
| 2 | `slack:MakeAPICall` — invite recruiting team, filter "channel created" | Channel id | Invite side-effect | **Essential** for the channel to be usable. |
| 3 | `slack:CreateMessage` — welcome message ("Hiring-Robot" bot) | Channel id, role, links to process docs | Posted message | **Nice-to-have.** Onboarding formatting, not load-bearing. |
| 4 | `slack:CreateMessage` — role recap | Channel id, role/HM/team + TA screening kit lines | Posted message (`ts` captured for threading) | **Essential.** Delivers the screening kit content and anchors the thread. |
| 5 | `anthropic-claude:createAMessage` — sourcing brief (`claude-sonnet-4-5`, web search tool, 1400 tokens, temp 0; resumes a diagnostic placeholder on error) | Existing JD content (truncated, fetched by step 11's calendar/Notion lookup below — runs earlier in the actual flow than its table position here), role/seniority/department/skills/team | Job titles, strict/broad boolean keywords, GitHub keywords, tech-stack alternatives, 3 web-sourced feeder companies with citations | **Essential to the route's purpose**, with a defined degrade path if web search fails. Previously only produced a keyword list + tech-stack alternatives + feeder companies; the LinkedIn/Google boolean-string generation that used to live in step 12's script moved into this prompt. |
| 6 | `slack:CreateMessage` — post sourcing brief as threaded reply (resumes empty on error) | Thread `ts`, step 5's brief text, step 12's Meetup query string | Posted threaded message | **Essential.** Where the brief actually reaches the user. |
| 7 | `slack:ListUsersWorkspace` (limit 500) | — | Workspace user list | **Supporting step** for the HM auto-invite — no direct "find user by name" lookup exists. |
| 8 | `slack:MakeAPICall` — auto-invite HM, filter on normalized name match (resumes empty on error) | Workspace list + `hm_name` | Invite side-effect | **Nice-to-have but fragile.** Silently fails to match if the Slack display name differs from the meeting/transcript name format. |
| 9 | `google-calendar:searchEvents` — find today's "Intake Meeting" event | Query + date range | Matching events | **Essential** to reliably identify the specific calendar event tied to this HM. |
| 10 | `regexp:Parser` — extract JD page id, filter requires HM email in attendee list (resumes empty on error) | Event description + `hm_email` | JD v1 page id | **Essential for reliability** — the attendee-email check is what makes the match trustworthy instead of guessing by time window. |
| 11 | `notion:makeApiCall` — fetch JD v1 content (resumes empty on error) | Page id from step 10 | JD v1 content | **Nice-to-have.** Improves the sourcing brief's keyword coverage; prompt has a fallback. |
| 12 | `code:ExecuteCode` (Python) — deterministic Airtable formula + Meetup query, see [`scripts/01_search_string_generator.py`](scripts/01_search_string_generator.py) | Skills, role, department | Airtable `SEARCH()` formula, Meetup query lines, role category bucket | **Essential.** Feeds both nested Airtable cross-checks below and the Meetup line in step 6's message. No longer generates LinkedIn/Google boolean strings — that moved into step 5's prompt. |
| 13 | `builtin:BasicRouter` — nested 2-way router (both branches always run) | — | Fans into two Airtable cross-check branches | **Nice-to-have addition**, not in the earlier doc — adds pipeline context to the channel. |

**Nested branch A — candidates already applied (Airtable)**

| # | Module | Input | Output | Necessity |
|---|---|---|---|---|
| A1 | `airtable:ActionSearchRecords` — search by step 12's `airtable_formula` (role/title/skills × France/Portugal/Spain), **no `maxRecords` cap** | `airtable_formula` from step 12 | Every matching candidate record | **Nice-to-have, known risk.** Surfaces existing pipeline overlap; not core to the intake flow. A broad role/skill match with no result cap can return a large record set and post one Slack message per record (A2) — accepted risk, not yet capped. |
| A2 | `slack:CreateMessage` — "Already in Teamtailor" note, threaded, one message per record from A1 | Candidate fields from A1 | Posted message(s) | **Nice-to-have.** Informational only. |

**Nested branch B — already-sourced leads by category (Airtable)**

| # | Module | Input | Output | Necessity |
|---|---|---|---|---|
| B1 | `airtable:ActionSearchRecords` — search by role category, sorted by score, **no `maxRecords` cap** | `role_bucket` from step 12 | Every sourced-lead record in that category | **Nice-to-have, known risk.** Supplementary sourcing context; same uncapped-result-set risk as A1 (e.g. the "AI/ML/Data Science" bucket alone can hold several hundred leads). |
| B2 | `slack:CreateMessage` — "Already sourced" note, threaded, one message per record from B1 | Lead fields from B1 | Posted message(s) | **Nice-to-have.** Informational only. |

### Route 2 — Notion: TA Screening Kit page

<img width="259" height="114" alt="routeB" src="https://github.com/user-attachments/assets/bafead3b-0264-4c9a-aa77-771394d7847b" />


| # | Module | Input | Output | Necessity |
|---|---|---|---|---|
| 1 | `notion:createAPage1` | Role name | New page `id`, `url` | **Essential.** Creates the deliverable. |
| 2 | `json:TransformToJSON` — build page body | TA screening kit lines (main chain step 8) | Page-body JSON | **Essential.** Structures the content for Notion's API. |
| 3 | `notion:makeApiCall` PATCH children | Page id + body | Populated page | **Essential.** Writes the content. |
| 4 | `slack:CreateMessage` — announce | Role, seniority, page `url` | Posted message | **Nice-to-have.** Visibility, not core output. |

### Route 3 — Notion: JD v2 (merged JD + changelog)

<img width="689" height="146" alt="routeC" src="https://github.com/user-attachments/assets/6aa76eae-db2a-44e2-a93c-8a1a54de7a32" />

**Note (2026-09-07):** this route's JD-generation step was redesigned twice since the
screenshot above — first from a from-scratch rewrite into a verbatim-copy-plus-suggestions
format, then from that into the merge-plus-changelog design described below. The image
predates both and may show a different module count/shape than the table.

| # | Module | Input | Output | Necessity |
|---|---|---|---|---|
| 1 | `google-calendar:searchEvents` — find today's "Intake Meeting" event | Query + date range | Matching events | **Essential** — needed to locate the JD v1 page linked from the invite. |
| 2 | `regexp:Parser` — extract JD v1 page id, filter requires HM email in attendee list (resumes empty on error) | Event description + `hm_email` | JD v1 page id | **Essential.** Same reliability guard as Route 1's equivalent step. |
| 3 | `notion:makeApiCall` — fetch JD v1 content (resumes empty on error) | Page id from step 2 | Raw JD v1 blocks (`body`) | **Essential** to the merge feature; degrades gracefully if missing. |
| 4 | `json:TransformToJSON` | Step 3's `body` | Parsed JSON of the JD v1 blocks | **Essential.** Normalizes the raw Notion response before it hits the Claude prompt as `{{220.json}}` — added specifically because this connector's Notion API version keys block content under `"text"`, not the documented `"rich_text"`, and the prompt/code below need a consistently-parsed structure either way. |
| 5 | `anthropic-claude:createAMessage` — JD v2 merge (`claude-haiku-4-5`, 4000 tokens, temp 0) | Role fields + JD v1 content from step 4 | JSON: `jd_blocks` (typed `{type, text}` entries reproducing the *entire* JD — boilerplate verbatim, role-specific sections updated to match the meeting), `changes_made` (past-tense changelog), `incoherencies` | **Essential — the core value-add.** Regenerates the full JD text merged with the meeting's changes, not just a diff list; `max_tokens` is 4000 (was 900) because it now reproduces the whole document instead of 16 summary lines. |
| 6 | `notion:createAPage1` | Role name | New page `id`, `url` | **Essential.** Creates the deliverable. |
| 7 | `code:ExecuteCode` (Python) — build page body | Step 5's `jd_blocks` / `changes_made` / `incoherencies` (JSON, parsed with a fallback if Claude's output isn't valid JSON) | Page-body JSON: a "Job description" section built from `jd_blocks`, then "What has been changed" (bulleted `changes_made`), then "Watch out — possible incoherencies" (bulleted `incoherencies`) | **Essential.** Replaced a `json:TransformToJSON` step here — this module validates/reshapes Claude's JSON output before it becomes a raw PATCH body, which a static `object` mapper can't do. |
| 8 | `notion:makeApiCall` PATCH children | Page id + body | Populated page | **Essential.** Writes the content. |
| 9 | `slack:CreateMessage` — announce | Role, seniority, page `url` | Posted message | **Nice-to-have.** Visibility, not core output. |

**Design note — why this route has its own calendar/Notion lookup instead of sharing
Route 1's:** modules 20/21/22 above are a byte-for-byte duplicate of Route 1's
90/91/92 (same calendar query, same HM-email-in-attendees filter, same Notion fetch).
A 2026-09-07 attempt to deduplicate them — by hoisting the shared lookup in front of a
single branch that fed both this route and Route 1's sourcing brief — accidentally
routed Slack channel creation (Route 1's first step) upstream of JD v2 generation too.
JD v2 never posts to that dynamic Slack channel, so it has no logical dependency on
channel creation succeeding — but once a same-day rerun hit `name_taken` on the
channel name, the whole shared branch died, silently taking JD v2 down with it.
Confirmed by stripping `onerror` handlers to force the real error to surface instead of
the swallowed empty-body fallback. Reverted; the two lookup chains stay duplicated on
purpose so each route's failure modes stay isolated to that route.

---

## Rebuilding this from scratch

Needs connections for Google Drive, Google Calendar, Anthropic Claude, Notion, Slack,
and Airtable (Route 1's pipeline cross-checks only). Scenario/hook/connection IDs,
Notion parent-page IDs, and Airtable base/table IDs are internal to this Make account
and intentionally not listed here — ask the owner for access instead. A real calendar
address appeared twice in the exported blueprint (the calendar searched for the intake
event) and has been replaced with `REDACTED_CALENDAR_EMAIL` in both copies.
