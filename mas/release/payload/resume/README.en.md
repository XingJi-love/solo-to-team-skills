# Resume an interrupted task · 1.3

Open [the English checkpoint reader](从这里续办.html#en) from the extracted folder. Keep the HTML and both JavaScript files together. The language button preserves your selected files. The page works offline in a current browser.

The saved reviewer label `review` has been supported since version 1.1. The current reader is version 1.3; this package is its 1.3a copy edit.

## Recover the next action

1. Choose the most recent agreed `checkpoint.json`. Then choose the actual deliverable and all available review, dispatch and receipt records. The second chooser accepts multiple files.
2. Read **What the records show**. If a file has changed, compare it with the reviewed version. If it is missing, recover it from the original work rather than restarting the task.
3. If only review is outstanding, look for the review of this exact version before commissioning one. If only dispatch is outstanding, first check whether the file was already sent. If only receipt is outstanding, the recipient checks the original delivery and records the file actually received. Completion requires all four matching files.

Display labels are translated. Original task text, destination, filenames, source references and author-entered actions stay in their original language. Contact the role named in the original agreement when the source itself needs clarification.

## Record progress

In **Create or update checkpoint.json**, enter a task ID, the original request, the latest change (use “none” if applicable), and the agreed return destination. Include the deliverable version, the next owner and concrete action, and the work to preserve. The original destination is locked when a populated checkpoint is opened.

**Register this file** computes a local SHA-256 and replaces the entry in the editable copy. Use it only after checking the file and version. **Download checkpoint copy** writes a separate JSON file. Put the agreed copy and original evidence together in the shared task folder.

## Make a source record

In **Prepare a record**, choose your role and copy the read-only, one-line `CHECKPOINT` draft. Add it beneath your own UTF-8 text account of what actually happened. Preserve the exact machine keys, destination and generated fingerprints. In that line, fill only these three author fields:

| Your role | actor | source_ref | result |
|---|---|---|---|
| Independent reviewer who opened this version | `reviewer` | Traceable review location | `pass` or `revise` |
| Lead who actually sent the file | `lead` | Original dispatch location | `sent` |
| Recipient who actually obtained and checked the file | `recipient` | Original receipt location | `received` |

A receipt draft also requires the registered dispatch file. The reader verifies its bytes, binding and destination, then includes its SHA-256 as `dispatch_sha256`. Keep one binding line of the appropriate kind per record. Keep any explanation in the record body.

A `dispatch.target` mismatch shows the original destination and the recorded value. If the original sender confirms the file reached the correct place, keep the original record, make a linked correction and register the corrected dispatch file and fingerprint. Reuse the reviewed deliverable and original send. If it went to the wrong place, establish where it actually went.

**For the lead at kickoff** — Save the current request, change, destination and prior passes in the checkpoint. Bind each existing record to the corresponding version. Each author attests only to their own action.

**For the lead resuming work** — Open the same checkpoint and files, recover the last evidenced stage and hand the next action to its owner. The reader checks bytes and relationships. The original host or author establishes what actually happened. The page does not dispatch messages, sign for other people, or grant permissions.
