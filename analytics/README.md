# TeamTailor Reporting V2 — Weekly Report + Final Summary

**Last updated:** September 2026
**Owner:** Diane Rocher
**Stack:** Make.com · TeamTailor API · Make Data Stores · Slack

---

## Overview

Two Make scenarios that together turn TeamTailor pipeline data into recurring Slack
reporting for open roles, with a cumulative wrap-up once a role is filled. They are not
chained to each other directly (no "Run a scenario" / webhook link between them) — they
communicate purely through two shared **Data Stores**, plus a manual status change on a
row in the first one. This supersedes the single-scenario V1 tracked at
[`../make/02_generate_weekly_report.py`](../make/02_generate_weekly_report.py), which
stayed active for comparison and has since been split into this two-scenario design.

```
                         ┌─────────────────────────┐
                         │   TT Roles Registry      │   Data Store
                         │   (status: active/       │   one row per role
                         │    filled/reported)      │
                         └──────────┬───────────────┘
                                    │ status = active
                                    ▼
                    ┌───────────────────────────────┐
                    │ Scenario "Weekly Report"       │   weekly, Fri 10:00
                    │ 1 SearchRecord (DS1, active)   │
                    │ 2 Python: pull TT API, build   │
                    │   weekly Slack report          │
                    │ 3 AddRecord → DS2 (upsert by   │
                    │   job_id_week_of)               │
                    │ 4 Slack: post weekly report     │
                    └──────────┬──────────────────────┘
                               ▼
                  ┌─────────────────────────┐
                  │  TT Weekly Snapshots     │  Data Store
                  │  one row per             │  (accumulates every Friday
                  │  job_id + week_of        │   this scenario runs)
                  └──────────┬───────────────┘
                             │ read by job_id
                             ▼
        (someone flips the DS1 row's status: active → filled — manual, see below)
                             │
                    ┌────────────────────────────────┐
                    │ Scenario "Final Summary"        │   on-demand
                    │ 1 SearchRecord (DS1, filled)     │
                    │ 2 SearchRecord (DS2, by job_id)  │
                    │ 3 BasicAggregator → array         │
                    │ 4 Python: cumulative summary       │
                    │ 5 Slack: post "Role Filled!"       │
                    │ 6 UpdateRecord DS1 → status=reported│
                    └────────────────────────────────┘
```

---

## Scenario 1 — Weekly Report

| Field | Value |
|---|---|
| Schedule | Weekly, Fridays at 10:00 |
| Blueprint | [`blueprints/teamtailor-weekly-report.blueprint.json`](blueprints/teamtailor-weekly-report.blueprint.json) |
| Local script copy | [`scripts/01_weekly_report.py`](scripts/01_weekly_report.py) |

### What it does

1. **datastore:SearchRecord** on *TT Roles Registry*, filtered `status = active` →
   iterates once per open role.
2. **code:ExecuteCode (Python)** — calls the TeamTailor API for that `job_id`
   (job details + paginated job-applications with candidate/stage includes), computes
   the stage breakdown, sourced-vs-inbound split, HM-stage conversion funnel and
   threshold-based alerts (days-open, pending-review backlog, low screen-pass rate,
   high use-case fail rate, low offer-acceptance), and renders it all into one Slack
   `mrkdwn` message.
3. **datastore:AddRecord** into *TT Weekly Snapshots*, key `{job_id}_{week_of}`,
   `overwrite: true` — so a re-run on the same day updates rather than duplicates that
   week's row.
4. **slack:CreateMessage** posts the weekly report to the role's `channel` (read off
   the DS1 row, not hardcoded), using the shared Slack connection.

### Module-by-module

| # | Module | Input | Output | Necessity |
|---|---|---|---|---|
| 1 | `datastore:SearchRecord` on *TT Roles Registry*, filter `status = active` | Nothing — this **is** the trigger, fired by the weekly schedule | One bundle per active role: `job_id`, `job_title`, `channel`, `status`, `date_added`, `date_filled` | **Essential.** Source of iteration — without it there's no list of roles to report on, and nothing downstream runs. |
| 2 | `code:ExecuteCode` (Python) — TeamTailor API pull + analytics | `job_id`, `channel` from module 1; API token | `result` dict: `slack_message`, `job_id`, `job_title`, `channel`, `week_of`, `total_all/active/rejected/sourced/inbound`, `days_open`, `alerts`, `hired_candidates` | **Essential — the engine.** Calls the TeamTailor API, computes the funnel/alerts, and renders the Slack text. Everything downstream just persists or posts what this produces. |
| 3 | `datastore:AddRecord` into *TT Weekly Snapshots* | Fields from module 2's `result`; key = `{job_id}_{week_of}` | A new (or overwritten) row in DS2 | **Essential for scenario 2.** If skipped, DS2 stays empty and the Final Summary scenario errors out (no snapshots found) when that role is later marked filled. |
| 4 | `slack:CreateMessage` | `text = result.slack_message`, `channel` from module 1 | Slack API response (unused downstream) | **Essential — the deliverable.** The reason the scenario exists: a human-readable weekly update in Slack. |

## Scenario 2 — Final Summary

| Field | Value |
|---|---|
| Schedule | On-demand only — no trigger fires it automatically |
| Blueprint | [`blueprints/teamtailor-final-summary.blueprint.json`](blueprints/teamtailor-final-summary.blueprint.json) |
| Local script copy | [`scripts/02_final_summary.py`](scripts/02_final_summary.py) (reads `snapshots` from [`scripts/fixtures/example_snapshots.json`](scripts/fixtures/example_snapshots.json) standalone, instead of the live aggregator array) |

