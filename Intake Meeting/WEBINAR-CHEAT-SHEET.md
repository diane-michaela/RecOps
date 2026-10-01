# Cheat sheet — From meeting recording to structured data

Companion to the Make Community Live Session with Diane Rocher (PhantomBuster):
the **common path** of the intake meeting scenario, built live from a blank canvas.
It covers everything from the webhook to the router, with the production settings
of V3, the simplified version.

- **Importable blueprint:** [`blueprints/intake-meeting-v3-common-path.blueprint.json`](blueprints/intake-meeting-v3-common-path.blueprint.json)
- **Full scenario** (all 3 routes after the router): [`blueprints/intake-meeting-automation-v3.blueprint.json`](blueprints/intake-meeting-automation-v3.blueprint.json), explained in [`README.md`](README.md)

---

## What you build

```
[1] Webhooks: Custom webhook          ← fileName + fileId of the new Gemini doc
      filter: file name contains "Intake Meeting"
[2] Google Drive: Download a File     ← the Gemini doc as Markdown: Notes tab + Transcript tab
[3] Anthropic Claude: Create a Prompt ← extract typed role data (Haiku 4.5)
[4] JSON: Parse JSON                  ← strip code fences, parse
[5] Anthropic Claude: Create a Prompt ← TA screening kit, 11 lines
[6] Router                            ← your branches go here
```

**Three ideas behind it:**
1. **Filter before you spend.** Gemini writes notes for *every* meeting. The filter sits before the first module that costs anything, so a filtered-out meeting costs 1 operation.
2. **Give the model the full source, and tell it which one wins.** Gemini puts the summary and the transcript in two tabs of the same doc, and a Markdown export brings both. The prompt says: if they disagree, trust the transcript.
3. **Extract once, into typed data, before the router.** Use fixed values for anything you route on. Every branch then just maps fields.

**Build it in a fresh scenario, in this order.** Make numbers modules in the order you create them and never reuses a number. The prompts below refer to modules by number (`{{2.data}}`, `{{3.textResponse}}`, `{{4.role}}`), so if your numbers differ, map those values by clicking instead of pasting.

---

## Module settings

### [1] Custom webhook
- Maximum number of results: `1`
- In production, a small **Google Apps Script** watching the Meet Recordings Drive folder calls it when a new "Notes by Gemini" doc lands, with `fileName` and `fileId`. This replaced a native "Watch Files in a Folder" trigger polling every 15 minutes, which spent operations checking an empty folder.
- To test it by hand, paste this in a browser:
  ```
  <your-webhook-url>?fileName=Intake Meeting - Senior Platform Engineer - Notes by Gemini&fileId=<doc ID>
  ```

### Filter (link 1 → 2)
`{{1.fileName}}` · Text operators: **contains** · `Intake Meeting`

It relies on a naming convention: intake meetings are titled "Intake Meeting — <role>".

### [2] Download a File (the Gemini doc)
- File: `{{1.fileId}}`
- **Convert Google Documents Files to Format: Markdown** (under advanced settings). The export contains **both tabs**, Notes then Transcript, and keeps the headings and the `[Name](mailto:…)` attendee links the prompt reads. PDF or Word is unreadable for the model; plain text loses the mailto links.

