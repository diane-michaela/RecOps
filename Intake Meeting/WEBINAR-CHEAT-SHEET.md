# Cheat sheet — From meeting recording to structured data

Companion to the Make Community Live Session with Diane Rocher (PhantomBuster):
the **common path** of the "Intake Meeting automation V2" scenario, built live from
a blank canvas. It covers everything from the webhook to the router, with the real
production settings.

- **Importable blueprint:** [`blueprints/intake-meeting-v2-common-path.blueprint.json`](blueprints/intake-meeting-v2-common-path.blueprint.json)
- **Full scenario** (all 3 routes after the router): [`blueprints/intake-meeting-automation.blueprint.json`](blueprints/intake-meeting-automation.blueprint.json), explained in [`README.md`](README.md)

---

## What you build

```
[1] Webhooks: Custom webhook          ← fileName + fileId of the new Gemini doc
      filter: file name contains "Intake Meeting"
[2] Google Drive: Download a File     ← the "Notes by Gemini" summary (markdown)
[3] Google Drive: Make an API Call    ← find the matching Transcript doc
[4] Text parser: Match pattern        ← pull the transcript's file ID
[5] Google Drive: Download a File     ← the transcript (plain text)
[6] Anthropic Claude: Create a Message ← extract typed role data (Haiku 4.5)
[7] JSON: Parse JSON                  ← strip code fences, parse
[8] Anthropic Claude: Create a Message ← TA screening kit, 11 lines
[9] Router                            ← your branches go here
```

**Three ideas behind it:**
1. **Filter before you spend.** Gemini writes notes for *every* meeting. The filter sits before the first module that costs anything, so a filtered-out meeting costs 1 operation. A full intake run is 21–25.
2. **Two documents, one meeting.** Gemini saves the summary and the transcript as separate docs, and the trigger only gives you one. Find the other with a Drive search, then give the model both and tell it which to trust.
3. **Extract once, into typed data, before the router.** Use fixed values for anything you route on. Every branch then just maps fields.

---

## Module settings

### [1] Custom webhook
- Maximum number of results: `1`
- In production, a small **Google Apps Script bound to the Drive folder** calls it when a new doc lands, with `fileName` and `fileId`. This replaced a native "Watch Files in a Folder" trigger polling every 15 minutes.
- To test it by hand, paste this in a browser:
  ```
  <your-webhook-url>?fileName=Intake Meeting — Senior Platform Engineer - Notes by Gemini&fileId=<doc ID>
  ```

**The Google Apps Script** (script.google.com › New project › paste › fill in the two values › Save):

```javascript
// Watches a Google Drive folder and calls a Make webhook for every new
// "Notes by Gemini" doc. Paste into a new project at script.google.com.

// 1. Make: open your Custom webhook module → "Copy address to clipboard".
//    Treat it like a password: anyone who has it can trigger your scenario.
const WEBHOOK_URL = 'PASTE_YOUR_WEBHOOK_URL_HERE';

// 2. Google Drive: open the folder Gemini saves notes to (Meet Recordings),
//    and copy the end of its URL, after /folders/
const FOLDER_ID = 'PASTE_YOUR_FOLDER_ID_HERE';

// Sends only two things: the file name (to filter on) and the file ID (to download it).
function sendToMake(file) {
  UrlFetchApp.fetch(WEBHOOK_URL, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ fileName: file.getName(), fileId: file.getId() }),
  });
  console.log('Sent to Make: ' + file.getName());
}

// Sends each Notes doc once. It remembers what it already sent in `seen`.
function checkNewNotes() {
  const props = PropertiesService.getScriptProperties();
  const seen = JSON.parse(props.getProperty('seen') || '[]');
  const files = DriveApp.getFolderById(FOLDER_ID).getFiles();
  const inFolder = [];

  while (files.hasNext()) {
    const file = files.next();
    if (!file.getName().endsWith('Notes by Gemini')) continue;
    inFolder.push(file.getId());
    if (!seen.includes(file.getId())) sendToMake(file);
  }
  props.setProperty('seen', JSON.stringify(inFolder));
}

// 3. Run this once by hand: Google then runs checkNewNotes every minute, for free.
function installTrigger() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('checkNewNotes').timeBased().everyMinutes(1).create();
}

// To stop it.
function removeTrigger() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
}
```

