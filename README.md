# Roadmap Agent for WS6 Goal 2

This agent generates a roadmap table for Goal 2 in the WS6 Enabling Weekly Releases workstream, incorporating the latest updates from JIRA tickets using the official Atlassian MCP server.

## Prerequisites

- Python 3.14+
- Official Atlassian MCP registered with Claude CLI

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Register the official Atlassian MCP server:
   ```bash
   claude mcp add --scope user --transport http atlassian https://mcp.atlassian.com/v1/mcp
   ```

## Usage

Run the script:
```bash
python3 roadmap_agent.py
```

The script generates a markdown table with the roadmap structure. The official Atlassian MCP server can be used to fetch real-time data from Confluence and JIRA as needed.

## Output

The roadmap table includes columns: Phase, Milestone, Status, JIRA Tickets, Latest Update.

## Notes

- The agent uses the official Atlassian MCP server registered globally with Claude
- The custom `atlassian_mcp_server` directory is kept for reference but is no longer used
- The official MCP provides access to JIRA and Confluence APIs through standardized tools