"""
FRED Analysis Tools

This module defines tools for analyzing FRED economic data.
"""

import mcp.types as types
import logging
import statistics
from typing import Dict, Any, List

logger = logging.getLogger("fred-mcp-server.tools.analysis")

# Define the compare series tool
compare_series_tool = types.Tool(
    name="fred_compare_series",
    description="Compare multiple FRED data series",
    inputSchema={
        "type": "object",
        "properties": {
            "series_ids": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of FRED series IDs to compare"
            },
            "observation_start": {
                "type": "string",
                "description": "Start date (YYYY-MM-DD)"
            },
            "observation_end": {
                "type": "string",
                "description": "End date (YYYY-MM-DD)"
            }
        },
        "required": ["series_ids"]
    }
)

# Define the calculate statistics tool
calculate_statistics_tool = types.Tool(
    name="fred_calculate_statistics",
    description="Calculate basic statistics for a FRED series",
    inputSchema={
        "type": "object",
        "properties": {
            "series_id": {
                "type": "string",
                "description": "FRED series ID"
            },
            "observation_start": {
                "type": "string",
                "description": "Start date (YYYY-MM-DD)"
            },
            "observation_end": {
                "type": "string",
                "description": "End date (YYYY-MM-DD)"
            }
        },
        "required": ["series_id"]
    }
)

# Define the detect trends tool
detect_trends_tool = types.Tool(
    name="fred_detect_trends",
    description="Identify trends in FRED economic data",
    inputSchema={
        "type": "object",
        "properties": {
            "series_id": {
                "type": "string",
                "description": "FRED series ID"
            },
            "observation_start": {
                "type": "string",
                "description": "Start date (YYYY-MM-DD)"
            },
            "observation_end": {
                "type": "string",
                "description": "End date (YYYY-MM-DD)"
            },
            "window_size": {
                "type": "integer",
                "description": "Window size for trend detection (default: 3)"
            }
        },
        "required": ["series_id"]
    }
)

async def handle_compare_series(resource_manager, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle compare_series tool calls.
    
    Args:
        resource_manager: FRED resource manager
        arguments: Tool arguments
        
    Returns:
        Comparison results
    """
    series_ids = arguments.get("series_ids", [])
    observation_start = arguments.get("observation_start")
    observation_end = arguments.get("observation_end")
    
    if not series_ids:
        return {"error": "No series IDs provided"}
    
    try:
        comparison = {"series": {}}
        
        # Get data for each series
        for series_id in series_ids:
            series_data = await resource_manager.get_observations(
                series_id=series_id,
                observation_start=observation_start,
                observation_end=observation_end
            )
            
            # Add to comparison
            comparison["series"][series_id] = {
                "title": series_data.get("series_info", {}).get("title", series_id),
                "observations": series_data.get("observations", [])
            }
        
        return comparison
    except Exception as e:
        logger.error(f"Error comparing series: {str(e)}")
        return {"error": str(e)}

async def handle_calculate_statistics(resource_manager, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle calculate_statistics tool calls.
    
    Args:
        resource_manager: FRED resource manager
        arguments: Tool arguments
        
    Returns:
        Statistics results
    """
    series_id = arguments.get("series_id")
    observation_start = arguments.get("observation_start")
    observation_end = arguments.get("observation_end")
    
    try:
        # Get series data
        series_data = await resource_manager.get_observations(
            series_id=series_id,
            observation_start=observation_start,
            observation_end=observation_end
        )
        
        # Extract series title from metadata
        title = series_data.get("series_info", {}).get("title", series_id)
        
        # Calculate statistics
        observations = series_data.get("observations", [])
        values = []
        
        for obs in observations:
            try:
                value = float(obs.get("value", "0"))
                values.append(value)
            except (ValueError, TypeError):
                # Skip non-numeric values
                pass
        
        if not values:
            return {
                "series_id": series_id,
                "title": title,
                "error": "No numeric values found"
            }
        
        stats = {
            "series_id": series_id,
            "title": title,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values)
        }
        
        # Calculate standard deviation if we have enough values
        if len(values) > 1:
            stats["std_dev"] = statistics.stdev(values)
        
        return stats
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}")
        return {"error": str(e)}

async def handle_detect_trends(resource_manager, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle detect_trends tool calls.
    
    Args:
        resource_manager: FRED resource manager
        arguments: Tool arguments
        
    Returns:
        Trend analysis results
    """
    series_id = arguments.get("series_id")
    observation_start = arguments.get("observation_start")
    observation_end = arguments.get("observation_end")
    window_size = int(arguments.get("window_size", 3))
    
    try:
        # Get series data
        series_data = await resource_manager.get_observations(
            series_id=series_id,
            observation_start=observation_start,
            observation_end=observation_end
        )
        
        # Extract series title from metadata
        title = series_data.get("series_info", {}).get("title", series_id)
        
        # Get observations
        observations = series_data.get("observations", [])
        
        # We need numeric values for trend detection
        dates = []
        values = []
        
        for obs in observations:
            try:
                date = obs.get("date", "")
                value = float(obs.get("value", "0"))
                dates.append(date)
                values.append(value)
            except (ValueError, TypeError):
                # Skip non-numeric values
                pass
        
        if len(values) < window_size * 2:
            return {
                "series_id": series_id,
                "title": title,
                "error": f"Not enough data points for trend detection (need at least {window_size * 2})"
            }
        
        # Simple trend detection: calculate moving averages and identify trends
        trends = []
        moving_avgs = []
        
        # Calculate moving averages
        for i in range(len(values) - window_size + 1):
            window = values[i:i+window_size]
            avg = sum(window) / len(window)
            moving_avgs.append(avg)
        
        # Identify trends by comparing consecutive moving averages
        for i in range(1, len(moving_avgs)):
            if moving_avgs[i] > moving_avgs[i-1]:
                trend = "up"
            elif moving_avgs[i] < moving_avgs[i-1]:
                trend = "down"
            else:
                trend = "flat"
            
            trends.append({
                "date": dates[i + window_size - 1],
                "value": values[i + window_size - 1],
                "moving_avg": moving_avgs[i],
                "trend": trend
            })
        
        # Identify overall trend
        up_count = sum(1 for t in trends if t["trend"] == "up")
        down_count = sum(1 for t in trends if t["trend"] == "down")
        flat_count = sum(1 for t in trends if t["trend"] == "flat")
        
        if up_count > down_count and up_count > flat_count:
            overall_trend = "upward"
        elif down_count > up_count and down_count > flat_count:
            overall_trend = "downward"
        else:
            overall_trend = "flat"
        
        return {
            "series_id": series_id,
            "title": title,
            "window_size": window_size,
            "overall_trend": overall_trend,
            "trend_details": trends
        }
    except Exception as e:
        logger.error(f"Error detecting trends: {str(e)}")
        return {"error": str(e)}