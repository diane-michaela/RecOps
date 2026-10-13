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
