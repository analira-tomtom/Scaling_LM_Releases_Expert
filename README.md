# Roadmap Agent for WS6 Goal 2

This agent generates a roadmap table for Goal 2 in the WS6 Enabling Weekly Releases workstream, incorporating the latest updates from JIRA tickets via an Atlassian MCP server.

## Prerequisites

- Python 3.14+
- Atlassian API access (JIRA and Confluence)
- MCP library

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables for Atlassian access:
   - `ATLASSIAN_BASE_URL`: Your Atlassian instance URL (e.g., https://tomtom.atlassian.net)
   - `ATLASSIAN_EMAIL`: Your Atlassian account email
   - `ATLASSIAN_API_TOKEN`: API token generated from https://id.atlassian.com/manage-profile/security/api-tokens

## Usage

Run the script:
```bash
python3 roadmap_agent.py
```

The script will use the Atlassian MCP server to fetch data from Confluence and JIRA, then generate a markdown table with the roadmap, updated with latest JIRA ticket information.

## Output

The roadmap table includes columns: Phase, Milestone, Status, JIRA Tickets, Latest Update.

## Notes

- The agent connects to the Atlassian MCP server located in the `atlassian_mcp_server` directory.
- If MCP calls fail, the script falls back to mock data.
- Ensure your Atlassian account has permissions to access the specified Confluence page and JIRA project.