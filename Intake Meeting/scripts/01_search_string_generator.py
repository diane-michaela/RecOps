"""
Make module (code:ExecuteCode, Python) inside Route 1 of scenario
"Intake Meeting automation V2" (module 93): deterministic ATS keyword
search formula, an "already sourced" link picked by role category, and
Meetup search strings, as a complement to the AI-generated sourcing brief.

This is a local copy of the code running inside the Make scenario, adapted
to run standalone for testing/versioning:
  - skills / category come from env vars instead of the Make pills
    {{join(4.skills; "|")}} / {{4.category}}, which are filled in from the
    extraction step's parsed JSON (module 4).

Its `result` feeds three places in the live scenario:
  - airtable_formula drives the "already in the ATS" Airtable search
    (module 103, maxRecords 50). It ANDs the top 2-3 *strong* skills: generic
    terms in WEAK_TERMS (react, python, sql, communication...) are pushed to
    the back, because a single common skill matches hundreds of candidates.
    On a real ~6,400-candidate base: "react" matched 518, "aws" 284,
    "ansible" 2, "pulumi" 1. Rare terms are the signal. Plus a fixed
    France/Portugal/Spain location OR-group.
  - sourced_link is posted as-is by module 106: one pre-filtered Airtable
    Interface page per role category (13 categories, the same fixed list the
    extraction prompt must choose from), instead of searching the sourced-
    candidates table (it has no per-candidate skill field worth searching).
  - meetup_queries (one `site:meetup.com "<term>" "France" "members"` line
    per term, first 2 skills) is posted in the Route 1 sourcing-brief message.

History: an earlier revision OR'd role title / department / category with every
skill, so one generic skill match ("react") surfaced candidates regardless of the
role, and ran a second uncapped Airtable search for already-sourced leads
(module 104). Both were replaced on 2026-09-11 by the AND-of-strong-skills
formula and the category link above; module 104 was deleted.

Replace every <AIRTABLE_INTERFACE_PAGE_URL for ...> with your own per-category
page (or any filtered view link). See ../README.md for the full automation.
"""
import os

# In Make these are injected by pills: {{join(4.skills; "|")}} / {{4.category}}
skills_raw = os.environ.get("SKILLS", "Kubernetes|Terraform|Pulumi|AWS|Python")
category = os.environ.get("CATEGORY", "DevOps / SRE / Infrastructure").strip()

CATEGORY_LINKS = {
    "DevOps / SRE / Infrastructure": "<AIRTABLE_INTERFACE_PAGE_URL for DevOps / SRE / Infrastructure>",
    "Backend": "<AIRTABLE_INTERFACE_PAGE_URL for Backend>",
    "Frontend / Mobile / Fullstack": "<AIRTABLE_INTERFACE_PAGE_URL for Frontend / Mobile / Fullstack>",
    "AI / ML / Data Science": "<AIRTABLE_INTERFACE_PAGE_URL for AI / ML / Data Science>",
    "Other Engineering": "<AIRTABLE_INTERFACE_PAGE_URL for Other Engineering>",
    "Product": "<AIRTABLE_INTERFACE_PAGE_URL for Product>",
    "Design": "<AIRTABLE_INTERFACE_PAGE_URL for Design>",
    "Marketing / Growth": "<AIRTABLE_INTERFACE_PAGE_URL for Marketing / Growth>",
    "Sales / AE / BDR / SDR": "<AIRTABLE_INTERFACE_PAGE_URL for Sales / AE / BDR / SDR>",
    "Customer Success / Enablement": "<AIRTABLE_INTERFACE_PAGE_URL for Customer Success / Enablement>",
    "Revenue / BizDev / Partnerships": "<AIRTABLE_INTERFACE_PAGE_URL for Revenue / BizDev / Partnerships>",
    "Investor / VC / Advisor": "<AIRTABLE_INTERFACE_PAGE_URL for Investor / VC / Advisor>",
    "Other / HR / Finance / Unknown": "<AIRTABLE_INTERFACE_PAGE_URL for Other / HR / Finance / Unknown>",
}
sourced_link = CATEGORY_LINKS.get(category, "<AIRTABLE_INTERFACE_URL>")

WEAK_TERMS = {
    "javascript", "typescript", "python", "java", "html", "css", "git",
    "agile", "scrum", "react", "node.js", "nodejs", "sql", "c#", ".net",
    "php", "communication", "leadership", "teamwork", "problem solving",
    "project management", "stakeholder management", "excel", "powerpoint",
}


def sanitize(s):
    s = s.replace("\\", "")
    for ch in ['"', "“", "”", "„", "‟", "«", "»", "″"]:
        s = s.replace(ch, "")
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return s.strip()


skills_raw = skills_raw.replace("\\", "")
skills = [sanitize(s).lower() for s in skills_raw.split("|") if sanitize(s)]

strong = [s for s in skills if s not in WEAK_TERMS]
weak = [s for s in skills if s in WEAK_TERMS]

NUM_TERMS = 3
skill_terms = (strong + weak)[:NUM_TERMS]

# AND of the top strong skills against the ATS {keywords} field
and_conditions_103 = [f'SEARCH(LOWER("{s}"); LOWER({{keywords}})) > 0' for s in skill_terms]
airtable_formula = (
    "AND(\n    "
    + ";\n    ".join(and_conditions_103)
    + ';\n    OR({location} = "France"; {location} = "Portugal"; {location} = "Spain")\n)'
)

meetup_terms = skills[:2]
meetup_queries = "\n".join(f'site:meetup.com "{t}" "France" "members"' for t in meetup_terms)

result = {
    "meetup_queries": meetup_queries,
    "airtable_formula": airtable_formula,
    "sourced_link": sourced_link,
}

if __name__ == "__main__":
    for key, value in result.items():
        print(f"--- {key}\n{value}\n")
