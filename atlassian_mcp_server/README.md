# Atlassian MCP Server

A Model Context Protocol server for interacting with Atlassian tools (JIRA and Confluence).

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   - `ATLASSIAN_BASE_URL`: Your Atlassian instance URL (e.g., https://yourcompany.atlassian.net)
   - `ATLASSIAN_EMAIL`: Your Atlassian account email
   - `ATLASSIAN_API_TOKEN`: Your Atlassian API token (generate from https://id.atlassian.com/manage-profile/security/api-tokens)

3. Run the server:
   ```bash
   python server.py
   ```

## Tools

- `get_jira_issue`: Get details of a JIRA issue by key
- `search_jira_issues`: Search JIRA issues using JQL
- `get_confluence_page`: Get content of a Confluence page by ID
- `search_confluence_pages`: Search Confluence pages

## Integration with Python Agent

To integrate with a Python agent using MCP, use the `mcp` client library.

Example:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["/path/to/atlassian_mcp_server/server.py"],
        env={"ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net", "ATLASSIAN_EMAIL": "your@email.com", "ATLASSIAN_API_TOKEN": "your_token"}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools])

            # Call a tool
            result = await session.call_tool("get_jira_issue", {"issue_key": "PROJ-123"})
            print(result)

asyncio.run(main())
```

For your roadmap_agent.py, modify it to use the MCP client to query JIRA and Confluence data as needed.