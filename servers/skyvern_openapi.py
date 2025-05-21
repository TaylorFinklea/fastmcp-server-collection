import asyncio
import os
import httpx

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, RouteType

load_dotenv()

skyvern_url = os.getenv("SKYVERN_URL")
skyvern_api_key = os.getenv("SKYVERN_API_KEY")

# Check if environment variables are set
if not skyvern_url:
    raise ValueError("SKYVERN_URL environment variable is not set")
if not skyvern_api_key:
    raise ValueError("SKYVERN_API_KEY environment variable is not set")

# Client for the Skyvern API
client = httpx.AsyncClient(
    base_url=skyvern_url,
    headers={
        "x-api-key": skyvern_api_key
    }
)

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=httpx.get("https://api.skyvern.com/openapi.json").json(), client=client, name="Skyvern", route_maps=[
        RouteMap(methods="*", pattern=r".*", route_type=RouteType.TOOL)
    ]
)

async def check_mcp(mcp: FastMCP):
    # List what components were created
    tools = await mcp.get_tools()
    resources = await mcp.get_resources()
    templates = await mcp.get_resource_templates()

    print(
        f"{len(tools)} Tool(s): {', '.join([t.name for t in tools.values() if t.name is not None])}"
    )
    print(
        f"{len(resources)} Resource(s): {', '.join([r.name for r in resources.values() if r.name is not None])}"
    )
    print(
        f"{len(templates)} Resource Template(s): {', '.join([t.name for t in templates.values() if t.name is not None])}"
    )

    return mcp


if __name__ == "__main__":
    asyncio.run(check_mcp(mcp))
    # Start the MCP server
    mcp.run()
