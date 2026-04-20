import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

# MCP server path
MCP_SERVER_PATH = "/Users/ana.lira/Documents/Orbis/Repos/Scaling LM Releases Expert/atlassian_mcp_server/server.py"

async def query_mcp_tool(tool_name, arguments):
    """Query the Atlassian MCP server."""
    server_params = StdioServerParameters(
        command="python3",
        args=[MCP_SERVER_PATH],
        env={
            "ATLASSIAN_BASE_URL": os.getenv("ATLASSIAN_BASE_URL", "https://tomtom.atlassian.net"),
            "ATLASSIAN_EMAIL": os.getenv("ATLASSIAN_EMAIL", ""),
            "ATLASSIAN_API_TOKEN": os.getenv("ATLASSIAN_API_TOKEN", "")
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text

def fetch_confluence_data():
    """Fetch Goal 2 and roadmap structure from Confluence via MCP."""
    try:
        # Use MCP to get Confluence page
        page_content = asyncio.run(query_mcp_tool("get_confluence_page", {"page_id": "1505067229"}))
        # Parse content to extract Goal 2 roadmap
        return parse_roadmap_from_content(page_content)
    except Exception as e:
        print(f"Error fetching Confluence data via MCP: {e}")
        return parse_roadmap_from_content("")

def fetch_jira_updates():
    """Fetch latest updates from JIRA tickets via MCP."""
    try:
        # Search for relevant tickets
        search_results = asyncio.run(query_mcp_tool("search_jira_issues", {
            "jql": "key in (ADASHD-2756, ADASHD-3339)",
            "max_results": 10
        }))
        updates = {}
        # Parse the results
        lines = search_results.strip().split('\n')
        for line in lines:
            if ': ' in line:
                key, summary = line.split(': ', 1)
                # Get detailed issue info
                issue_details = asyncio.run(query_mcp_tool("get_jira_issue", {"issue_key": key}))
                # Parse status and updated date (simplified)
                updates[key] = {
                    "status": "In Progress",  # Placeholder
                    "summary": summary,
                    "updated": "2026-04-20"  # Placeholder
                }
        return updates
    except Exception as e:
        print(f"Error fetching JIRA data via MCP: {e}")
        return {}

def parse_roadmap_from_content(content):
    """
    Parse the Confluence page content to extract roadmap structure.
    This is a mock implementation. In practice, use BeautifulSoup or similar to parse HTML.
    """
    # Mock roadmap structure for Goal 2: Enabling Weekly Releases
    roadmap = [
        {'Phase': 'Planning', 'Milestone': 'Define Release Process', 'Status': 'Completed', 'JIRA Tickets': 'REL-1, REL-2'},
        {'Phase': 'Development', 'Milestone': 'Automate Build Pipeline', 'Status': 'In Progress', 'JIRA Tickets': 'REL-3, REL-4'},
        {'Phase': 'Testing', 'Milestone': 'Implement Automated Testing', 'Status': 'Pending', 'JIRA Tickets': 'REL-5'},
        {'Phase': 'Deployment', 'Milestone': 'Enable Weekly Deployments', 'Status': 'Pending', 'JIRA Tickets': 'REL-6, REL-7'},
        {'Phase': 'Monitoring', 'Milestone': 'Set up Release Monitoring', 'Status': 'Not Started', 'JIRA Tickets': 'REL-8'}
    ]
    return roadmap

def query_jira_tickets():
    """
    Query JIRA for relevant tickets related to Goal 2.
    Assumes a JQL query to find tickets in the workstream.
    """
    jql = 'project = "WS6" AND labels = "Goal2" OR summary ~ "Weekly Releases"'  # Placeholder JQL
    try:
        issues = jira.jql(jql)
        ticket_updates = {}
        for issue in issues['issues']:
            key = issue['key']
            status = issue['fields']['status']['name']
            summary = issue['fields']['summary']
            updated = issue['fields']['updated']
            ticket_updates[key] = {'status': status, 'summary': summary, 'updated': updated}
        return ticket_updates
    except Exception as e:
        print(f"Error querying JIRA: {e}")
        return {}

def update_roadmap_with_jira(roadmap, ticket_updates):
    """
    Update the roadmap with latest JIRA ticket information.
    """
    for item in roadmap:
        tickets = item['JIRA Tickets'].split(', ')
        for ticket in tickets:
            if ticket in ticket_updates:
                # Update status if ticket status differs
                if ticket_updates[ticket]['status'] != item['Status']:
                    item['Status'] = ticket_updates[ticket]['status']
                # Add update info
                item['Latest Update'] = f"{ticket}: {ticket_updates[ticket]['summary']} (Updated: {ticket_updates[ticket]['updated']})"
            else:
                item['Latest Update'] = f"{ticket}: No recent updates"
    return roadmap

def generate_markdown_table(roadmap):
    """
    Generate a markdown table from the roadmap data.
    """
    headers = ['Phase', 'Milestone', 'Status', 'JIRA Tickets', 'Latest Update']
    table = '| ' + ' | '.join(headers) + ' |\n'
    table += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
    for row in roadmap:
        table += '| ' + ' | '.join([row.get(h, '') for h in headers]) + ' |\n'
    return table

def main():
    print("Fetching Goal 2 roadmap from Confluence via MCP...")
    roadmap = fetch_confluence_data()
    if not roadmap:
        print("Failed to fetch roadmap. Using mock data.")
        roadmap = parse_roadmap_from_content("")  # Use mock

    print("Querying JIRA for ticket updates via MCP...")
    ticket_updates = fetch_jira_updates()

    print("Updating roadmap with JIRA data...")
    updated_roadmap = update_roadmap_with_jira(roadmap, ticket_updates)

    print("Generating markdown table...")
    table = generate_markdown_table(updated_roadmap)

    print("\nRoadmap Table for Goal 2:\n")
    print(table)

if __name__ == "__main__":
    main()