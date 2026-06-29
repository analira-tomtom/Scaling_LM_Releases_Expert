---
name: report_expert
description: Generate the weekly workstream section for the Workstreams Weekly Report using the project-local expert config. Pass the workstream name or number as argument (e.g. /report_expert WS6, /report_expert WS3, /report_expert Leg Boosting).
---

Generate the workstream section for the current week's Workstreams Weekly Report.

## Step 1 — Resolve the workstream

The user has passed a workstream identifier as an argument (e.g. "WS6", "WS3", "Leg Boosting", "Scaling LM Releases").

1. List all files matching `skills/*/resources/config.json` relative to the ai-playbook plugin root.
2. Read each config file and check its `aliases` array for a case-insensitive match against the argument.
3. If exactly one match is found, proceed with that workstream's config.
4. If no match is found, list all available workstreams (name + aliases from each config) and ask the user to clarify.

## Step 2 — Load context

From the matched `config.json`, extract:
- `confluence.pages` — main page ID and weekly reports CQL query
- `slack.channels` — IDs and purposes
- `jira` — project and example tickets
- `report.required_sections` and `report.format_note`

## Step 3 — Fetch live data

Run these fetches in parallel where possible:

1. **Weekly reports**: fetch the two most recent weekly reports using the CQL query. Read both: the latest gives the current state to build on; the previous gives the format reference and WoW baseline.
2. **Slack**: read the primary channel (first in the channels list) for updates from the **last 72 hours** — Slack is the source of truth for recent changes.
3. **Main Confluence page**: read for current high-level status.
4. **JIRA**: follow any open ticket links referenced in the above sources for active issues.

## Step 4 — Generate the report section

Write the workstream section for the current week's Workstreams Weekly Report:

- **Match the format exactly** from the most recent report entry — same headings, same table column order, same structure.
- Highlight what is **new or changed** compared to the previous week.
- Include every section listed in `config.json` under `report.required_sections`.
- Include the overall **RAG status**. If proposing a change from the previous week's RAG, explain why with evidence.
- Cite the source (Confluence page, JIRA ticket, Slack channel) for each material statement.
- Do not include updates older than 2–3 weeks unless they remain active blockers.

## Step 5 — Prompt to save

After generating the report, ask:
*"Would you like me to copy this to the Confluence draft report page? Run `/save_expert [workstream]` to do so."*
