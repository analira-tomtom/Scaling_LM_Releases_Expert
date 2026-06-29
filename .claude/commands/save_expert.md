---
name: save_expert
description: Save the most recently generated weekly report section to the Confluence draft page. Pass the workstream name or number as argument (e.g. /save_expert WS6, /save_expert WS3). Always run /report_expert first to generate content for this session.
---

Push the weekly report generated in this session to the Confluence draft page.

## Step 1 — Resolve the workstream

The user has passed a workstream identifier as an argument (e.g. "WS6", "WS3", "Leg Boosting").

1. List all files matching `skills/*/resources/config.json` relative to the ai-playbook plugin root.
2. Read each config file and check its `aliases` array for a case-insensitive match against the argument.
3. If no match is found, list all available workstreams (name + aliases) and ask the user to clarify.

## Step 2 — Locate the report

Find the most recently generated report section from the current session.

If no report has been generated in this session, tell the user to run `/report_expert [workstream]` first and stop here.

## Step 3 — Push to Confluence

1. From the matched `config.json`, read `report.draft_page_id`.
2. Use the Atlassian MCP `updateConfluencePage` tool to replace the content of that page with the generated report:
   - Cloud ID: tomtom.atlassian.net
   - Content format: markdown
3. Confirm to the user with the page title and a link to the draft page.
