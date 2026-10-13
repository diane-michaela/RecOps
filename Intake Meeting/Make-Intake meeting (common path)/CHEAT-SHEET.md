# Intake meeting → structured data · copy-paste kit

From the Make Community Live Session *“From meeting recording to structured data”*. Everything you need to rebuild the common path: a recorded Google Meet intake goes in, a typed data bundle and a screening kit come out, ready for any route after the router.

The blueprint is in this folder ([intake-meeting-common-path.blueprint.json](intake-meeting-common-path.blueprint.json)): import it in Make (… › Import Blueprint), then pick your own connections, webhook and data structures.

**Jump to the three things you'll copy:**
- [The Google Apps Script](#step-2--google-apps-script)
- [Claude prompt 1 · extraction](#3--anthropic-claude--create-a-prompt-extraction)
- [Claude prompt 2 · screening kit](#5--anthropic-claude--create-a-prompt-screening-kit) (with its JSON schema)

---

## What you need

- **Google Workspace with Gemini**: in Meet, turn on *Take notes with Gemini* **and** transcription. The notes doc then has two tabs, Notes and Transcript.
- **A naming convention**: title every intake calendar event `Intake Meeting - <role>`. Gemini copies the title into the doc name, and the Make filter reads it.
- **Make**, with a Google Drive connection and an Anthropic connection (your own API key).

---

## Step 1 · Two keys

| Key | Where to find it |
|---|---|
| `FOLDER_ID` | Google Drive › open the folder Gemini saves notes to (“Meet Recordings”) › the end of the URL, after `/folders/` |
| `WEBHOOK_URL` | Make › your Custom webhook module › **Copy address to clipboard**. Treat it like a password. |

## Step 2 · Google Apps Script

script.google.com › New project › paste this › fill in the two keys › Save.

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

The four functions:

| Function | What it does | When to run it |
|---|---|---|
| `installTrigger` | Tells Google to run `checkNewNotes` every minute | **Once**, by hand, after pasting the script |
| `checkNewNotes` | The watcher: looks at the folder and sends each new “Notes by Gemini” doc to Make, once | Runs on its own every minute. Run it by hand to send a doc right away |
| `sendToMake` | The messenger: posts `fileName` + `fileId` to the webhook | **Never by hand**: it needs a file, so on its own it fails with “cannot read getName of undefined” |
| `removeTrigger` | Stops the every-minute check | When you want to turn it off |

Then:
1. Save, then in the function dropdown next to **Run**, choose **`installTrigger`** › Run. The dropdown shows `sendToMake` first: always check what it says before clicking Run.
2. Approve the authorization. “This app isn't verified” is normal for your own script: Advanced › Go to the project.
3. Check **Triggers** (clock icon): `checkNewNotes`, every minute. Check **Executions**: a new doc shows “Sent to Make”.

---

## Step 3 · Make, module by module

> **Module numbers.** The formulas below (`{{2.data}}`, `3.textResponse`, `{{4.role}}`…) assume you add the modules in exactly this order in a new scenario. Make never reuses a number, so if yours differ, paste the text and then **re-map each bubble by clicking** the right module in the mapping panel.

### 1 · Webhooks › Custom webhook
Add › name it › Save › Copy address to clipboard (that's your `WEBHOOK_URL`).

### Filter · on the link between 1 and 2
`fileName` · Text operators: **Contains** · `Intake Meeting`

### 2 · Google Drive › Download a File
- File ID: map `fileId` from the webhook.
- Show advanced settings › **Convert Google Documents Files to Format: Markdown**. The default is Word, which Claude can't read: the run either fails as too long, or stays green with invented answers. Markdown keeps both tabs, the headings and the attendees' mailto links.

### 3 · Anthropic Claude › Create a Prompt (extraction)
Model: Claude Haiku 4.5 · Max tokens: 800 · Temperature: **0** (type it, empty means 1) · Messages › Role user › Multiple content blocks › Text:

```
Read this intake meeting document and extract the role information. The document below is a Gemini meeting doc: a summary ("Notes" tab) followed by the full meeting transcript ("Transcript" tab) — if the two disagree on any detail, trust the transcript. Return ONLY a valid JSON object with exactly these fields, no extra text, no markdown:
{"role":"job title","role_slug":"lowercase-hyphenated-title","department":"department name","seniority":"junior or mid or senior or lead or head or vp or director","hm_name":"First Last — REQUIRED disambiguation: if more than one non-recruiter attendee could plausibly be the hiring manager (for example their manager or a skip-level exec also attended the meeting), pick the person who owns the day-to-day of the team this role reports into and speaks about it as their own headcount/need — not whoever talks the most or holds the most senior title. Only pick the more senior attendee if the document explicitly states they are the hiring manager for this specific role.","skills":["every skill the hiring manager names as required, usually 3 to 8"],"team":"team name","hm_email":"REQUIRED lookup: the transcript's attendee/invitee list near the top has each person's name immediately followed by a mailto: link, e.g. [Full Name](mailto:email@company.com). Find the entry whose name matches hm_name and return that exact email address. Recruiters are different attendees in that same list — never return a recruiter's email. Recruiter names: <YOUR NAME>. Only use empty string if the attendee list itself is completely absent from the document.","project_context":"one sentence on why this role is opening","key_responsibilities":["every main responsibility the hiring manager describes, usually 3 to 6"],"summary":"one sentence role description"}

Meeting document (Gemini "Notes" tab followed by the full "Transcript" tab):
{{2.data}}
```

Replace `<YOUR NAME>` with the recruiter(s) who run your intakes, comma-separated.

### 4 · JSON › Parse JSON
JSON string:
```
{{trim(replace(replace(3.textResponse; "```json"; emptystring); "```"; emptystring))}}
```
Type `emptystring`, not `""`: the Make editor drops a pasted `""`.

Data structure: Create a data structure › **Generate** › paste this sample › Save:
```json
{"role":"Senior Platform Engineer","role_slug":"senior-platform-engineer","department":"Engineering","seniority":"senior","hm_name":"Alex Martin","skills":["Kubernetes","Terraform","Go"],"team":"Platform","hm_email":"alex.martin@example.com","project_context":"One sentence on why the role opens.","key_responsibilities":["Own the CI/CD platform","Lead infra migrations"],"summary":"One sentence role description."}
```

### 5 · Anthropic Claude › Create a Prompt (screening kit)
Model: Claude Haiku 4.5 · Max tokens: **1200** · Temperature: **0** · Text:

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

Output Format: **JSON schema**:
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

### 6 · JSON › Parse JSON (the kit)
JSON string:
```
{{trim(replace(replace(5.textResponse; "```json"; emptystring); "```"; emptystring))}}
```
Data structure: Generate from this sample:
```json
{"must_have_skill_1":"a","must_have_skill_2":"b","must_have_skill_3":"c","must_have_skill_4":"d","project_context":"e","screening_question_1":"f","screening_question_2":"g","screening_question_3":"h","red_flag_1":"i","red_flag_2":"j","closing_recommendation":"k"}
```

### 7 · Router
Add your routes: Slack, Notion, a new JD… Each one just maps fields from modules 4 and 6.

---

## Every time you create a new webhook

1. Make: create the webhook › Copy address.
2. Apps Script: paste it into `WEBHOOK_URL` › Save.
3. **Save the scenario** in Make.
4. Webhook module › **Redetermine data structure** (it starts listening).
5. Put a notes doc in the folder › Apps Script: run `checkNewNotes` (if the doc was already there, take it out, run `checkNewNotes`, put it back, run it again).
6. Make shows “Successfully determined” › OK › Save.

## Troubleshooting

| You see | It means |
|---|---|
| `410 · There is no scenario listening` | The scenario isn't saved yet |
| `410 · Webhook is no longer active` | The script has an old webhook URL |
| `getName of undefined` in Apps Script | You ran `sendToMake`: run `checkNewNotes` |
| Nothing in the script log, no error | The doc was already sent once: take it out, run `checkNewNotes`, put it back |
| `prompt is too long` | Module 2 is still on Word, not Markdown |
| A green run with made-up answers | A mapping points at the wrong module: Claude got empty fields. Open each module's input |
| `fileId` shows as an outlined bubble | The webhook never received data: Redetermine data structure and send a doc |
