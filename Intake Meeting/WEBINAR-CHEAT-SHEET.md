# Cheat sheet — From meeting recording to structured data

Companion to the Make Community Live Session with Diane Rocher (PhantomBuster):
the **common path** of the intake-meeting scenario, built live from a blank canvas.
It covers everything from the webhook to the router, with the real settings.

- **Importable blueprint:** [`blueprints/intake-meeting-common-path.blueprint.json`](blueprints/intake-meeting-common-path.blueprint.json). Import it (… › Import Blueprint), then pick your own connections, webhook and data structures.

---

## What you build

```
[1] Webhooks: Custom webhook          ← fileName + fileId of the new Gemini doc
      filter: file name contains "Intake Meeting"
[2] Google Drive: Download a File     ← the Gemini doc as Markdown: Notes tab + Transcript tab
[3] Anthropic Claude: Create a Prompt ← Claude A: extract typed role data (Haiku 4.5)
[4] JSON: Parse JSON                  ← strip code fences, parse into 11 role fields
[5] Anthropic Claude: Create a Prompt ← Claude B: TA screening kit, as JSON (JSON schema)
[6] JSON: Parse JSON                  ← parse the kit into 11 named fields
[7] Router                            ← your branches go here
```

**Three ideas behind it:**
1. **Filter before you spend.** Gemini writes notes for *every* meeting. The filter sits before the first module that costs anything, so a filtered-out meeting costs 1 operation.
2. **One doc, two tabs.** Gemini puts the summary and the full transcript in the same doc, in two tabs. A Markdown export brings both, so one download gives the model the whole meeting. Tell it which one to trust when they disagree.
3. **Extract once, into typed data, before the router.** Use fixed values for anything you route on. Every branch then just maps fields.

> **Module numbers.** The formulas below (`{{2.data}}`, `3.textResponse`, `{{4.role}}`…) assume you add the modules in exactly this order in a new scenario. Make never reuses a number, so if yours differ, paste the text and then **re-map each bubble by clicking** the right module.

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

### [2] Google Drive: Download a File
- File: `{{1.fileId}}`
- Show advanced settings › **Convert Google Documents Files to Format: Markdown**. The default is Word, which Claude can't read: the run either fails as too long, or stays green with invented answers. Markdown keeps both tabs (Notes, then Transcript), the headings and the `[Name](mailto:…)` attendee links the prompt reads.

