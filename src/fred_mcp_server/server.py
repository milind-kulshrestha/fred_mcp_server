"""
FRED MCP Server
==============

This module implements an MCP server for Federal Reserve Economic Data (FRED).
It provides tools for searching, retrieving, and analyzing economic data.
"""

import asyncio
import logging
import sys
from typing import Dict, Any, List, Optional

import aiohttp
import mcp.types as types
from mcp.server import Server, InitializationOptions, NotificationOptions
from mcp.server.stdio import stdio_server

from .config import Settings
from .resources import FREDResourceManager

# Import tool definitions directly
from .tools.search_tools import search_series_tool
from .tools.data_tools import get_series_data_tool, get_series_metadata_tool, get_category_series_tool, get_releases_tool
from .tools.analysis_tools import compare_series_tool, calculate_statistics_tool, detect_trends_tool

# Import tool handlers directly
from .tools.search_tools import handle_search_series
from .tools.data_tools import handle_get_series_data, handle_get_series_metadata, handle_get_category_series, handle_get_releases
from .tools.analysis_tools import handle_compare_series, handle_calculate_statistics, handle_detect_trends

# Initialize server settings
settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE, mode="a")
    ]
)
logger = logging.getLogger("fred-mcp-server")

# Create resource manager
resource_manager = FREDResourceManager(
    api_key=settings.API_KEY,
    base_url=settings.API_BASE_URL,
    rate_limit=settings.RATE_LIMIT,
    period=settings.RATE_LIMIT_PERIOD
)

# Initialize MCP server
server = Server(settings.APP_NAME)

@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools for FRED economic data analysis."""
    tools = [
        search_series_tool,
        get_series_data_tool,
        get_series_metadata_tool,
        get_category_series_tool,
        get_releases_tool,
        compare_series_tool,
        calculate_statistics_tool,
        detect_trends_tool
    ]
    
    logger.info(f"Loaded {len(tools)} tools")
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls by calling the appropriate handler with the FRED resource manager."""
    logger.info(f"Tool call: {name} with arguments: {arguments}")
    
    try:
        # Map tool names to handler functions
        handlers = {
            "search_fred_series": handle_search_series,
            "fred_get_series_data": handle_get_series_data,
            "fred_get_series_metadata": handle_get_series_metadata,
            "fred_get_category_series": handle_get_category_series,
            "fred_get_releases": handle_get_releases,
            "fred_compare_series": handle_compare_series,
            "fred_calculate_statistics": handle_calculate_statistics,
            "fred_detect_trends": handle_detect_trends
        }
        
        if name not in handlers:
            return [types.TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
        
        # Call the appropriate handler
        result = await handlers[name](resource_manager, arguments)
        
        # Convert result to TextContent
        if isinstance(result, dict):
            return [types.TextContent(
                type="text",
                text=str(result)
            )]
        elif isinstance(result, str):
            return [types.TextContent(
                type="text",
                text=result
            )]
        else:
            return [types.TextContent(
                type="text",
                text=str(result)
            )]
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error: Failed to execute tool '{name}': {str(e)}"
        )]

@server.list_prompts()
async def list_prompts() -> List[types.Prompt]:
    """List available prompts for FRED economic data analysis."""
    from .prompts import PROMPTS
    return list(PROMPTS.values())

@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str] | None = None) -> types.GetPromptResult:
    """Handle prompt requests for FRED analysis templates."""
    try:
        from .prompts import PROMPT_HANDLERS
        
        if name in PROMPT_HANDLERS:
            handler = PROMPT_HANDLERS[name]
            # Pass resource_manager to the prompt handler for dynamic content
            try:
                return await handler(arguments if arguments else {}, resource_manager)
            except TypeError:
                # Fallback for handlers that don't accept resource_manager
                logger.debug(f"Prompt handler {name} doesn't accept resource_manager parameter")
                return await handler(arguments if arguments else {})
        else:
            raise ValueError(f"Unknown prompt: {name}")
    except Exception as e:
        logger.error(f"Error handling prompt {name}: {str(e)}")
        raise ValueError(f"Error handling prompt: {str(e)}")


async def main():
    """Run the server as an async context."""
    logger.info(f"Starting {settings.APP_NAME} MCP Server v{settings.APP_VERSION}")
    
    # Test FRED API connection
    try:
        health_check = await resource_manager.check_health()
        if health_check:
            logger.info("FRED API connection successful")
        else:
            logger.warning("FRED API health check failed - API might be experiencing issues")
    except Exception as e:
        logger.error(f"Could not connect to FRED API: {str(e)}")
        logger.info("Server will continue to run, but tools may not function properly")
    
    # Start the MCP server
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name=settings.APP_NAME,
                server_version=settings.APP_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

# If script is run directly
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)