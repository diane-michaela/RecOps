"""
Make module 4 ("Python") of scenario "TeamTailor-report — Final Summary V2
(diane)" — code:ExecuteCode, Python
https://eu1.make.com/67084/scenarios/7106762/edit

This is a local copy of the code running inside the Make scenario, adapted to
run standalone for testing/versioning:
  - job_id / job_title / channel / date_added / date_filled come from env
    vars instead of the Make iterator pills ({{1.data.*}}), which are filled
    in from a SearchRecord on "TT Roles Registry" (id 172310, filtered
    status = filled).
  - `snapshots` — normally {{3.array}}, the output of module 3's
    BasicAggregator over a SearchRecord on "TT Weekly Snapshots" (id 172312,
    filtered by job_id) — is read from a local JSON file instead. See
    fixtures/example_snapshots.json for the expected shape, produced by
    01_weekly_report.py's `result` (minus `slack_message`) accumulating
    week over week.

In Make, this module's `result` is consumed by a Slack CreateMessage posting
`result["slack_message"]`, followed by an UpdateRecord that sets the DS1
row's status to "reported". See ../README.md for the full picture.

To push a change back into Make: re-hardcode the {{1.data.*}} pills and
{{3.array}} as they were, and keep this file as the source of truth for the
report logic.
"""
import json
import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()

_here = os.path.dirname(os.path.abspath(__file__))

# In Make these are injected by module 1's SearchRecord: {{1.data.*}}
job_id = os.environ.get("JOB_ID", "7463157")
job_title = os.environ.get("JOB_TITLE", "Senior Product Expert")
channel = os.environ.get("SLACK_CHANNEL", "#product-expert-recruitment-2026")
date_added = os.environ.get("DATE_ADDED", "2026-06-01")
date_filled = os.environ.get("DATE_FILLED", date.today().isoformat())

# In Make this is {{3.array}} — the BasicAggregator output over DS2 rows for this job_id
snapshots_file = os.environ.get(
    "SNAPSHOTS_FILE", os.path.join(_here, "fixtures", "example_snapshots.json")
)
with open(snapshots_file) as f:
    snapshots = json.load(f)

if not snapshots:
    raise ValueError(f"No Weekly Snapshots found in DS2 for job_id={job_id} — nothing to summarize.")

snapshots.sort(key=lambda row: row["week_of"])
latest = snapshots[-1]

weeks_tracked = len(snapshots)
days_to_fill = (date.fromisoformat(date_filled[:10]) - date.fromisoformat(date_added[:10])).days

hired_names = (latest.get("hired_candidates") or "").strip()
hired_line = hired_names if hired_names else "see TeamTailor for details"

total_all = latest["total_all"]
total_active = latest["total_active"]
total_rejected = latest["total_rejected"]
total_sourced = latest["total_sourced"]
total_inbound = latest["total_inbound"]


def conv(num, denom):
    return round((num / denom) * 100) if denom > 0 else 0


slack_message = f"""🎉 *Role Filled — {job_title}!*

Huge thanks to the whole hiring team — hiring managers, interviewers, and everyone who gave their time along the way. Great work! 🙌

Below is the cumulative result of that effort throughout the process.

*🏆 Hired:* {hired_line}
📅 Tracked over *{weeks_tracked}* week{"s" if weeks_tracked != 1 else ""}  |  ⏱️ Time to fill: *{days_to_fill} days*

*🔢 Final Overview*
- 👥 Total candidates: *{total_all}* | ✅ Active: *{total_active}* ({conv(total_active, total_all)}%) | ❌ Rejected: *{total_rejected}* ({conv(total_rejected, total_all)}%)
- 🎯 Sourced: *{total_sourced}* ({conv(total_sourced, total_all)}%) vs 📥 Inbound: *{total_inbound}* ({conv(total_inbound, total_all)}%)"""

result = {
    "slack_message": slack_message,
    "job_id": job_id,
    "channel": channel,
    "weeks_tracked": weeks_tracked,
    "days_to_fill": days_to_fill,
    "hired_candidates": hired_names,
}

if __name__ == "__main__":
    print(json.dumps(result, indent=2, ensure_ascii=False))
