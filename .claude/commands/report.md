Generate the WS6 section for the current week's Workstreams Weekly Report.

Steps:
1. Search Confluence for the two most recent weekly reports using CQL: `title ~ "Workstreams Weekly Report" AND space = "ADPU" ORDER BY lastModified DESC` — read both for current state and WoW baseline.
2. Read the primary Slack channel #tmp-scaling-lm-weekly-releases (C0AJG2HHFRN) for updates from the last 72 hours.
3. Read the operational channel #lmmap-e2e-workgroup (C0ACPGKLKCP) for release pipeline updates.
4. Read the WS6 main Confluence page (ID: 1505067229) for current lead time and milestone status.
5. Follow any open JIRA ticket links referenced in the above sources.

Generate the report section matching the exact format of the most recent WS6 entry — same headings, same table column order, same structure. Include:
- Overall RAG status (explain any change from previous week)
- Delivery table with WoW changes (newest release at top)
- Goal 2 milestone status table
- Risks and Challenges table
- Production Metrics / Workstream Health Metrics

Favor Slack as source of truth for updates from the last 72 hours. Cite the source for each material statement.

After generating, ask: "Would you like me to copy this to the Confluence draft report page? Run `/save` to do so."
