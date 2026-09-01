"""
Make module (code:ExecuteCode, Python) inside Route 1 of scenario
"Intake Meeting automation V2 (Diane)" — generates deterministic sourcing
search strings, as opposed to the AI-generated sourcing brief text.

This is a local copy of the code running inside the Make scenario, adapted
to run standalone for testing/versioning:
  - skills / role / department come from env vars instead of the Make pills
    {{join(4.skills; "|")}} / {{4.role}} / {{4.department}}, which are
    filled in from the extraction step's parsed JSON (module 7 in the main
    chain, referenced downstream as module id 4's fields).

Its `result` feeds two places in the live scenario:
  - linkedin_query / google_query / meetup_query are posted verbatim in the
    Route 1 sourcing-brief Slack message.
  - role_bucket is used by the nested Airtable "already sourced" lookup to
    match previously-sourced leads by category.
linkedin_valid / google_valid are computed but not consumed by anything
downstream in the live blueprint — kept here for parity with the original.

See ../README.md for the full automation and where this fits among the
other modules.
"""
import os

from dotenv import load_dotenv

load_dotenv()

# In Make these are injected by pills: {{join(4.skills; "|")}} / {{4.role}} / {{4.department}}
skills_raw = os.environ.get("SKILLS", "Python|Kubernetes|Terraform")
role = os.environ.get("ROLE", "Senior Platform Engineer")
department = os.environ.get("DEPARTMENT", "Engineering")

skills_raw = skills_raw.replace("\\", "")

skills = [s.strip() for s in skills_raw.split("|") if s.strip()]
titles = [role] if role else []
locations = ["France", "Portugal", "Spain"]


def fmt(t):
    return f'"{t}"' if " " in t else t


def or_group_hack(terms):
    if not terms:
        return ""
    if len(terms) == 1:
        return fmt(terms[0])
    return "(" + fmt(terms[0]) + " " + " ".join(f"OR({fmt(t)})" for t in terms[1:]) + ")"


def or_group_plain(terms):
    if not terms:
        return ""
    return "(" + " OR ".join(fmt(t) for t in terms) + ")"


if skills:
    rest = " ".join(f"AND({fmt(s)})" for s in skills[1:])
    skill_part = f"{fmt(skills[0])} {rest}".strip()
else:
    skill_part = ""
title_part = f" AND({or_group_hack(titles)})" if titles else ""
location_part = f" AND({or_group_hack(locations)})" if locations else ""
linkedin_query = (skill_part + title_part + location_part).strip()
linkedin_valid = len(linkedin_query) <= 1000

skills_group = f"({' '.join(skills)})" if skills else ""
title_group = ""
if titles:
    title_group = " (" + " OR ".join(f'intitle:"{t}"' if " " in t else f"intitle:{t}" for t in titles) + ")"
location_group = f" {or_group_plain(locations)}" if locations else ""
exclusions = " -site:linkedin.com -site:indeed.com -site:glassdoor.com"
google_query = f"{skills_group}{title_group}{location_group}{exclusions}".strip()
google_words = len(google_query.split())
google_valid = google_words <= 32

meetup_skills_group = or_group_plain(skills)
meetup_location_group = or_group_plain(locations)
meetup_query = f"site:meetup.com {meetup_skills_group} {meetup_location_group} inurl:/members/".strip()

CATEGORIES = [
    ("AI / ML / Data Science", ["ml", "machine learning", "data scien", "ai engineer", "ai researcher", "nlp", "llm", " ai "]),
    ("Frontend / Mobile / Fullstack", ["frontend", "front-end", "front end", "mobile", "ios", "android", "fullstack", "full-stack", "full stack"]),
    ("Backend", ["backend", "back-end", "back end", "api engineer", "server-side"]),
    ("DevOps / SRE / Infrastructure", ["devops", "sre", "site reliability", "infrastructure", "platform engineer", "cloud engineer", "kubernetes"]),
    ("Design", ["designer", "design", "ux", "ui "]),
    ("Product", ["product manager", "product owner", " pm ", "product lead"]),
    ("Marketing / Growth", ["marketing", "growth", "seo", "content"]),
    ("Sales / AE / BDR / SDR", ["sales", "account executive", " ae ", "bdr", "sdr"]),
    ("Customer Success / Enablement", ["customer success", "customer support", "enablement", "support"]),
    ("Revenue / BizDev / Partnerships", ["revenue", "biz dev", "business development", "partnership"]),
    ("Investor / VC / Advisor", ["investor", "vc", "venture", "advisor"]),
    ("Other Engineering", ["engineer", "engineering", "qa", "test", "security", "embedded", "firmware"]),
]

text = f" {role.lower()} {department.lower()} "
role_bucket = "Other / HR / Finance / Unknown"
for name, kws in CATEGORIES:
    if any(kw in text for kw in kws):
        role_bucket = name
        break

result = {
    "linkedin_query": linkedin_query,
    "linkedin_valid": linkedin_valid,
    "google_query": google_query,
    "google_valid": google_valid,
    "meetup_query": meetup_query,
    "role_bucket": role_bucket,
}

if __name__ == "__main__":
    import json

    print(json.dumps(result, indent=2, ensure_ascii=False))
