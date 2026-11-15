# Solo to Team · MAS

[中文](README.md) · [Local edition](index.html#en)

## Hand your unfinished project to an AI team.

Give the lead a partial draft, then change one requirement. Production revises it, a separate reviewer opens the result, and the lead brings the approved version back to your original conversation.

**A table uses the spare kit as planned. How many kits should come back?** Production draft R1 — Still expects 1 kit. Delivered revision R2 — Expects 0; records table and time.

Two forms from a WorkBuddy run on a fictional event. Evidence comes from local observation and retained files. Platform runtime logs were unavailable. [See a real correction](proof/README.md)

## Which platform do you use?

Pick a platform where your model already works. Start with the three delivery roles: lead, producer and reviewer.

### Grok Bot

Reuse your existing seats, or create the three roles from the included cards. [Get the first-order pack](adapters/grok/first-order.zip)

An existing team handled the change from 20 to 24. Oversight flagged a handoff issue; the team revised and reviewed R2, then delivered it in the lead’s original conversation. Whole-team import is unverified.

### OpenMausBot

Choose Templates → Import. Check first for a department of the same name: adding again creates another copy. [Get the team file](adapters/openmaus/team.openmaus.json) · [Read the import guide](adapters/openmaus/README.md)

Three seats created manually on this Mac ran the first order and returned two attachments after independent review. One directory action required approval. The downloadable file passed native import/export functions in isolated storage. Its real-account UI import remains untested. Check each seat’s approval settings before sending work.

### WorkBuddy

The bundled installer targets WorkBuddy 5.9.3 on macOS only and has no Apple notarization. Read the setup guide, choose the route that fits your Mac, then pick a dedicated work folder. [Open the setup guide](adapters/workbuddy/README.md) · [Choose either route on the offline start page](adapters/workbuddy/start.html)

The bundled 0.1.0 original completed its first order on a previously configured private team. After one targeted revision, the reviewer reopened R2. The lead returned the file and its review. Any example support email in the original is a placeholder; do not contact it.

### DeepSeek Harness

Extract the standard project.zip. Find the two sibling folders 一人成阵-DSH (the project) and 试用者第二步 (the change card). In the Harness workspace picker, select 一人成阵-DSH itself. It contains inputs and the hidden .dsh folder. Do not select the outer extraction folder or .dsh. In a new chat, type / and select solo-to-team. After the lead acknowledges the draft, send the card from 试用者第二步. [Get the standard project ZIP](adapters/deepseek/project.zip) · [DS Bot v0.3.2 guide (team setup awaits a live test)](adapters/deepseek/ds-bot-guide.zip)

For a custom ZIP exported by the team builder, create a new empty folder and extract the archive contents directly into it. Select that folder, which now contains team.definition.json and .dsh.

The configured standard team on this Mac used separate production and review subtasks. Local observation and retained files document six returns. R7 had no blockers and five advisory findings. The lead returned two openable attachments in the original conversation. Cloud review covered the delivery. Independent onboarding by an outside newcomer remains untested.

## Run your first order

1. **Send the partial draft**　Give the lead the root file brief/01-intake.md, a 20-person activity draft. Ask it to confirm the version and fixed conditions. The earlier brief inside each fixed starter is also usable. [Open the root activity brief](brief/01-intake.md) · [Delivery check](delivery-check/README.md). If the deliverable gives a date, which input establishes it? With no source, mark the date as pending. Which downstream notices must reflect the change? Only the bilingual root brief includes the added check for date sources and downstream notices. Earlier runs used its preceding version.

2. **Change the requirement**　After the lead identifies the draft, send the change to 24 in the same conversation. Keep the venue, budget cap and time window. [Open the change request](brief/02-change.md)

3. **Inspect the delivery**　Open both the event pack and the independent review returned by the lead. Match their versions, find the change in the tables, and check how the review findings were resolved.

## Try another order: community maintenance

Give the lead the [four maintenance bookings](examples/maintenance/01-intake.md). Once it acknowledges the draft, send the [building closure](examples/maintenance/02-change.md). Compare the revised schedule with the notices drafted for the affected sites. After delivery, [compare the observed outcome](examples/maintenance/outcome.md).

## What else comes with the team?

<details><summary>What has been verified for custom teams?</summary>

The builder checks that production and review have different role IDs. The run record and the file the reviewer opened are needed to establish who operated those seats and whether review was independent.

The fixed starter and a team exported by the editor are separate artifacts with separate evidence. In the team’s local observation, a renamed four-seat team ran in DeepSeek Harness from a project exported by this version of the builder. The UI showed three subtasks; retained files cover assignments, review and the fourth seat’s return. Cloud review had no platform runtime logs. A custom four-seat OpenMausBot department was imported with the native 0.1.148 data layer in isolated storage. A run in a real user account through its UI remains untested. The team holds the receipts and import records for these two observations outside this package; readers cannot independently verify them from this download.

</details>

- [Build your own team](team-builder/index.html#en)　Edit roles, groups, portraits and handoffs locally, or inspect the [three-seat starter](team/team.json).

- [The original four skills](skills-original/)　Use the included skills on their own.

- [Bilingual evidence](proof/README.md)　Inspect the original cells, findings and review scope.

All four entries share the division of work. The evidence comes from the team’s own runs. Setup and review evidence are listed separately for each host.
