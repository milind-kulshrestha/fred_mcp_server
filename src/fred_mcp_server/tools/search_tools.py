"""
FRED Search Tools

This module defines tools for searching FRED data series.
"""
import json
import logging
from typing import Dict, Any

import mcp.types as types

logger = logging.getLogger("fred-mcp-server.tools.search")

# Define the search tool
search_series_tool = types.Tool(
    name="search_fred_series",
    description="Search for FRED data series by keywords",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for FRED series"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 10)"
            },
            "order_by": {
                "type": "string",
                "description": "How to order results (popularity, title, etc.)"
            }
        },
        "required": ["query"]
    }
)

async def handle_search_series(resource_manager, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle search_fred_series tool calls.
    
    Args:
        resource_manager: FRED resource manager
        arguments: Tool arguments
        
    Returns:
        Search results
    """
    query = arguments.get("query")
    limit = int(arguments.get("limit", 10))
    order_by = arguments.get("order_by", "popularity")
    
    try:
        results = await resource_manager.search_series(query, limit)
        
        # Format the results for better readability
        formatted_results = {
            "search_query": query,
            "count": len(results),
            "series": []
        }
        
        for series in results:
            formatted_results["series"].append({
                "id": series.get("id"),
                "title": series.get("title"),
                "frequency": series.get("frequency"),
                "units": series.get("units"),
                "observation_start": series.get("observation_start"),
                "observation_end": series.get("observation_end"),
                "seasonal_adjustment": series.get("seasonal_adjustment")
            })
        
        return formatted_results
    except Exception as e:
        logger.error(f"Error searching series: {str(e)}")
        return {"error": str(e)}