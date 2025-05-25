"""
FRED Data Tools

This module defines tools for retrieving FRED economic data.
"""

import mcp.types as types
import logging
from typing import Dict, Any

logger = logging.getLogger("fred-mcp-server.tools.data")

# Define the series data tool
get_series_data_tool = types.Tool(
    name="fred_get_series_data",
    description="Retrieve time series data for a specific FRED series",
    inputSchema={
        "type": "object",
        "properties": {
            "series_id": {
                "type": "string",
                "description": "FRED series ID (e.g., 'GDP', 'UNRATE')"
            },
            "observation_start": {
                "type": "string",
                "description": "Start date (YYYY-MM-DD)"
            },
            "observation_end": {
                "type": "string",
                "description": "End date (YYYY-MM-DD)"
            },
            "frequency": {
                "type": "string",
                "description": "Data frequency (d, w, bw, m, q, sa, a)"
            }
        },
        "required": ["series_id"]
    }
)

# Define the series metadata tool
get_series_metadata_tool = types.Tool(
    name="fred_get_series_metadata",
    description="Get metadata for a specific FRED series",
    inputSchema={
        "type": "object",
        "properties": {
            "series_id": {
                "type": "string",
                "description": "FRED series ID (e.g., 'GDP', 'UNRATE')"
            }
        },
        "required": ["series_id"]
    }
)

# Define the category series tool
get_category_series_tool = types.Tool(
    name="fred_get_category_series",
    description="List series in a FRED category",
    inputSchema={
        "type": "object",
        "properties": {
            "category_id": {
                "type": "integer",
                "description": "FRED category ID"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 10)"
            }
        },
        "required": ["category_id"]
    }
)

# Define the releases tool
get_releases_tool = types.Tool(
    name="fred_get_releases",
    description="Get economic data releases from FRED",
    inputSchema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 10)"
            }
        }
    }
)

async def handle_get_series_data(resource_manager, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle get_series_data tool calls.
    
    Args:
        resource_manager: FRED resource manager
        arguments: Tool arguments
        
    Returns:
        Series data
    """
    series_id = arguments.get("series_id")
    observation_start = arguments.get("observation_start")
    observation_end = arguments.get("observation_end")
    frequency = arguments.get("frequency")
    
    try:
        results = await resource_manager.get_observations(
            series_id=series_id,
            observation_start=observation_start,
            observation_end=observation_end,
            frequency=frequency
        )
        
        # Format the results for better readability
        formatted_results = {
            "series_id": series_id,
            "count": len(results.get("observations", [])),
            "observations": results.get("observations", []),
            "series_info": results.get("series_info", {})
        }
        
        return formatted_results
    except Exception as e:
        logger.error(f"Error getting series data: {str(e)}")
        return {"error": str(e)}

async def handle_get_series_metadata(resource_manager, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle get_series_metadata tool calls.
    
    Args:
        resource_manager: FRED resource manager
        arguments: Tool arguments
        
    Returns:
        Series metadata
    """
    series_id = arguments.get("series_id")
    
    try:
        results = await resource_manager.get_series_info(series_id=series_id)
        
        return results
    except Exception as e:
        logger.error(f"Error getting series metadata: {str(e)}")
        return {"error": str(e)}

async def handle_get_category_series(resource_manager, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle get_category_series tool calls.
    
    Args:
        resource_manager: FRED resource manager
        arguments: Tool arguments
        
    Returns:
        Category series
    """
    category_id = arguments.get("category_id")
    limit = int(arguments.get("limit", 10))
    
    try:
        # Since the actual method might differ from the interface we're expecting,
        # we'll assume there's a method to get series by category
        # If this doesn't exist, you'll need to implement it in the resource manager
        results = await resource_manager.get_category_series(
            category_id=category_id,
            limit=limit
        )
        
        return results
    except Exception as e:
        logger.error(f"Error getting category series: {str(e)}")
        return {"error": str(e)}

async def handle_get_releases(resource_manager, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle get_releases tool calls.
    
    Args:
        resource_manager: FRED resource manager
        arguments: Tool arguments
        
    Returns:
        Releases data
    """
    limit = int(arguments.get("limit", 10))
    
    try:
        results = await resource_manager.list_releases()
        
        # Just take the first 'limit' items
        releases = results[:limit] if limit < len(results) else results
        
        return {"releases": releases, "count": len(releases)}
    except Exception as e:
        logger.error(f"Error getting releases: {str(e)}")
        return {"error": str(e)}