### [3] Anthropic Claude: Create a Prompt (Claude A, extraction)
- Model: Claude Haiku 4.5 · Max tokens: `800` · Temperature: `0` (type it: empty means 1)
- Messages › Role user › Multiple content blocks › Text: see [Extraction prompt](#extraction-prompt-claude-a) below
- The output field is `textResponse`.

### [4] JSON: Parse JSON (role)
**Why:** Claude returns one block of text. It looks like JSON, but for Make it's a single string: you can't map `role` or `hm_email` from it. Parse JSON turns it into real fields, one bubble per value.
- JSON string:
  ```
  {{trim(replace(replace(3.textResponse; "```json"; emptystring); "```"; emptystring))}}
  ```
  Read it from the inside out: take Claude's answer, remove the opening ` ```json `, remove the closing ` ``` `, trim the spaces. Type `emptystring`, not `""`: the Make editor drops a pasted `""`, the fences stay, and Parse JSON fails.
- Data structure: **Create a data structure › Generate**, paste this sample, Save. Strict: **No**.
  ```json
  {"role":"Senior Platform Engineer","role_slug":"senior-platform-engineer","department":"Engineering","seniority":"senior","hm_name":"Alex Martin","skills":["Kubernetes","Terraform","Go"],"team":"Platform","hm_email":"alex.martin@example.com","project_context":"One sentence on why the role opens.","key_responsibilities":["Own the CI/CD platform","Lead infra migrations"],"summary":"One sentence role description."}
  ```
  With it, the fields are mappable in the next module before any run. Without it, Parse JSON still works, but Make only learns the fields after a first run: run, map the next module, run again.

### [5] Anthropic Claude: Create a Prompt (Claude B, screening kit)
- Model: Claude Haiku 4.5 · Max tokens: `1200` · Temperature: `0`
- Messages › Role user › Multiple content blocks › Text: see [Screening kit prompt](#screening-kit-prompt-claude-b) below
- **Output Format: JSON schema**, paste:
  ```json
  {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "must_have_skill_1": { "type": "string" },
      "must_have_skill_2": { "type": "string" },
      "must_have_skill_3": { "type": "string" },
      "must_have_skill_4": { "type": "string" },
      "project_context": { "type": "string" },
      "screening_question_1": { "type": "string" },
      "screening_question_2": { "type": "string" },
      "screening_question_3": { "type": "string" },
      "red_flag_1": { "type": "string" },
      "red_flag_2": { "type": "string" },
      "closing_recommendation": { "type": "string" }
    },
    "required": [
      "must_have_skill_1", "must_have_skill_2", "must_have_skill_3", "must_have_skill_4",
      "project_context",
      "screening_question_1", "screening_question_2", "screening_question_3",
      "red_flag_1", "red_flag_2",
      "closing_recommendation"
    ]
  }
  ```
- Max tokens is 1200, not 800: in JSON, every value carries its key and quotes, and a 250–320 word context can otherwise get cut mid-JSON.

### [6] JSON: Parse JSON (kit)
- JSON string:
  ```
  {{trim(replace(replace(5.textResponse; "```json"; emptystring); "```"; emptystring))}}
  ```
- Data structure: **Create a data structure › Generate**, paste this sample, Save. Strict: **No**. Field names must match the JSON keys exactly.
  ```json
  {"must_have_skill_1":"a","must_have_skill_2":"b","must_have_skill_3":"c","must_have_skill_4":"d","project_context":"e","screening_question_1":"f","screening_question_2":"g","screening_question_3":"h","red_flag_1":"i","red_flag_2":"j","closing_recommendation":"k"}
  ```

### [7] Router
Add your own branches here: a Slack hiring channel, a Notion screening kit page, a new JD… Each one just maps fields from [4] and [6].

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

## Screening kit prompt (Claude B)

```
Generate a TA screening kit for this role.

Return only one valid JSON object. Do not use Markdown code fences. Do not add any explanation before or after the JSON object.

Use exactly these keys:
must_have_skill_1
must_have_skill_2
must_have_skill_3
must_have_skill_4
project_context
screening_question_1
screening_question_2
screening_question_3
red_flag_1
red_flag_2
closing_recommendation

Every value must be a string. Do not add any other keys.

Role: {{4.role}}
Seniority: {{4.seniority}}
Department: {{4.department}}
Hiring manager: {{4.hm_name}}
Project context: {{4.project_context}}
Team: {{4.team}}
Summary: {{4.summary}}

Rules:
- Skills and red flags: maximum 15 words each.
- Screening questions: maximum 30 words each.
- Closing recommendation: maximum 20 words.
- project_context is a hard 250–320 word requirement.
- project_context must cover, in this order:
  1. What the team builds and its mission, in concrete detail.
  2. The team’s current situation and the specific gap or growth driving this opening.
  3. Why this matters for the wider business or product.
  4. What this person will do and own day to day.
- Write project_context in full, specific sentences. Do not produce a short generic paragraph.
- project_context must never include any person’s name, including the hiring manager, existing team members, or anyone being replaced or reinforced.
- Describe the team’s needs functionally and never name a person.
- If the role replaces or reinforces someone, do not mention that person.
- Return exactly the 11 requested keys.
- Return only valid JSON.
```

**Why JSON with named keys:** an earlier version asked for 11 plain lines and read them by position (line 5 = the context). One extra line from the model shifted everything, silently. With named keys and a JSON schema, every value has a name, the format is enforced, and the next step maps names.

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