| Function | What it does | When to run it |
|---|---|---|
| `installTrigger` | Tells Google to run `checkNewNotes` every minute | **Once**, by hand, after pasting the script |
| `checkNewNotes` | The watcher: sends each new “Notes by Gemini” doc in the folder to Make, once | Runs on its own every minute. Run it by hand to send a doc right away |
| `sendToMake` | The messenger: posts `fileName` + `fileId` to the webhook | **Never by hand**: it needs a file, so on its own it fails with “cannot read getName of undefined” |
| `removeTrigger` | Stops the every-minute check | When you want to turn it off |

### Filter (link 1 → 2)
`{{1.fileName}}` · Text operators: **contains** · `Intake Meeting`

It relies on a naming convention: intake meetings are titled "Intake Meeting — <role>".

### [2] Download a File (the notes)
- File: `{{1.fileId}}`
- Google Docs export format: **text/markdown**. This keeps the headings and the `[Name](mailto:…)` attendee links the prompt reads.

### [3] Google Drive: Make an API Call (find the transcript)
- URL: `/v3/files` · Method: `GET`
- Query string `q`:
  ```
  name contains '{{replace(1.fileName; " - Notes by Gemini"; "")}}' and name contains 'Transcript' and '<DRIVE_MEET_RECORDINGS_FOLDER_ID>' in parents and trashed = false
  ```
- Query string `fields`: `files(id,name)`

It depends on how your Gemini files are named. Check a real notes/transcript pair and adjust the two `name contains` parts to match.

### [4] Text parser: Match pattern
- Pattern: `"id":\s*"([a-zA-Z0-9_-]{15,})"`
- Text: `{{3.body}}`
- Global match: No · Case sensitive: Yes · Continue the execution of the route even if the module finds no matches: **Yes**
- Map the result as `{{4.$1}}`, the first capture group.

### [5] Download a File (the transcript)
- File: `{{4.$1}}`
- Google Docs export format: **text/plain**