### What it does

1. **datastore:SearchRecord** on DS1, filtered `status = filled` → iterates once per
   role that just got marked filled.
2. **datastore:SearchRecord** on DS2, filtered `job_id = <current role>`, sorted
   `week_of` ascending → pulls that role's entire weekly history.
3. **builtin:BasicAggregator** collapses module 2's per-row iteration back into one
   array, since module 2 runs inside module 1's iterator.
4. **code:ExecuteCode (Python)** — sorts the snapshot array, takes the most recent
   week's cumulative totals, computes `weeks_tracked` and `days_to_fill` (from DS1's
   `date_added`/`date_filled`), and builds a "🎉 Role Filled!" cumulative Slack summary.
   Raises if DS2 has no snapshots for the job — i.e. scenario 1 must have run at least
   once for that role before this can produce anything.
5. **slack:CreateMessage** posts the summary to the same `channel`.
6. **datastore:UpdateRecord** sets that DS1 row's `status` to `reported` — this is the
   idempotency guard: once flipped, the row no longer matches `status = filled` and
   scenario 2 won't reprocess it on a future run.

### Module-by-module

| # | Module | Input | Output | Necessity |
|---|---|---|---|---|
| 1 | `datastore:SearchRecord` on DS1, filter `status = filled` | Nothing — fired manually | One bundle per newly-filled role: `job_id`, `job_title`, `channel`, `date_added`, `date_filled`, record key | **Essential.** Trigger/source — determines which roles get a final summary this run. Also handles multiple simultaneously-filled roles: each gets its own pass through modules 2–6 in the same execution. |
| 2 | `datastore:SearchRecord` on DS2, filter `job_id = {{1.data.job_id}}`, sorted `week_of` ascending | `job_id` from module 1 | One bundle per weekly snapshot row belonging to that role | **Essential.** Pulls the historical data the cumulative summary is built from — without it there's nothing to aggregate. |
| 3 | `builtin:BasicAggregator` (feeder = module 2) | Every bundle module 2 emits for the current role | A single array of that role's weekly snapshots | **Structurally essential, not analytical.** Make iterates per-record after a search; this collapses those per-week bundles back into one array so module 4 runs once per role instead of once per week. Skip it and module 4 would fire redundantly per snapshot row. |
| 4 | `code:ExecuteCode` (Python) — cumulative summary | Module 1's `job_id/job_title/channel/date_added/date_filled` + module 3's `snapshots` array | `result` dict: `slack_message`, `job_id`, `channel`, `weeks_tracked`, `days_to_fill`, `hired_candidates` | **Essential — the engine.** Computes time-to-fill, weeks tracked, and the latest cumulative totals; builds the "🎉 Role Filled!" message. |
| 5 | `slack:CreateMessage` | `text = result.slack_message`, `channel` from module 1 | Slack API response | **Essential — the deliverable.** The celebratory wrap-up post. |
| 6 | `datastore:UpdateRecord` on DS1, sets `status: "reported"` | Module 1's record key + its existing field values (status overwritten) | Updated DS1 row | **Essential idempotency guard.** Without it, re-running the scenario would re-post the same "Role Filled!" summary for a role that's already been announced. |

---

## The manual link between the two scenarios

Nothing in either blueprint sets a role's status to `filled` (or creates the initial
`active` row). Both transitions on *TT Roles Registry* are manual today:

- **Seeding a role** (`status = active`, plus `job_id`, `job_title`, `channel`,
  `date_added`) — add the row by hand in the Make Data Store UI when a role opens.
  (Not produced by the [intake automation](../make/Make_Scenarios_Intake_Automation.md) —
  that flow explicitly creates no TeamTailor job draft.)
- **Marking a role filled** (`status = filled`, `date_filled` set) — edit the row by
  hand once TeamTailor shows the role as filled, then run the Final Summary scenario
  on demand.

Rows already flipped to `reported` are permanently excluded from future Final Summary
runs — only rows currently at `status = filled` are picked up, so older, already-
summarized roles are never reprocessed even if several roles are filled over time.

This manual step is the main gap worth closing if this pipeline scales to more roles:
either a scheduled Final Summary run (searching all `filled` rows on its own) or a
TeamTailor webhook that flips the status automatically would remove it.

---

## Data Stores

### TT Roles Registry — one row per role

| Field | Type | Notes |
|---|---|---|
| `job_id` | text | TeamTailor job ID |
| `job_title` | text | |
| `channel` | text | Slack channel the reports post to |
| `status` | text | `active` → `filled` → `reported`, hand-edited (see above) |
| `date_added` | date | Used for `days_open` / `days_to_fill` |
| `date_filled` | date | Set when marking a role filled |

### TT Weekly Snapshots — one row per `job_id` + week

| Field | Type |
|---|---|
| `job_id` | text |
| `week_of` | date |
| `total_all`, `total_active`, `total_rejected`, `total_sourced`, `total_inbound` | number |
| `days_open` | number |
| `alerts` | text (`\|`-joined) |
| `hired_candidates` | text (comma-joined names) |

---

## Rebuilding this from scratch

Needs a TeamTailor API token (Settings → Integrations, in TeamTailor — currently a
`PASTE_TOKEN_HERE` placeholder in the Python module, not yet moved to a proper Make
connection/env), a Slack connection with write access to the target channels, and the
two data stores above created from their field lists. Scenario IDs, data store IDs,
and connection IDs are internal to this Make account and intentionally not listed here
— ask the owner for access instead.
