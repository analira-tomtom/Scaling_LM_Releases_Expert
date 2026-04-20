Generate the WS6 section for the next Workstreams Weekly Report using live data.

## Step 1 — Find the most recent existing report
- `searchConfluenceUsingCql`: `title ~ "Workstreams Weekly Report" AND space = "ADPU" ORDER BY lastModified DESC` (limit 3)
- Identify the page with the highest week number (e.g. W17 > W16). Fetch it with `getConfluencePage` to read the current WS6 section and all existing delivery table rows.

## Step 2 — Gather all fresh data
Fetch all of these in parallel:
- `slack_read_channel` C0AJG2HHFRN limit=50 (#tmp-scaling-lm-weekly-releases)
- `slack_read_channel` C0ACPGKLKCP limit=30 (#lmmap-e2e-workgroup)
- `slack_read_channel` C0AAZCMMANT limit=20 (#tmp-adas-crossworkstream-alignment)
- `searchJiraIssuesUsingJql`: `project = ADASHD AND text ~ "WS6" AND statusCategory != Done ORDER BY updated DESC` (max 15)
- `getJiraIssue` for: ADASHD-2756, ADASHD-3339, ADASHD-3336, ADASHD-3335

## Step 3 — Determine the target week number
- The report to generate is for W(current ISO week).
- If the most recent Confluence page is already for this week, generate for W(current ISO week + 1).

## Step 4 — Output the complete WS6 section

Output the full section below — ready to copy-paste into the new Confluence weekly page.
Preserve ALL existing rows from the fetched Confluence page exactly; only ADD the new week row at the top of the Goal 1 table. Update Goal 2 risks and milestones with current JIRA + Slack data. Every cell must contain real data — flag any gaps explicitly rather than leaving placeholders.

---
# ‌WS6: Enabling Weekly Deliveries

**Leads: Stefanie Gysels (TPM), Mario Aigner (PM), Guillermo Ruiz (EM)**

---

## **Goal 1: Stable weekly releases**

**On-time weekly LM map releases → Target: All on time**
**Errors per release → Target: <1 error**

| **Delivery** | **On Time Delivery** | **Lead Time** | **WoW (%)** | **CRD Blockers** | **CRD Minor/Data issue** | **Highlights (What went better?)** | **Lowlights (What went wrong?)** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CW[NEW WEEK]-Weekly | [from Slack] | [days ↑/↓ or TBD] | [% or TBD] | [count or -] | [count or -] | [from Slack/Confluence] | [from Slack/Confluence] |
| [all previous rows preserved exactly] | | | | | | | |

---

## **Goal 2: Reach an average lead time of 7 days or less by end of 2026**

**Key Risks and Challenges**

| Issue / Risk / Dependency | Impact | Mitigation / Next Step | Status | Owner |
| --- | --- | --- | --- | --- |
| [from JIRA + Slack, updated] | | | | |

**Q1/Q2 Goals and Milestones**

| Milestone (JIRA) | Due Date | Status | Outcome |
| --- | --- | --- | --- |
| [updated from JIRA] | | | |

---

**📋 Key Actions**

| Action | Owner | ETA |
|--------|-------|-----|
| [from meeting notes and Slack action items] | | |
