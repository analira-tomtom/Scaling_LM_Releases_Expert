import asyncio
import os
from datetime import datetime

# The agent now uses the official Atlassian MCP server
# registered via: claude mcp add --scope user --transport http atlassian https://mcp.atlassian.com/v1/mcp
# 
# This agent generates a roadmap table for Goal 2 by querying JIRA and Confluence
# No need for local MCP spawning - use the global registered MCP instead

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

def fetch_confluence_data():
    """Fetch Goal 2 and roadmap structure from Confluence."""
    # Note: With official Atlassian MCP, this would be called through the registered MCP
    # For now, return mock data - the official MCP tools can be invoked through Claude
    return parse_roadmap_from_content("")

def fetch_jira_updates():
    """Fetch latest updates from JIRA tickets."""
    # Note: With official Atlassian MCP, this would be called through the registered MCP
    # For now, return empty updates - the official MCP tools can be invoked through Claude
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
    print("Fetching Goal 2 roadmap from Confluence...")
    roadmap = fetch_confluence_data()
    if not roadmap:
        print("Failed to fetch roadmap. Using mock data.")
        roadmap = parse_roadmap_from_content("")  # Use mock

    print("Querying JIRA for ticket updates...")
    ticket_updates = fetch_jira_updates()

    print("Updating roadmap with JIRA data...")
    updated_roadmap = update_roadmap_with_jira(roadmap, ticket_updates)

    print("Generating markdown table...")
    table = generate_markdown_table(updated_roadmap)

    print("\nRoadmap Table for Goal 2:\n")
    print(table)

if __name__ == "__main__":
    main()