#!/usr/bin/env python3
"""
WS6 Scaling LM Releases Expert — Interactive Chat Agent

Standalone conversational agent for the WS6 Enabling Weekly Releases
workstream. Answers questions using live data from Confluence, JIRA and Slack.

Usage:
    python agent.py

Commands (at the prompt):
    /report     Generate this week's WS6 status report (paste into Confluence)
    /clear      Clear conversation history
    /help       Show available commands
    /exit       Exit

Required env vars:
    ATLASSIAN_EMAIL        your Atlassian account email
    ATLASSIAN_API_TOKEN    Atlassian API token (or JIRA_API_TOKEN)
    ATLASSIAN_BASE_URL     defaults to https://tomtom.atlassian.net
    ANTHROPIC_API_KEY      Claude API key

Optional:
    SLACK_BOT_TOKEN        enables Slack channel reads
"""

import os
import sys
import json
import re
from datetime import datetime

import requests
from anthropic import Anthropic

# ── API Clients ──────────────────────────────────────────────────────────────


class AtlassianClient:
    def __init__(self):
        self.base_url = os.environ.get("ATLASSIAN_BASE_URL", "https://tomtom.atlassian.net")
        email = os.environ.get("ATLASSIAN_EMAIL")
        token = os.environ.get("ATLASSIAN_API_TOKEN") or os.environ.get("JIRA_API_TOKEN")
        if not email or not token:
            raise EnvironmentError(
                "Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN (or JIRA_API_TOKEN)."
            )
        self.session = requests.Session()
        self.session.auth = (email, token)
        self.session.headers.update({"Accept": "application/json"})

    def get_confluence_page(self, page_id: str) -> str:
        r = self.session.get(
            f"{self.base_url}/rest/api/content/{page_id}",
            params={"expand": "body.view,version"},
        )
        r.raise_for_status()
        page = r.json()
        raw_html = page["body"]["view"]["value"]
        text = re.sub(r"<[^>]+>", " ", raw_html)
        text = re.sub(r"\s+", " ", text).strip()
        return f"# {page['title']} (v{page['version']['number']})\n\n{text[:10000]}"

    def search_confluence_pages(self, query: str, space_key: str = "ADPU", limit: int = 5) -> str:
        cql = f'text ~ "{query}" AND space = "{space_key}" ORDER BY lastModified DESC'
        r = self.session.get(
            f"{self.base_url}/rest/api/content/search",
            params={"cql": cql, "limit": limit, "expand": "version"},
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return "No pages found."
        return "\n".join(
            f"- [{p['id']}] {p['title']} (v{p['version']['number']})" for p in results
        )

    def get_jira_issue(self, issue_key: str) -> str:
        r = self.session.get(
            f"{self.base_url}/rest/api/3/issue/{issue_key}",
            params={"fields": "summary,status,assignee,priority,description,updated,comment"},
        )
        r.raise_for_status()
        issue = r.json()
        f = issue["fields"]
        assignee = (f.get("assignee") or {}).get("displayName", "Unassigned")
        priority = (f.get("priority") or {}).get("name", "-")
        desc = str(f.get("description") or "")[:500]
        last_comments = []
        for c in (f.get("comment") or {}).get("comments", [])[-3:]:
            author = c.get("author", {}).get("displayName", "?")
            body = str(c.get("body") or "")[:200]
            last_comments.append(f"  [{author}]: {body}")
        comments_text = "\n".join(last_comments) if last_comments else "  (none)"
        return (
            f"**{issue_key}**: {f['summary']}\n"
            f"Status: {f['status']['name']} | Assignee: {assignee} | Priority: {priority}\n"
            f"Updated: {f.get('updated', '')[:10]}\n"
            f"Description: {desc}\n"
            f"Recent comments:\n{comments_text}"
        )

    def search_jira_issues(self, jql: str, max_results: int = 15) -> str:
        r = self.session.get(
            f"{self.base_url}/rest/api/3/search",
            params={
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,status,assignee,priority,updated",
            },
        )
        r.raise_for_status()
        issues = r.json().get("issues", [])
        if not issues:
            return "No issues found."
        return "\n".join(
            f"- {i['key']}: {i['fields']['summary']} "
            f"[{i['fields']['status']['name']}] "
            f"({(i['fields'].get('assignee') or {}).get('displayName', 'Unassigned')})"
            for i in issues
        )


class SlackClient:
    def __init__(self):
        token = os.environ.get("SLACK_BOT_TOKEN") or os.environ.get("SLACK_API_TOKEN")
        self.enabled = bool(token)
        if self.enabled:
            self.session = requests.Session()
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def read_channel(self, channel_id: str, limit: int = 30) -> str:
        if not self.enabled:
            return "Slack not configured — set SLACK_BOT_TOKEN."
        r = self.session.get(
            "https://slack.com/api/conversations.history",
            params={"channel": channel_id, "limit": limit},
        )
        data = r.json()
        if not data.get("ok"):
            return f"Slack error: {data.get('error')}"
        messages = data.get("messages", [])
        lines = []
        for msg in reversed(messages):
            ts = datetime.fromtimestamp(float(msg["ts"])).strftime("%Y-%m-%d %H:%M")
            text = msg.get("text", "")
            lines.append(f"[{ts}] {msg.get('user', 'bot')}: {text}")
        return "\n".join(lines) if lines else "No messages."

    def search_messages(self, query: str, limit: int = 10) -> str:
        if not self.enabled:
            return "Slack not configured — set SLACK_BOT_TOKEN."
        r = self.session.get(
            "https://slack.com/api/search.messages",
            params={"query": query, "count": limit},
        )
        data = r.json()
        if not data.get("ok"):
            return f"Slack error: {data.get('error')}"
        matches = data.get("messages", {}).get("matches", [])
        lines = [
            f"[#{m.get('channel', {}).get('name', '?')}] "
            f"{m.get('username', '?')}: {m.get('text', '')[:300]}"
            for m in matches
        ]
        return "\n".join(lines) if lines else "No results."


# ── Tool Definitions for Claude ───────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_confluence_page",
        "description": (
            "Fetch the full text content of a Confluence page by its numeric page ID. "
            "Use this to read weekly reports, process definitions, or roadmap pages."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Confluence numeric page ID"}
            },
            "required": ["page_id"],
        },
    },
    {
        "name": "search_confluence_pages",
        "description": (
            "Search for Confluence pages in the ADPU space by keyword. "
            "Returns page IDs and titles. Use to find the latest weekly report."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords"},
                "limit": {"type": "integer", "description": "Max results (default 5)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_jira_issue",
        "description": (
            "Get the current status, assignee, description and recent comments "
            "for a single JIRA issue."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_key": {
                    "type": "string",
                    "description": "JIRA issue key, e.g. ADASHD-2756",
                }
            },
            "required": ["issue_key"],
        },
    },
    {
        "name": "search_jira_issues",
        "description": (
            "Search JIRA issues using JQL. Use to find open blockers, "
            "in-progress tickets, or WS6-labelled work."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "jql": {"type": "string", "description": "JQL query string"},
                "max_results": {
                    "type": "integer",
                    "description": "Max results (default 15)",
                },
            },
            "required": ["jql"],
        },
    },
    {
        "name": "read_slack_channel",
        "description": (
            "Read recent messages from a Slack channel by channel ID. "
            "WS6 channels: C0AJG2HHFRN (#tmp-scaling-lm-weekly-releases), "
            "C0ACPGKLKCP (#lmmap-e2e-workgroup), "
            "C0AAZCMMANT (#tmp-adas-crossworkstream-alignment)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "Slack channel ID"},
                "limit": {
                    "type": "integer",
                    "description": "Number of messages to retrieve (default 30)",
                },
            },
            "required": ["channel_id"],
        },
    },
    {
        "name": "search_slack_messages",
        "description": "Search Slack messages across all channels by keyword.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results (default 10)"},
            },
            "required": ["query"],
        },
    },
]

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""\
You are the WS6 Enabling Weekly Releases Expert — an AI project manager \
for TomTom's Q1/Q2 2026 Quality Sprint (workstream WS6).

