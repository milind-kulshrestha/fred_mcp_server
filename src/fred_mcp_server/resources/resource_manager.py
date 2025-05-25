"""
Resource management for the FRED MCP server.

Provides high-level access to FRED API resources.
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from .fred_api_client import FREDAPIClient, FREDAPIError


class FREDResourceManager:
    """
    Manages FRED API resources.
    
    Provides methods to access FRED data.
    """
    
    def __init__(self, api_key: str, 
                 base_url: str = "https://api.stlouisfed.org/fred",
                 rate_limit: int = 100, period: int = 60):
        """
        Initialize the FRED resource manager.
        
        Args:
            api_key: API key for authenticating with the FRED API
            base_url: Base URL for the FRED API
            rate_limit: Maximum number of requests per period
            period: Time period in seconds for rate limiting
        """
        self.client = FREDAPIClient(api_key, base_url, rate_limit, period)
        
    async def check_health(self) -> bool:
        """
        Check the health of the FRED API connection.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        import logging
        logger = logging.getLogger("fred-resource-manager")
        logger.info("Checking FRED API health...")
        
        try:
            # Try to fetch a simple resource to check if the API is accessible
            result = await self.client.get_series_info("GDP")
            
            # Log the full response for debugging
            try:
                logger.info(f"API response: {json.dumps(result)[:250] if result else 'None'}")
            except:
                logger.info(f"API response (raw): {str(result)[:250] if result else 'None'}")
            
            # More permissive validation - just check that we got a non-empty response
            if result:
                # If we got any response data, consider it successful even if not in the exact format we expected
                logger.info("API connection successful - received data from FRED API")
                return True
            else:
                logger.warning("API connection returned empty response")
                return False
                
        except Exception as e:
            logger.error(f"FRED API health check failed: {str(e)}")
            return False
    
    async def search_series(self, search_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for economic data series by keywords.
        
        Args:
            search_text: Keywords to search for
            limit: Maximum number of results
            
        Returns:
            List of matching series
        """
        params = {
            "search_text": search_text,
            "limit": limit
        }
        
        data = await self.client.make_request("series/search", params)
        return data.get("seriess", [])
    
    async def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata about a specific series.
        
        Args:
            series_id: FRED series identifier
            
        Returns:
            Series metadata
        """
        params = {
            "series_id": series_id
        }
        
        data = await self.client.make_request("series", params)
        if "seriess" in data and data["seriess"]:
            return data["seriess"][0]
        return {}
    
    async def get_observations(self, series_id: str, observation_start: Optional[str] = None,
                             observation_end: Optional[str] = None, 
                             frequency: Optional[str] = None,
                             units: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the actual time series data.
        
        Args:
            series_id: FRED series identifier
            observation_start: Start date (YYYY-MM-DD)
            observation_end: End date (YYYY-MM-DD)
            frequency: Frequency of observations (e.g., 'd', 'w', 'm', 'q', 'a')
            units: Units transformation (e.g., 'lin', 'chg', 'ch1', 'pch', 'pc1', 'pca')
            
        Returns:
            Series observations data
        """
        params = {
            "series_id": series_id
        }
        
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        if frequency:
            params["frequency"] = frequency
        if units:
            params["units"] = units
        
        data = await self.client.make_request("series/observations", params)
        
        # Add series info to the response
        series_info = await self.get_series_info(series_id)
        
        return {
            "observations": data.get("observations", []),
            "series_info": series_info
        }
    
    async def search_by_tags(self, tags: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for series using FRED tags.
        
        Args:
            tags: List of FRED tags
            limit: Maximum number of results
            
        Returns:
            List of matching series
        """
        params = {
            "tag_names": ",".join(tags),
            "limit": limit
        }
        
        data = await self.client.make_request("tags/series", params)
        return data.get("seriess", [])
    
    async def list_categories(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get category hierarchies to browse data.
        
        Args:
            parent_id: Parent category ID
            
        Returns:
            List of categories
        """
        params = {}
        if parent_id is not None:
            params["parent_id"] = parent_id
        
        endpoint = "category/children" if parent_id is not None else "category"
        
        data = await self.client.make_request(endpoint, params)
        return data.get("categories", [])
    
    async def list_releases(self) -> List[Dict[str, Any]]:
        """
        Get release information and schedules.
        
        Returns:
            List of releases
        """
        params = {}
        
        data = await self.client.make_request("releases", params)
        return data.get("releases", [])
    
    async def get_related_series(self, series_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find related data series.
        
        Args:
            series_id: FRED series identifier
            limit: Maximum number of results
            
        Returns:
            List of related series
        """
        params = {
            "series_id": series_id,
            "limit": limit
        }
        
        data = await self.client.make_request("series/related_tags", params)
        
        # Now get series for these tags
        if "tags" in data and data["tags"]:
            tag_names = [tag["name"] for tag in data["tags"][:5]]  # Use top 5 tags
            return await self.search_by_tags(tag_names, limit)
        
        return []
    
    async def get_series_categories(self, series_id: str) -> List[Dict[str, Any]]:
        """
        Get categories for a series.
        
        Args:
            series_id: FRED series identifier
            
        Returns:
            List of categories
        """
        params = {
            "series_id": series_id
        }
        
        data = await self.client.make_request("series/categories", params)
        return data.get("categories", [])
    
    async def get_vintage_data(self, series_id: str, vintage_dates: List[str]) -> Dict[str, Any]:
        """
        Get historical versions of data.
        
        Args:
            series_id: FRED series identifier
            vintage_dates: List of vintage dates (YYYY-MM-DD)
            
        Returns:
            Vintage data for the series
        """
        # We need to fetch each vintage date separately
        results = {}
        
        for date in vintage_dates:
            params = {
                "series_id": series_id,
                "vintage_dates": date
            }
            
            data = await self.client.make_request("series/observations", params)
            results[date] = data.get("observations", [])
        
        return {
            "series_id": series_id,
            "vintages": results
        }
