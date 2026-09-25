"""
Make module (code:ExecuteCode, Python) inside Route 1 of scenario
"Intake Meeting automation V2" (module 93): deterministic Meetup search
strings, posted with the AI-generated "Sourcing & Market Intelligence" brief.

This is a local copy of the code running inside the Make scenario, adapted
to run standalone for testing/versioning: skills come from an env var instead
of the Make pill {{join(4.skills; "|")}} (module 4 = the parsed extraction).

Output: meetup_queries, one `site:meetup.com "<skill>" "France" "members"`
line per skill (first 2 skills), used by module 81.

History: until 2026-09-25 this module also built an Airtable ATS keyword
formula (AND of the rarest skills) and a per-category "already sourced" link.
Those cross-checks were removed from the intake scenario and will come back
as a separate "Sourcing" scenario.

See ../README.md for the full automation.
"""
import os

# In Make this is injected by the pill {{join(4.skills; "|")}}
skills_raw = os.environ.get("SKILLS", "Kubernetes|Terraform|Pulumi")


def sanitize(s):
    s = s.replace("\\", "")
    for ch in ['"', "“", "”", "„", "‟", "«", "»", "″"]:
        s = s.replace(ch, "")
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return s.strip()


skills_raw = skills_raw.replace("\\", "")
skills = [sanitize(s).lower() for s in skills_raw.split("|") if sanitize(s)]

meetup_terms = skills[:2]
meetup_queries = "\n".join(f'site:meetup.com "{t}" "France" "members"' for t in meetup_terms)

result = {
    "meetup_queries": meetup_queries,
}

if __name__ == "__main__":
    print(result["meetup_queries"])
