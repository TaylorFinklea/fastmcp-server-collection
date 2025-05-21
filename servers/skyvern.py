import asyncio
import httpx
import os

from typing import Any, Dict, Annotated, Literal
from pydantic import Field
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env
load_dotenv()

skyvern_url = os.getenv("SKYVERN_URL")
skyvern_api_key = os.getenv("SKYVERN_API_KEY")

# Check if environment variables are set
if not skyvern_url:
    raise ValueError("SKYVERN_URL environment variable is not set")
if not skyvern_api_key:
    raise ValueError("SKYVERN_API_KEY environment variable is not set")

# Create the MCP server
mcp = FastMCP("skyvern")

# Constants
USER_AGENT = "fastmcp-server-collection/1.0"

@mcp.tool()
async def initiate_task(
    url: Annotated[str, Field(description="The starting URL for the task. If not provided, Skyvern will attempt to determine an appropriate URL.")],
    prompt: Annotated[str, Field(description="The goal or task for Skyvern to accomplish. Use 'complete'/'terminate'; prompt specifically, simply, and verbosely; define single, clear goals with guardrails (e.g., 'close cookie dialogs'); and provide concrete examples.")],
    title: Annotated[str, Field(description="The title for the task.")],
    engine: Annotated[str, Field(description="The Skyvern engine version to use for this task. Supported values are 'skyvern-1.0' and 'skyvern-2.0'. Default is 'skyvern-2.0'.")] = "skyvern-2.0",
    proxy_location: Annotated[str, Field(description="Geographic Proxy location to route the browser traffic through. Default is 'RESIDENTIAL'")] = "RESIDENTIAL",
    data_extraction_schema: Annotated[Dict[str, Any] | None, Field(description="Schema defining what data should be extracted from the webpage")] = None,
    error_code_mapping: Annotated[Dict[str, Any] | None, Field(description="Custom mapping of error codes to error messages if Skyvern encounters an error")] = None,
    max_steps: Annotated[int, Field(description="Maximum number of steps the task can take before timing out")] = 10,
    webhook_url: Annotated[str | None, Field(description="URL to send task status updates to after a run is finished")] = None,
    totp_identifier: Annotated[str | None, Field(description="Identifier for TOTP (Time-based One-Time Password) authentication if codes are being pushed to Skyvern")] = None,
    totp_url: Annotated[str | None, Field(description="URL for TOTP authentication setup if Skyvern should poll endpoint for 2FA codes")] = None,
    browser_session_id: Annotated[str | None, Field(description="ID of an existing browser session to reuse, having it continue from the current screen state")] = None,
    publish_workflow: Annotated[bool, Field(description="Whether to publish this task as a reusable workflow. Default is false")] = False
) -> Dict[str, Any]:
    """
    Initiates a task with the Skyvern API.

    Args:
        url: The URL for the task.
        prompt: The prompt for the task.
        title: The title for the task.
        engine: The Skyvern engine version to use. Default is "skyvern-2.0".
        proxy_location: Geographic proxy location to route browser traffic. Default is "RESIDENTIAL".
        data_extraction_schema: Schema defining what data should be extracted from the webpage.
        error_code_mapping: Custom mapping of error codes to error messages.
        max_steps: Maximum number of steps the task can take before timing out. Default is 10.
        webhook_url: URL to send task status updates after the run is finished.
        totp_identifier: Identifier for TOTP authentication if codes are being pushed to Skyvern.
        totp_url: URL for TOTP authentication setup if Skyvern should poll for 2FA codes.
        browser_session_id: ID of an existing browser session to reuse.
        publish_workflow: Whether to publish this task as a reusable workflow. Default is False.

    Returns:
        A dictionary containing the Skyvern API response or a structured error message.
    """
    api_url = f"{skyvern_url}/v1/run/tasks"
    headers = {
        "x-api-key": skyvern_api_key,
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
    }
    payload = {
        "url": url,
        "prompt": prompt,
        "title": title,
        "engine": engine,
        "proxy_location": proxy_location,
        "max_steps": max_steps,
        "publish_workflow": publish_workflow,
    }

    # Add optional parameters only if they're provided
    if data_extraction_schema is not None:
        payload["data_extraction_schema"] = data_extraction_schema
    if error_code_mapping is not None:
        payload["error_code_mapping"] = error_code_mapping
    if webhook_url is not None:
        payload["webhook_url"] = webhook_url
    if totp_identifier is not None:
        payload["totp_identifier"] = totp_identifier
    if totp_url is not None:
        payload["totp_url"] = totp_url
    if browser_session_id is not None:
        payload["browser_session_id"] = browser_session_id

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log or print the error for server-side visibility
            # In a production app, you'd use a proper logger here.
            print(f"Skyvern API HTTPStatusError: {e.response.status_code} - {e.response.text}")
            return {
                "error": "SkyvernAPIError",
                "message": f"Skyvern API request failed with status {e.response.status_code}",
                "details": e.response.text,
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            print(f"Skyvern API RequestError: {e}")
            return {
                "error": "NetworkError",
                "message": "Failed to connect to Skyvern API or other network issue.",
                "details": str(e)
            }
        except Exception as e: # Catch any other unexpected errors
            print(f"Unexpected error during Skyvern API call: {e}")
            return {
                "error": "InternalServerError",
                "message": "An unexpected error occurred while processing the Skyvern task initiation.",
                "details": str(e)
            }

@mcp.tool()
async def get_task_details(run_id: str) -> Dict[str, Any]:
    """
    Gets details about a specific Skyvern task.

    Args:
        run_id: The unique identifier for the task.

    Returns:
        A dictionary containing the task details or a structured error message.
    """
    api_url = f"{skyvern_url}/v1/runs/{run_id}"
    headers = {
        "x-api-key": skyvern_api_key,
        "User-Agent": USER_AGENT,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Skyvern API HTTPStatusError: {e.response.status_code} - {e.response.text}")
            return {
                "error": "SkyvernAPIError",
                "message": f"Skyvern API request failed with status {e.response.status_code}",
                "details": e.response.text,
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            print(f"Skyvern API RequestError: {e}")
            return {
                "error": "NetworkError",
                "message": "Failed to connect to Skyvern API or other network issue.",
                "details": str(e)
            }
        except Exception as e:  # Catch any other unexpected errors
            print(f"Unexpected error during Skyvern API call: {e}")
            return {
                "error": "InternalServerError",
                "message": "An unexpected error occurred while retrieving the Skyvern task details.",
                "details": str(e)
            }

@mcp.tool()
async def cancel_task(run_id: str) -> Dict[str, Any]:
    """
    Cancels a running Skyvern task.

    Args:
        run_id: The unique identifier for the task to cancel.

    Returns:
        A dictionary containing the cancellation response or a structured error message.
    """
    api_url = f"{skyvern_url}/v1/runs/{run_id}/cancel"
    headers = {
        "x-api-key": skyvern_api_key,
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Skyvern API HTTPStatusError: {e.response.status_code} - {e.response.text}")
            return {
                "error": "SkyvernAPIError",
                "message": f"Skyvern API request failed with status {e.response.status_code}",
                "details": e.response.text,
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            print(f"Skyvern API RequestError: {e}")
            return {
                "error": "NetworkError",
                "message": "Failed to connect to Skyvern API or other network issue.",
                "details": str(e)
            }
        except Exception as e:  # Catch any other unexpected errors
            print(f"Unexpected error during Skyvern API call: {e}")
            return {
                "error": "InternalServerError",
                "message": "An unexpected error occurred while canceling the Skyvern task.",
                "details": str(e)
            }

if __name__ == "__main__":
    # Start the MCP server
    mcp.run()