Your role is to support the team by answering questions about project status \
and generating executive-quality updates.

ALWAYS structure answers around:
  ✅ GOOD NEWS  — progress, achievements, milestones reached
  ⚠️  BAD NEWS   — blockers, risks, unresolved dependencies (owner + impact)
  🔷 DECISIONS  — decisions made; decisions needed (with recommendation + owner)

Primary data sources — fetch fresh data before answering; never rely on memory:
  Confluence (space ADPU):
    - Main delivery page:              page 1505067229
    - Weekly reports folder:           search "WS6 Weekly Report" for latest
    - Q1 2026 Quality Sprint:          page 1426915690
    - Monthly→Weekly switch:           page 1500217912
  Slack channels:
    - #tmp-scaling-lm-weekly-releases   C0AJG2HHFRN  (primary WS6 channel)
    - #lmmap-e2e-workgroup               C0ACPGKLKCP
    - #tmp-adas-crossworkstream-alignment C0AAZCMMANT
  JIRA:
    - Key tickets: ADASHD-2756, ADASHD-3339, ADASHD-3299, ADASHD-3336
    - JQL for open work: project = ADASHD AND labels = WS6 AND statusCategory != Done

Rules:
  - Always use tools to get live data before answering.
  - Be concise and structured. Use bullet points. Include owners and ETAs.
  - Professional, neutral tone — output is for executive consumption.
  - Today's date: {datetime.now().strftime("%Y-%m-%d")}
