import os
import requests
from typing import Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, ToolAnnotations
from pydantic import BaseModel, Field
from enum import Enum

class JiraIssueInput(BaseModel):
    issue_key: str = Field(description="The JIRA issue key, e.g., 'PROJ-123'")

class JiraSearchInput(BaseModel):
    jql: str = Field(description="JQL query to search issues")
    max_results: int = Field(default=10, description="Maximum number of results to return")

class ConfluencePageInput(BaseModel):
    page_id: str = Field(description="The Confluence page ID")

class ConfluenceSearchInput(BaseModel):
    query: str = Field(description="Search query for Confluence pages")
    space_key: Optional[str] = Field(default=None, description="Space key to limit search")
    max_results: int = Field(default=10, description="Maximum number of results to return")

class AtlassianTools(str, Enum):
    GET_JIRA_ISSUE = "get_jira_issue"
    SEARCH_JIRA_ISSUES = "search_jira_issues"
    GET_CONFLUENCE_PAGE = "get_confluence_page"
    SEARCH_CONFLUENCE_PAGES = "search_confluence_pages"

class AtlassianMCPServer:
    def __init__(self):
        self.base_url = os.getenv("ATLASSIAN_BASE_URL")
        self.email = os.getenv("ATLASSIAN_EMAIL")
        self.api_token = os.getenv("ATLASSIAN_API_TOKEN")

        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError("ATLASSIAN_BASE_URL, ATLASSIAN_EMAIL, and ATLASSIAN_API_TOKEN must be set")

        self.session = requests.Session()
        self.session.auth = (self.email, self.api_token)

    def get_jira_issue(self, issue_key: str) -> str:
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        response = self.session.get(url)
        response.raise_for_status()
        issue = response.json()
        return f"Issue {issue_key}: {issue['fields']['summary']}\nStatus: {issue['fields']['status']['name']}\nDescription: {issue['fields'].get('description', 'No description')}"

    def search_jira_issues(self, jql: str, max_results: int = 10) -> str:
        url = f"{self.base_url}/rest/api/3/search"
        params = {"jql": jql, "maxResults": max_results}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = []
        for issue in data['issues']:
            results.append(f"{issue['key']}: {issue['fields']['summary']}")
        return "\n".join(results)

    def get_confluence_page(self, page_id: str) -> str:
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {"expand": "body.storage"}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        page = response.json()
        return f"Page: {page['title']}\nContent: {page['body']['storage']['value']}"

    def search_confluence_pages(self, query: str, space_key: Optional[str] = None, max_results: int = 10) -> str:
        url = f"{self.base_url}/rest/api/content/search"
        params = {"cql": f"text ~ '{query}'" + (f" and space = {space_key}" if space_key else ""), "limit": max_results}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = []
        for page in data['results']:
            results.append(f"{page['id']}: {page['title']}")
        return "\n".join(results)

async def serve():
    server = Server("atlassian-mcp-server")
    atlassian = AtlassianMCPServer()

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name=AtlassianTools.GET_JIRA_ISSUE,
                description="Get details of a JIRA issue by key",
                inputSchema=JiraIssueInput.model_json_schema(),
                annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
            ),
            Tool(
                name=AtlassianTools.SEARCH_JIRA_ISSUES,
                description="Search JIRA issues using JQL",
                inputSchema=JiraSearchInput.model_json_schema(),
                annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
            ),
            Tool(
                name=AtlassianTools.GET_CONFLUENCE_PAGE,
                description="Get content of a Confluence page by ID",
                inputSchema=ConfluencePageInput.model_json_schema(),
                annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
            ),
            Tool(
                name=AtlassianTools.SEARCH_CONFLUENCE_PAGES,
                description="Search Confluence pages",
                inputSchema=ConfluenceSearchInput.model_json_schema(),
                annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        match name:
            case AtlassianTools.GET_JIRA_ISSUE:
                result = atlassian.get_jira_issue(arguments["issue_key"])
                return [TextContent(type="text", text=result)]
            case AtlassianTools.SEARCH_JIRA_ISSUES:
                result = atlassian.search_jira_issues(arguments["jql"], arguments.get("max_results", 10))
                return [TextContent(type="text", text=result)]
            case AtlassianTools.GET_CONFLUENCE_PAGE:
                result = atlassian.get_confluence_page(arguments["page_id"])
                return [TextContent(type="text", text=result)]
            case AtlassianTools.SEARCH_CONFLUENCE_PAGES:
                result = atlassian.search_confluence_pages(arguments["query"], arguments.get("space_key"), arguments.get("max_results", 10))
                return [TextContent(type="text", text=result)]
            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())