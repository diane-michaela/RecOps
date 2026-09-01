# TeamTailor Reporting V2 — Weekly Report + Final Summary

**Last updated:** September 2026
**Owner:** Diane Rocher
**Stack:** Make.com · TeamTailor API · Make Data Stores · Slack
**Team:** MyCompany (Make org xxx) → folder **secretfolder** (id `xxx`)

---

## Overview

Two Make scenarios that together turn TeamTailor pipeline data into recurring Slack
reporting for open roles, with a cumulative wrap-up once a role is filled. They are not
chained to each other directly (no "Run a scenario" / webhook link between them) — they
communicate purely through two shared **Data Stores**, plus a manual status change on a
row in the first one. This supersedes the single-scenario V1 tracked at
[`../make/02_generate_weekly_reportxxx`](../make/02_generate_weekly_reportxxx.py)
(scenario `xxx`), which stayed active for comparison and has since been split into
this two-scenario design.

```
                         ┌─────────────────────────┐
                         │   TT Roles Registry      │   Data Store xxx
                         │   (status: active/       │   one row per role
                         │    filled/reported)      │
                         └──────────┬───────────────┘
                                    │ status = active
                                    ▼
                    ┌───────────────────────────────┐
                    │ Scenario 1               │
                    │ "TeamTailor-report V2"         │   weekly, Fri 10:00
                    │ 1 SearchRecord (DS1, active)   │
                    │ 2 Python: pull TT API, build   │
                    │   weekly Slack report          │
                    │ 3 AddRecord → DS2 (upsert by   │
                    │   job_id_week_of)               │
                    │ 4 Slack: post weekly report     │
                    └──────────┬──────────────────────┘
                               ▼
                  ┌─────────────────────────┐
                  │  TT Weekly Snapshots     │  Data Store xxx
                  │  one row per             │  (accumulates every Friday
                  │  job_id + week_of        │   this scenario runs)
                  └──────────┬───────────────┘
                             │ read by job_id
                             ▼
        (someone flips the DS1 row's status: active → filled — manual, see below)
                             │
                    ┌────────────────────────────────┐
                    │ Scenario 2                │
                    │ "…Final Summary V2"             │   on-demand
                    │ 1 SearchRecord (DS1, filled)     │
                    │ 2 SearchRecord (DS2, by job_id)  │
                    │ 3 BasicAggregator → array         │
                    │ 4 Python: cumulative summary       │
                    │ 5 Slack: post "Role Filled!"       │
                    │ 6 UpdateRecord DS1 → status=reported│
                    └────────────────────────────────┘
```

---

## Scenario 1 — `TeamTailor-report V2 (diane)`

| Field | Value |
|---|---|
| Schedule | Weekly, Fridays at 10:00 |
| Folder | Myfolder (`xxx`) |
| Blueprint | [`blueprints/teamtailor-weekly-report.blueprint.json`](blueprints/teamtailor-weekly-report.blueprint.json) |
| Local script copy | [`scripts/01_weekly_report.py`](scripts/01_weekly_report.py) |

1. **datastore:SearchRecord** on *TT Roles Registry* (DS `xxx`), filtered
   `status = active` → iterates once per open role.
2. **code:ExecuteCode (Python)** — calls the TeamTailor API for that `job_id`
   (job details + paginated job-applications with candidate/stage includes), computes
   the stage breakdown, sourced-vs-inbound split, HM-stage conversion funnel and
   threshold-based alerts (days-open, pending-review backlog, low screen-pass rate,
   high use-case fail rate, low offer-acceptance), and renders it all into one Slack
   `mrkdwn` message.
3. **datastore:AddRecord** into *TT Weekly Snapshots* (DS `xxx`), key
   `{job_id}_{week_of}`, `overwrite: true` — so a re-run on the same day updates rather
   than duplicates that week's row.
4. **slack:CreateMessage** posts the weekly report to the role's `channel` (read off
   the DS1 row, not hardcoded), using the shared Slack connection.

## Scenario 2 — `TeamTailor-report — Final Summary V2 (diane)`

| Field | Value |
|---|---|
| Schedule | On-demand only — no trigger fires it automatically |
| Folder | Myfolder (`xxx`) |
| Blueprint | [`blueprints/teamtailor-final-summary.blueprint.json`](blueprints/teamtailor-final-summary.blueprint.json) |
| Local script copy | [`scripts/02_final_summary.py`](scripts/02_final_summary.py) (reads `snapshots` from [`scripts/fixtures/example_snapshots.json`](scripts/fixtures/example_snapshots.json) standalone, instead of `{{3.array}}`) |

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

---

## The manual link between the two scenarios

Nothing in either blueprint sets a role's status to `filled` (or creates the initial
`active` row). Both transitions on *TT Roles Registry* are manual today:

- **Seeding a role** (`status = active`, plus `job_id`, `job_title`, `channel`,
  `date_added`) — add the row by hand in the Make Data Store UI when a role opens.
  (Not produced by the [intake automation](../make/Make_Scenarios_Intake_Automation.md) —
  that flow explicitly creates no TeamTailor job draft.)
- **Marking a role filled** (`status = filled`, `date_filled` set) — edit the row by
  hand once TeamTailor shows the role as filled, then run scenario 7106762 on demand.

This is the main gap worth closing if this pipeline gets more roles running through it:
either a scheduled scenario 2 (searching all `filled` rows on its own) or a TeamTailor
webhook that flips the status automatically would remove the manual step.

---

## Data Stores

### TT Roles Registry (`xxx`) — one row per role

| Field | Type | Notes |
|---|---|---|
| `job_id` | text | TeamTailor job ID |
| `job_title` | text | |
| `channel` | text | Slack channel the reports post to |
| `status` | text | `active` → `filled` → `reported`, hand-edited (see above) |
| `date_added` | date | Used for `days_open` / `days_to_fill` |
| `date_filled` | date | Set when marking a role filled |

### TT Weekly Snapshots (`172312`) — one row per `job_id` + week

| Field | Type |
|---|---|
| `job_id` | text |
| `week_of` | date |
| `total_all`, `total_active`, `total_rejected`, `total_sourced`, `total_inbound` | number |
| `days_open` | number |
| `alerts` | text (`\|`-joined) |
| `hired_candidates` | text (comma-joined names) |

---

## Keys and IDs to collect before rebuilding this from scratch

| What | Where to find it |
|---|---|
| TeamTailor API token | TeamTailor → Settings → Integrations → API key (currently hardcoded as `PASTE_TOKEN_HERE` in module 2 of scenario xxx — move to a Make connection/env before reuse) |
| Slack connection | Make → Connections (id `xxx`, shared by both scenarios' `slack:CreateMessage` modules) |
| *TT Roles Registry* data store ID | `xxx`, structure `xxx` |
| *TT Weekly Snapshots* data store ID | `xxx`, structure `xxx` |
| People folder ID | `xxx` |
