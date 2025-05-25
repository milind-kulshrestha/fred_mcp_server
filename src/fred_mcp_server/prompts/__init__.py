"""
Prompt templates for the FRED MCP server.

This module contains reusable prompt templates to guide users in using the 
available FRED analysis tools effectively.
"""

import logging
import mcp.types as types
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("fred-mcp-server.prompts")

# Define available prompts
PROMPTS = {
    "search-guidance": types.Prompt(
        name="search-guidance",
        description="How to effectively search FRED data series",
        arguments=[
            types.PromptArgument(
                name="topic",
                description="Economic topic you want to search for (e.g., inflation, GDP)",
                required=False
            )
        ],
    ),
    "data-analysis-guidance": types.Prompt(
        name="data-analysis-guidance",
        description="How to analyze FRED economic data",
        arguments=[
            types.PromptArgument(
                name="series_id",
                description="FRED series ID (e.g., 'GDP', 'UNRATE')",
                required=False
            )
        ],
    ),
    "economic-indicators-guide": types.Prompt(
        name="economic-indicators-guide",
        description="Understanding key economic indicators in FRED",
        arguments=[],
    ),
    "compare-indicators-guidance": types.Prompt(
        name="compare-indicators-guidance",
        description="How to compare multiple economic indicators",
        arguments=[
            types.PromptArgument(
                name="indicators",
                description="Comma-separated list of indicators to compare (e.g., 'GDP,UNRATE')",
                required=False
            )
        ],
    ),
    "seasonal-adjustment-guide": types.Prompt(
        name="seasonal-adjustment-guide",
        description="Understanding seasonal adjustments in economic data",
        arguments=[],
    )
}

# Default examples for common topics when API access is not available
DEFAULT_TOPIC_EXAMPLES = {
    "inflation": [
        {"id": "CPIAUCSL", "title": "Consumer Price Index for All Urban Consumers"},
        {"id": "PCEPI", "title": "Personal Consumption Expenditures Price Index"},
        {"id": "CPILFESL", "title": "Core Consumer Price Index"}
    ],
    "unemployment": [
        {"id": "UNRATE", "title": "Unemployment Rate"},
        {"id": "PAYEMS", "title": "All Employees, Total Nonfarm"},
        {"id": "ICSA", "title": "Initial Claims"}
    ],
    "gdp": [
        {"id": "GDP", "title": "Gross Domestic Product"},
        {"id": "GDPC1", "title": "Real Gross Domestic Product"},
        {"id": "A191RL1Q225SBEA", "title": "GDP Growth Rate"}
    ],
    "interest": [
        {"id": "FEDFUNDS", "title": "Federal Funds Effective Rate"},
        {"id": "DGS10", "title": "10-Year Treasury Constant Maturity Rate"},
        {"id": "MORTGAGE30US", "title": "30-Year Fixed Rate Mortgage Average"}
    ],
    "housing": [
        {"id": "HOUST", "title": "Housing Starts"},
        {"id": "CSUSHPINSA", "title": "Case-Shiller Home Price Index"},
        {"id": "HSN1F", "title": "New One Family Houses Sold"}
    ]
}

# Enhanced economic indicators with context
ECONOMIC_INDICATORS = {
    "GDP": {
        "id": "GDP",
        "alt_ids": ["GDPC1"],
        "description": "Measures the total value of goods and services produced",
        "frequency": "Quarterly",
        "when_to_use": "When assessing overall economic health and growth",
        "related_indicators": ["UNRATE", "CPIAUCSL", "FEDFUNDS"]
    },
    "UNRATE": {
        "id": "UNRATE",
        "description": "Percentage of the labor force that is unemployed",
        "frequency": "Monthly",
        "when_to_use": "When analyzing labor market conditions",
        "related_indicators": ["PAYEMS", "ICSA", "GDP"]
    },
    "CPIAUCSL": {
        "id": "CPIAUCSL",
        "description": "Consumer Price Index for All Urban Consumers",
        "frequency": "Monthly",
        "when_to_use": "When analyzing inflation and purchasing power",
        "related_indicators": ["PCEPI", "FEDFUNDS", "T10YIE"]
    },
    "FEDFUNDS": {
        "id": "FEDFUNDS",
        "description": "Federal Funds Effective Rate",
        "frequency": "Monthly",
        "when_to_use": "When analyzing monetary policy and interest rates",
        "related_indicators": ["DGS10", "CPIAUCSL", "GDP"]
    },
    "INDPRO": {
        "id": "INDPRO",
        "description": "Industrial Production Index",
        "frequency": "Monthly",
        "when_to_use": "When analyzing manufacturing sector health",
        "related_indicators": ["GDP", "UNRATE", "PCEPILFE"]
    }
}