### [6] Anthropic Claude: Create a Message (extraction)
- Model: Claude Haiku 4.5 · Max tokens: `800` · Temperature: `0`
- Prompt: see [Extraction prompt](#extraction-prompt-module-6) below
- The output field is `textResponse`.

### [7] JSON: Parse JSON
- JSON string:
  ```
  {{trim(replace(replace(6.textResponse; "```json"; emptystring); "```"; emptystring))}}
  ```
  Type `emptystring`, not `""`: the Make editor drops a pasted `""`, the fences stay, and Parse JSON fails.
- Data structure: **Create a data structure › Generate**, paste this sample, Save. Strict: **No**.
  ```json
  {"role":"Senior Platform Engineer","role_slug":"senior-platform-engineer","department":"Engineering","seniority":"senior","hm_name":"Alex Martin","skills":["Kubernetes","Terraform","Go"],"team":"Platform","hm_email":"alex.martin@example.com","project_context":"One sentence on why the role opens.","key_responsibilities":["Own the CI/CD platform","Lead infra migrations"],"summary":"One sentence role description."}
  ```
  With it, the fields are mappable in the next module before any run. Without it, Parse JSON still works, but Make only learns the fields after a first run: run, map the next module, run again.

### [8] Anthropic Claude: Create a Message (TA screening kit)
- Model: Claude Haiku 4.5 · Max tokens: `800` · Temperature: `0`
- Prompt: see [Screening kit prompt](#screening-kit-prompt-module-8) below
- Read a line downstream with `{{trim(get(split(8.textResponse; newline); 5))}}`, which returns line 5.

### [9] Router
Add your own branches here. In the full scenario there are three: a Slack hiring channel with a sourcing brief, a Notion TA Screening Kit, and a Notion JD v2. See [`README.md`](README.md).

---

## Extraction prompt (Claude A)

Replace `<RECRUITER_NAME>` with the recruiter's name (several names: comma-separated). `{{2.data}}` is the Drive download, exported as Markdown: it already contains the Notes tab **and** the Transcript tab.

```
Read this intake meeting document and extract the role information. The document below is a Gemini meeting doc: a summary ("Notes" tab) followed by the full meeting transcript ("Transcript" tab) — if the two disagree on any detail, trust the transcript. Return ONLY a valid JSON object with exactly these fields, no extra text, no markdown:
{"role":"job title","role_slug":"lowercase-hyphenated-title","department":"department name","seniority":"junior or mid or senior or lead or head or vp or director","hm_name":"First Last — REQUIRED disambiguation: if more than one non-recruiter attendee could plausibly be the hiring manager (for example their manager or a skip-level exec also attended the meeting), pick the person who owns the day-to-day of the team this role reports into and speaks about it as their own headcount/need — not whoever talks the most or holds the most senior title. Only pick the more senior attendee if the document explicitly states they are the hiring manager for this specific role.","skills":["every skill the hiring manager names as required, usually 3 to 8"],"team":"team name","hm_email":"REQUIRED lookup: the transcript's attendee/invitee list near the top has each person's name immediately followed by a mailto: link, e.g. [Full Name](mailto:email@company.com). Find the entry whose name matches hm_name and return that exact email address. Recruiters are different attendees in that same list — never return a recruiter's email. Recruiter names: <RECRUITER_NAME>. Only use empty string if the attendee list itself is completely absent from the document.","project_context":"one sentence on why this role is opening","key_responsibilities":["every main responsibility the hiring manager describes, usually 3 to 6"],"summary":"one sentence role description"}

Meeting document (Gemini "Notes" tab followed by the full "Transcript" tab):
{{2.data}}
```

**Why each rule is there:**
- **"If the two disagree, trust the transcript":** summaries simplify, for example "mid-level" when the manager clearly said senior.
- **Hiring manager disambiguation:** skip-level managers join intakes. Without this rule, the model picks the most senior title or whoever talks the most.
- **`hm_email` from the mailto list:** later branches use it to find the right calendar event and invite the manager.
- **`seniority` from a fixed list:** anything you'll route on later gets a fixed list, not free text. If the model can write 'senior-ish', a later filter on 'senior' silently misses it.

## Screening kit prompt (module 8)

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

Role: {{7.role}}, Seniority: {{7.seniority}}, Department: {{7.department}}, HM: {{7.hm_name}}
Project context: {{7.project_context}}
Team: {{7.team}}, Summary: {{7.summary}}

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

Create these as Google Docs in one folder to reproduce the live demo. The planted details are intentional:
- **The summary says "mid-level" and the transcript says senior**, so "trust the transcript" is visible.
- **A VP attends**, so the hiring-manager rule is visible.
- **Attendees are mailto links**, so `hm_email` gets extracted.

### `Intake Meeting — Senior Platform Engineer - Notes by Gemini`
```
Intake Meeting — Senior Platform Engineer
Notes by Gemini

Attendees: [Diane Rocher](mailto:recruiter@example.com), [Alex Martin](mailto:alex.martin@example.com), [Sam Leroy](mailto:sam.leroy@example.com)

Summary
The Platform team is opening a mid-level Platform Engineer role. The team runs infrastructure on
AWS with Kubernetes and Terraform and is migrating part of it to Pulumi. Sam Leroy (VP Engineering)
joined to share context on the observability roadmap.

Next steps
- Diane to share a sourcing brief and a first batch of profiles by Friday.
```

### `Intake Meeting — Senior Platform Engineer - Transcript`
```
Intake Meeting — Senior Platform Engineer
Transcript

Invited: [Diane Rocher](mailto:recruiter@example.com), [Alex Martin](mailto:alex.martin@example.com), [Sam Leroy](mailto:sam.leroy@example.com)

Diane Rocher: Thanks for joining. Alex, tell me about the need.
Alex Martin: So this is my team's headcount. We're taking over observability and CI/CD from the
product squads and we can't absorb it with the people we have.
Sam Leroy: And from my side, observability is a priority for next year, so this matters.
Diane Rocher: What level are we targeting?
Alex Martin: Senior. Five years minimum. I need someone who has run Kubernetes in production and
carried on-call, not someone learning it on the job.
Diane Rocher: Must-haves?
Alex Martin: Kubernetes in production, Terraform or Pulumi, AWS, strong Linux. Datadog, ArgoCD
and Go are nice to have.
Diane Rocher: Location?
Alex Martin: Paris hybrid, or remote in France.
```

### `Weekly Sync - Notes by Gemini` (the filter should stop this one)
```
Weekly Sync
Notes by Gemini

Summary
Team reviewed last week's metrics and priorities.
```

**Expected result for the Senior Platform Engineer docs:** `seniority` = senior, `hm_name` = Alex Martin, `hm_email` = alex.martin@example.com, `category` = DevOps / SRE / Infrastructure.
