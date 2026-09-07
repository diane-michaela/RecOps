"""
Make module (code:ExecuteCode, Python) inside Route 1 of scenario
"Intake Meeting automation V2 (Diane)" — generates a deterministic Airtable
search formula plus Meetup search strings, as a complement to the AI-generated
sourcing brief text.

This is a local copy of the code running inside the Make scenario, adapted
to run standalone for testing/versioning:
  - skills / role / department come from env vars instead of the Make pills
    {{join(4.skills; "|")}} / {{4.role}} / {{4.department}}, which are
    filled in from the extraction step's parsed JSON (referenced downstream
    as module id 4's fields).

Its `result` feeds three places in the live scenario:
  - airtable_formula gates the "already applied to this role" Airtable
    cross-check (module 103) — an AND of an OR-of-role/title/skill SEARCH()
    matches with a fixed France/Portugal/Spain location OR-group. No
    maxRecords limit is set on that lookup downstream — a broad match can
    return a large result set (known accepted risk, not yet capped).
  - role_bucket is used by the nested "already sourced" Airtable lookup
    (module 104, also uncapped) to match previously-sourced leads by category.
  - meetup_queries (one `site:meetup.com "<term>" "France" "members"` line
    per term, up to 3 terms drawn from skills + role) is posted verbatim in
    the Route 1 sourcing-brief Slack message.
  - role_clean / department_clean (quote/backslash/newline-stripped versions
    of role and department) are only used internally to build the formula
    above — not consumed elsewhere downstream.

An earlier revision of this module generated LinkedIn Recruiter and Google
X-ray boolean strings instead of the Airtable formula — that logic moved
into the AI-generated sourcing brief prompt (which now writes its own
strict/broad boolean keywords and GitHub keywords), and this module's role
narrowed to the two deterministic lookups above.

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


def sanitize(s):
    s = s.replace("\\", "")
    for ch in ['"', "“", "”", "„", "‟", "«", "»", "″"]:
        s = s.replace(ch, "")
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return s.strip()


role_clean = sanitize(role)
department_clean = sanitize(department)

skills_raw = skills_raw.replace("\\", "")
skills = [s.strip() for s in skills_raw.split("|") if s.strip()]

skill_terms = [sanitize(s).lower() for s in skills if sanitize(s)][:6]
role_conditions = [
    f'SEARCH(LOWER("{role_clean.lower()}"); LOWER({{latest_role_applied}})) > 0',
    f'SEARCH(LOWER("{role_clean.lower()}"); LOWER({{suggested_title}})) > 0',
    f'SEARCH(LOWER("{department_clean.lower()}"); LOWER({{keywords}})) > 0',
] + [
    f'SEARCH(LOWER("{skill}"); LOWER({{keywords}})) > 0' for skill in skill_terms
]
airtable_formula = (
    "AND(\n  OR(\n    "
    + ",\n    ".join(role_conditions)
    + '\n  ),\n  OR({location} = "France", {location} = "Portugal", {location} = "Spain")\n)'
)

meetup_terms = skills[:2] + ([role] if role else [])
meetup_terms = meetup_terms[:3]
meetup_queries = "\n".join(f'site:meetup.com "{t}" "France" "members"' for t in meetup_terms)

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
    "meetup_queries": meetup_queries,
    "role_bucket": role_bucket,
    "role_clean": role_clean,
    "department_clean": department_clean,
    "airtable_formula": airtable_formula,
}

if __name__ == "__main__":
    import json

    print(json.dumps(result, indent=2, ensure_ascii=False))