async def handle_search_guidance(arguments: Dict[str, str], resource_manager=None) -> types.GetPromptResult:
    """Guide users on how to effectively search FRED data series with real examples."""
    topic = arguments.get("topic", "inflation").lower()
    
    # Try to get real examples if resource manager is available
    example_series = []
    if resource_manager:
        try:
            results = await resource_manager.search_series(topic, limit=3)
            for series in results[:3]:
                example_series.append({
                    "id": series.get("id"),
                    "title": series.get("title")
                })
            logger.info(f"Retrieved {len(example_series)} real examples for topic '{topic}'")
        except Exception as e:
            logger.warning(f"Failed to get real examples for {topic}: {str(e)}")
    
    # Use default examples if API call fails or resource_manager not provided
    if not example_series:
        # Find the closest matching topic or use inflation as default
        for key in DEFAULT_TOPIC_EXAMPLES.keys():
            if key in topic or topic in key:
                example_series = DEFAULT_TOPIC_EXAMPLES[key]
                break
        
        if not example_series and 'inflation' in DEFAULT_TOPIC_EXAMPLES:
            example_series = DEFAULT_TOPIC_EXAMPLES['inflation']
    
    # Format example series for display
    examples_text = "\n".join([f"- {series['id']}: {series['title']}" for series in example_series])
    
    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"I want to find information about {topic} in FRED data. What's the best approach?"
                )
            ),
            types.PromptMessage(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text=f"To search for information about {topic} in FRED data, I recommend using the `search_fred_series` tool with the following parameters:\n\n"
                         f"- Set `query` to a specific term related to {topic} (e.g., \"{topic} rate\" or \"{topic} index\")\n"
                         f"- Optional: Use `limit` to control the number of results (default: 10)\n"
                         f"- Optional: Use `order_by` to sort by relevance or popularity\n\n"
                         f"For example:\n"
                         f"```\n"
                         f"search_fred_series(query=\"{topic}\", limit=5)\n"
                         f"```\n\n"
                         f"Here are some relevant {topic}-related series to get you started:\n\n"
                         f"{examples_text}\n\n"
                         f"After finding a series ID of interest, use the `get_series_data` tool to retrieve the actual data points for analysis."
                )
            )
        ]
    )

async def handle_data_analysis_guidance(arguments: Dict[str, str], resource_manager=None) -> types.GetPromptResult:
    """Guide users on how to analyze FRED economic data with validation."""
    series_id = arguments.get("series_id", "GDP")
    
    # Validate series_id exists if resource manager is available
    series_exists = True
    series_title = None
    if resource_manager:
        try:
            metadata = await resource_manager.get_series_info(series_id=series_id)
            if metadata:
                series_title = metadata.get("title", series_id)
            else:
                series_exists = False
            logger.info(f"Validated series '{series_id}': exists={series_exists}")
        except Exception as e:
            logger.warning(f"Failed to validate series {series_id}: {str(e)}")
    
    # Adjust response based on validation
    if not series_exists and resource_manager:
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"How can I analyze the {series_id} data series from FRED?"
                    )
                ),
                types.PromptMessage(
                    role="assistant",
                    content=types.TextContent(
                        type="text",
                        text=f"The series ID '{series_id}' doesn't appear to be valid in FRED. "
                             f"Try using the `search_fred_series` tool first to find valid series IDs:\n\n"
                             f"```\n"
                             f"search_fred_series(query=\"{series_id.lower()}\")\n"
                             f"```\n\n"
                             f"Once you find a valid series ID, you can analyze it using the tools."
                    )
                )
            ]
        )
    
    # For valid series or when we can't validate
    title_text = f"{series_title} ({series_id})" if series_title else series_id
    
    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"How can I analyze the {series_id} data series from FRED?"
                )
            ),
            types.PromptMessage(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text=f"To analyze the {title_text} data series from FRED, follow these steps:\n\n"
                         f"1. First, retrieve the data using the `get_series_data` tool:\n"
                         f"   ```\n"
                         f"   get_series_data(series_id=\"{series_id}\", observation_start=\"2010-01-01\")\n"
                         f"   ```\n\n"
                         f"2. For basic statistics, use the `calculate_statistics` tool:\n"
                         f"   ```\n"
                         f"   calculate_statistics(series_id=\"{series_id}\")\n"
                         f"   ```\n\n"
                         f"3. To identify trends in the data, use the `detect_trends` tool:\n"
                         f"   ```\n"
                         f"   detect_trends(series_id=\"{series_id}\", window_size=3)\n"
                         f"   ```\n\n"
                         f"4. If you want to compare with related indicators, use the `compare_series` tool with multiple series IDs.\n\n"
                         f"These tools will help you understand the patterns, trends, and key metrics in the data."
                )
            )
        ]
    )