"""

# ── Weekly Report Command ─────────────────────────────────────────────────────

WEEKLY_REPORT_TASK = f"""\
Today is {datetime.now().strftime("%Y-%m-%d")} (ISO week {datetime.now().isocalendar().week}). \
Generate the WS6 section for the NEXT week's Workstreams Weekly Report.

Step 1 — Find the most recent existing report:
  a. search_confluence_pages("Workstreams Weekly Report") — find all matching pages.
  b. Identify the one with the highest week number (e.g. "W17" > "W16"). Fetch it with \
get_confluence_page to read the current WS6 section content and all existing table rows.
  c. If a page for the current ISO week already exists, fetch that too.

Step 2 — Gather all fresh data in parallel:
  - read_slack_channel C0AJG2HHFRN limit=50  (#tmp-scaling-lm-weekly-releases)
  - read_slack_channel C0AAZCMMANT limit=30  (#tmp-adas-crossworkstream-alignment)
  - read_slack_channel C0ACPGKLKCP limit=20  (#lmmap-e2e-workgroup)
  - search_jira_issues "project = ADASHD AND labels = WS6 AND statusCategory != Done \
ORDER BY updated DESC" max_results=20
  - get_jira_issue for each open ticket found and for ADASHD-2756, ADASHD-3339.

Step 3 — Determine the new week number:
  The report to generate is for W(current ISO week). \
If the most recent Confluence page is already for this week, generate for W(current ISO week + 1).

Step 4 — Output the COMPLETE updated WS6 section below. \
Users will copy-paste this directly into the new Confluence page. \
Preserve ALL existing rows from the fetched page exactly; only ADD the new week row at the top \
of the Goal 1 table. Update Goal 2 risks and milestones with current JIRA status.

---
# ‌WS6: Enabling Weekly Deliveries

**Leads: Stefanie (TPM), Mario Aigner (PM), Guillermo Ruiz (EM)**

---

## **Goal 1: Stable weekly releases**

**On-time weekly LM map releases → Target: All on time**
**Errors per release → Target: <1 error**

| **Delivery** | **On Time Delivery** | **Lead Time** | **WoW (%)** | **CRD Blockers** | **CRD Minor/Data issue** | **Highlights (What went better?)** | **Lowlights (What went wrong?)** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CW[NEW WEEK]-Weekly | [status from Slack] | [days ↑/↓] | [%] | [count or -] | [count or -] | [from Slack/Confluence] | [from Slack/Confluence] |
| [all previous rows preserved exactly as fetched] | | | | | | | |

---

## **Goal 2: Reach an average lead time of 7 days or less by end of 2026**

**Key Risks and Challenges**

| Issue / Risk / Dependency | Impact | Mitigation / Next Step | Status | Owner |
| --- | --- | --- | --- | --- |
| [updated from JIRA + Slack] | | | | |

**Q1/Q2 Goals and Milestones**

| Milestone (JIRA) | Due Date | Status | Outcome |
| --- | --- | --- | --- |
| [updated rows from JIRA] | | | |

---

Rules: every cell must contain real data from the sources fetched — no placeholders left blank \
unless the source genuinely has no information. Flag any missing data explicitly.
"""

# ── Tool Dispatcher ───────────────────────────────────────────────────────────


def dispatch(atlassian: AtlassianClient, slack: SlackClient, name: str, inputs: dict) -> str:
    try:
        match name:
            case "get_confluence_page":
                return atlassian.get_confluence_page(inputs["page_id"])
            case "search_confluence_pages":
                return atlassian.search_confluence_pages(
                    inputs["query"], limit=inputs.get("limit", 5)
                )
            case "get_jira_issue":
                return atlassian.get_jira_issue(inputs["issue_key"])
            case "search_jira_issues":
                return atlassian.search_jira_issues(inputs["jql"], inputs.get("max_results", 15))
            case "read_slack_channel":
                return slack.read_channel(inputs["channel_id"], inputs.get("limit", 30))
            case "search_slack_messages":
                return slack.search_messages(inputs["query"], inputs.get("limit", 10))
            case _:
                return f"Unknown tool: {name}"
    except requests.HTTPError as e:
        return f"API error {e.response.status_code}: {e.response.text[:400]}"
    except Exception as e:
        return f"Tool error: {e}"


# ── Agent Turn ────────────────────────────────────────────────────────────────


def run_turn(
    client: Anthropic,
    atlassian: AtlassianClient,
    slack: SlackClient,
    messages: list,
    user_text: str,
) -> str:
    messages.append({"role": "user", "content": user_text})

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return "\n".join(b.text for b in response.content if hasattr(b, "text"))

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                args_preview = json.dumps(block.input)
                if len(args_preview) > 80:
                    args_preview = args_preview[:77] + "..."
                print(f"  › {block.name}({args_preview})", flush=True)
                result = dispatch(atlassian, slack, block.name, block.input)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )
            messages.append({"role": "user", "content": tool_results})
        else:
            return "[Unexpected stop reason: " + response.stop_reason + "]"


# ── Main ──────────────────────────────────────────────────────────────────────

HELP_TEXT = """
Commands:
  /report   Generate this week's WS6 status update (paste into Confluence)
  /clear    Clear conversation history
  /help     Show this help
  /exit     Quit

Or ask anything about the WS6 workstream, e.g.:
  "What are the current blockers?"
  "Who owns the idle time investigation?"
  "What decisions were made last week?"
  "Summarize the latest Slack updates"
"""


def main():
    print("━" * 60)
    print("  WS6 Scaling LM Releases Expert")
    print("━" * 60)

    try:
        atlassian = AtlassianClient()
    except EnvironmentError as e:
        print(f"\n[ERROR] {e}\nSee .env.example for required configuration.")
        sys.exit(1)

    slack = SlackClient()
    if not slack.enabled:
        print("[!] Slack not configured — set SLACK_BOT_TOKEN to enable channel reads.\n")

    client = Anthropic()
    messages: list = []

    print("Type /help for commands or ask a question. Ctrl+C to exit.\n")

    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            match user_input.lower():
                case "/exit" | "/quit":
                    print("Goodbye.")
                    break
                case "/clear":
                    messages = []
                    print("[Conversation cleared]\n")
                    continue
                case "/help":
                    print(HELP_TEXT)
                    continue
                case "/report":
                    print("[Fetching live data to generate weekly report...]\n")
                    user_input = WEEKLY_REPORT_TASK

            reply = run_turn(client, atlassian, slack, messages, user_input)
            print(f"\nAgent: {reply}\n")

    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