### [3] Anthropic Claude: Create a Prompt (extraction)
- Use **Create a Prompt**, not "Simple Text Prompt" (that one runs on Make's AI tokens instead of your Anthropic connection).
- Model: Claude Haiku 4.5 · Max tokens: `800` · Temperature: `0` (type it: an empty field means 1)
- Messages → Role: `user` · Input type: **Multiple content blocks** · Content → Type: **Text** → paste the [extraction prompt](#extraction-prompt-module-3)
- No tools, no system prompt, extended thinking off.
- The output field is `textResponse`.

### [4] JSON: Parse JSON
- JSON string:
  ```
  {{trim(replace(replace(3.textResponse; "```json"; emptystring); "```"; emptystring))}}
  ```
  Use Make's `emptystring` keyword, not `""`: the editor can silently drop a pasted `""`, the code fences stay, and Parse JSON fails with "Source is not valid JSON".
- Data structure: either create one with the 12 fields of the prompt (`skills` and `key_responsibilities` as arrays, the rest as text; Make's **Generate** button builds it from a sample of the JSON), or leave it empty and run once so Make infers the fields. With a data structure, the fields are mappable in later modules before any run.

### [5] Anthropic Claude: Create a Prompt (TA screening kit)
- Model: Claude Haiku 4.5 · Max tokens: `800` · Temperature: `0`
- Messages: same setup as [3], with the [screening kit prompt](#screening-kit-prompt-module-5)
- Read a line downstream with `{{trim(get(split(5.textResponse; newline); 5))}}`, which returns line 5.

### [6] Router
Add your own branches here. In the full scenario there are three: a Slack hiring channel with a sourcing brief, a Notion TA Screening Kit, and a Notion JD v2. See [`README.md`](README.md).

---

## The transcript lookup I removed (and why)

The previous version (V2) assumed Gemini saved the transcript as a **separate** Drive file, so it had three more modules between [2] and [3]:

- **Google Drive: Make an API Call.** URL `/v3/files` · Method `GET` · `fields` = `files(id,name)` · `q` =
  ```
  name contains '{{replace(1.fileName; " - Notes by Gemini"; "")}}' and name contains 'Transcript' and '<DRIVE_FOLDER_ID>' in parents and trashed = false
  ```
  It takes the notes' file name, removes " - Notes by Gemini", and searches for a file with that name plus "Transcript" in the folder, not trashed. There's no native "find the matching document" module; the API call gives you the full Drive query language in one field.
- **Text parser: Match pattern** on the API response, to pull the file ID (first capture group, `$1`):
  ```
  "id":\s*"([a-zA-Z0-9_-]{15,})"
  ```
- **Google Drive: Download a File** of that ID, as plain text.
- **Resume error handlers** on the API call and the download, so a missing transcript wouldn't stop the run.

**What actually happened:** Gemini writes the transcript as a tab, not a file. The search always returned an empty list, the download failed on every run, and the Resume handlers kept every run green. Claude was getting the transcript the whole time, through the Markdown export in [2]. Removing the lookup saves 3 operations per run.

**The lesson:** open every module's output at least once on a real run. An error handler that swallows an *expected* failure can hide a step that never works. And if you do need to find a separate document, the Drive API + regex pattern above is the way: just check the document exists.

---

## Extraction prompt (module 3)

Replace `<RECRUITER_NAME>` with the recruiter's name.

```
Read this intake meeting document and extract the role information. The document below is a Gemini meeting doc: a summary ("Notes" tab) followed by the full meeting transcript ("Transcript" tab) — if the two disagree on any detail, trust the transcript. Return ONLY a valid JSON object with exactly these fields, no extra text, no markdown:
{"role":"job title","role_slug":"lowercase-hyphenated-title","department":"department name","seniority":"junior or mid or senior or lead or head or vp or director","hm_name":"First Last — REQUIRED disambiguation: if more than one non-recruiter attendee could plausibly be the hiring manager (for example their manager or a skip-level exec also attended the meeting), pick the person who owns the day-to-day of the team this role reports into and speaks about it as their own headcount/need — not whoever talks the most or holds the most senior title. Only pick the more senior attendee if the document explicitly states they are the hiring manager for this specific role.","skills":["skill1","skill2","skill3"],"team":"team name","hm_email":"REQUIRED lookup: the transcript's attendee/invitee list near the top has each person's name immediately followed by a mailto: link, e.g. [Full Name](mailto:email@company.com). Find the entry whose name matches hm_name and return that exact email address. The recruiter (<RECRUITER_NAME>) is a different attendee in that same list — do not return her email. Only use empty string if the attendee list itself is completely absent from the document.","project_context":"one sentence on why this role is opening","key_responsibilities":["responsibility 1","responsibility 2","responsibility 3"],"summary":"one sentence role description","category":"REQUIRED — pick the SINGLE closest match from this exact fixed list, copy the text exactly as written, no variations: DevOps / SRE / Infrastructure, Backend, Frontend / Mobile / Fullstack, AI / ML / Data Science, Other Engineering, Product, Design, Marketing / Growth, Sales / AE / BDR / SDR, Customer Success / Enablement, Revenue / BizDev / Partnerships, Investor / VC / Advisor, Other / HR / Finance / Unknown"}

Meeting document (Gemini "Notes" tab followed by the full "Transcript" tab):
{{2.data}}
```

**Why each rule is there:**
- **"If the two disagree, trust the transcript":** summaries simplify, for example "mid-level" when the manager clearly said senior.
- **Hiring manager disambiguation:** skip-level managers join intakes. Without this rule, the model picks the most senior title or whoever talks the most.
- **`hm_email` from the mailto list:** later branches use it to find the right calendar event and invite the manager.
- **`category` from a fixed list:** anything you'll route on later gets a fixed list, not free text. Here it's meant for a sourcing step that opens a pre-filtered candidate view per category, where a made-up 14th value would break the lookup.
- **800 max tokens:** the JSON is usually 300–450 tokens. It's a ceiling, not a cost: you pay for what the model writes. Too low, and the JSON gets cut off and Parse JSON fails.

## Screening kit prompt (module 5)

```
Generate a TA screening kit for this role. Output exactly 11 lines, one value per line, in this exact order:

Line 1: [must-have skill 1]
Line 2: [must-have skill 2]
Line 3: [must-have skill 3]
Line 4: [must-have skill 4]
Line 5: [project context: 250-320 words, one continuous line — explain what the team does, why this role exists, and the broader business context/mission behind it. Describe needs and gaps functionally, never by naming a person.]
Line 6: [screening question 1]
Line 7: [screening question 2]
Line 8: [screening question 3]
Line 9: [red flag 1]
Line 10: [red flag 2]
Line 11: [closing recommendation]

Role: {{4.role}}, Seniority: {{4.seniority}}, Department: {{4.department}}, HM: {{4.hm_name}}
Project context: {{4.project_context}}
Team: {{4.team}}, Summary: {{4.summary}}

Rules:
- Skills and red flags: max 15 words each
- Screening questions: max 30 words each
- Closing: max 20 words
- Project context (Line 5) is a HARD 250-320 word requirement — count as you write and keep going until you are genuinely in that range; a short paragraph is a failure to follow instructions. Cover, in order: (1) what the team builds and its mission, in concrete detail — not one generic sentence; (2) the team's current situation and the specific gap or growth driving this opening; (3) why this matters for the wider business/product; (4) what this person will actually do and own day to day. Write in full, specific sentences — expand on each point rather than compressing it.
- Project context (Line 5): NEVER include any person's name — not the hiring manager, not any existing team member, not anyone being replaced or reinforced. Describe the team and the need functionally (e.g. "the team needs additional senior expertise" or "this role covers a recent departure"), never by name. If the role exists to replace or reinforce a specific person, do not say so explicitly — focus on the team's mission, what it's building, and why the headcount is needed now.
- NO double quotes anywhere in the output
- NO backslashes anywhere in the output
- Each value MUST be on a single line (no line breaks within a value)
- Output ONLY the 11 values, one per line, nothing else
```

**Why lines and not JSON, and why "NO double quotes":** this text ends up inside JSON bodies sent to the Notion API later. One stray `"` breaks the call, and Make formulas have no function to escape it. Stop it at the source in the prompt, and build API bodies with **JSON → Transform to JSON** instead of typing `"{{…}}"` into a raw body.

---

## Demo docs (fictional)

Create these as Google Docs to reproduce the demo. A real Gemini doc has two tabs; one doc with a Notes section followed by a Transcript section exports the same way for this scenario. The planted details are intentional:
- **The summary says "mid-level" and the transcript says senior**, so "trust the transcript" is visible.
- **A VP attends**, so the hiring-manager rule is visible.
- **Attendees are mailto links**, so `hm_email` gets extracted.

### `Intake Meeting - Senior Platform Engineer - Notes by Gemini`
```
# 📝 Notes

## Intake Meeting - Senior Platform Engineer

Invited: [Jordan Lee](mailto:recruiter@example.com), [Alex Martin](mailto:alex.martin@example.com), [Sam Leroy](mailto:sam.leroy@example.com)

### Summary
The Platform team is opening a mid-level Platform Engineer role. The team runs infrastructure on
AWS with Kubernetes and Terraform and is migrating part of it to Pulumi. Sam Leroy (VP Engineering)
joined to share context on the observability roadmap.

### Next steps
- The recruiter shares a sourcing brief and a first batch of profiles by Friday.

# 📖 Transcript

## Intake Meeting - Senior Platform Engineer - Transcript

### 00:00:00
Jordan Lee: Thanks for joining. Alex, tell me about the need.
Alex Martin: So this is my team's headcount. We're taking over observability and CI/CD from the
product squads and we can't absorb it with the people we have.
Sam Leroy: And from my side, observability is a priority for next year, so this matters.

### 00:01:12
Jordan Lee: What level are we targeting?
Alex Martin: Senior. Five years minimum. I need someone who has run Kubernetes in production and
carried on-call, not someone learning it on the job.
Jordan Lee: Must-haves?
Alex Martin: Kubernetes in production, Terraform or Pulumi, AWS, strong Linux. Datadog, ArgoCD
and Go are nice to have.

### 00:02:30
Jordan Lee: Location?
Alex Martin: Paris hybrid, or remote in France.
```

### `Weekly Sync - Notes by Gemini` (the filter should stop this one)
```
Weekly Sync
Notes by Gemini

Summary
Team reviewed last week's metrics and priorities.
```

**Expected result for the Senior Platform Engineer doc:** `seniority` = senior, `hm_name` = Alex Martin, `hm_email` = alex.martin@example.com, `category` = DevOps / SRE / Infrastructure.