async def handle_economic_indicators_guide(arguments: Dict[str, str]) -> types.GetPromptResult:
    """Guide users on key economic indicators in FRED with enhanced context."""
    
    # Format enhanced indicator information
    enhanced_indicators_text = ""
    for key, indicator in ECONOMIC_INDICATORS.items():
        enhanced_indicators_text += f"**{indicator['id']}: {indicator['description']}**\n"
        enhanced_indicators_text += f"- Frequency: {indicator['frequency']}\n"
        enhanced_indicators_text += f"- When to use: {indicator['when_to_use']}\n"
        enhanced_indicators_text += f"- Related indicators: {', '.join(indicator['related_indicators'])}\n\n"
    
    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="What are the most important economic indicators available in FRED?"
                )
            ),
            types.PromptMessage(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text="FRED contains many important economic indicators. Here's a guide to the key ones with context:\n\n"
                         f"{enhanced_indicators_text}\n"
                         "These indicators can be combined to form a comprehensive view of economic conditions.\n"
                         "Try using `get_series_data()` with any of these IDs to start your analysis."
                )
            )
        ]
    )

async def handle_compare_indicators_guidance(arguments: Dict[str, str]) -> types.GetPromptResult:
    """Guide users on comparing multiple economic indicators."""
    indicators_raw = arguments.get("indicators", "GDP,UNRATE")
    indicators = [ind.strip() for ind in indicators_raw.split(",")]
    
    indicators_list = ", ".join([f"`{ind}`" for ind in indicators])
    indicators_args = ", ".join([f'"{ind}"' for ind in indicators])
    
    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"How can I compare {indicators_list} indicators?"
                )
            ),
            types.PromptMessage(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text=f"To compare {indicators_list}, follow these steps:\n\n"
                         f"1. Use the `compare_series` tool with the series IDs:\n"
                         f"   ```\n"
                         f"   compare_series(series_ids=[{indicators_args}], observation_start=\"2010-01-01\")\n"
                         f"   ```\n\n"
                         f"2. For meaningful comparison, consider:\n"
                         f"   - Different frequencies (GDP is quarterly, UNRATE is monthly)\n"
                         f"   - Different scales (normalize or use separate axes)\n"
                         f"   - Lagging vs. leading indicators\n\n"
                         f"3. To analyze correlation, look at whether indicators move together or oppositely.\n\n"
                         f"4. Consider economic theory: For example, unemployment typically falls as GDP rises."
                )
            )
        ]
    )

async def handle_seasonal_adjustment_guide(arguments: Dict[str, str]) -> types.GetPromptResult:
    """Guide users on understanding seasonal adjustments in economic data."""
    
    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="What is seasonal adjustment in economic data?"
                )
            ),
            types.PromptMessage(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text="**Seasonal Adjustment in Economic Data**\n\n"
                         "Seasonal adjustment is a statistical technique that removes regular seasonal fluctuations from economic time series data. Here's what you need to know:\n\n"
                         "**Why it matters:**\n"
                         "- Economic data often shows predictable patterns within a year (e.g., retail sales spike in December)\n"
                         "- Seasonal adjustment helps identify the underlying trend by removing these expected variations\n"
                         "- This makes it easier to spot actual economic changes versus regular seasonal patterns\n\n"
                         "**In FRED data:**\n"
                         "- Series ending with 'SA' are seasonally adjusted (e.g., `UNRATE`)\n"
                         "- Series ending with 'NSA' are not seasonally adjusted (e.g., `UNRATENSA`)\n"
                         "- Some series offer both versions so you can choose based on your analysis needs\n\n"
                         "**When to use each:**\n"
                         "- **Seasonally Adjusted (SA)**: When analyzing trends, business cycles, or month-to-month changes\n"
                         "- **Not Seasonally Adjusted (NSA)**: When analyzing seasonal patterns themselves or when actual values are needed\n\n"
                         "To compare different versions of the same indicator, use:\n"
                         "```\n"
                         "compare_series(series_ids=[\"UNRATE\", \"UNRATENSA\"])\n"
                         "```"
                )
            )
        ]
    )

# Mapping of prompt names to their handler functions
PROMPT_HANDLERS = {
    "search-guidance": handle_search_guidance,
    "data-analysis-guidance": handle_data_analysis_guidance,
    "economic-indicators-guide": handle_economic_indicators_guide,
    "compare-indicators-guidance": handle_compare_indicators_guidance,
    "seasonal-adjustment-guide": handle_seasonal_adjustment_guide
}