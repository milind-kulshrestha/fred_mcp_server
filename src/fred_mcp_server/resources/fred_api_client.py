"""
FRED API client with rate limiting.
"""
import time
import asyncio
from typing import Dict, Any, List, Optional

import aiohttp


class FREDAPIError(Exception):
    """Exception raised for FRED API errors."""
    pass


class FREDAPIClient:
    """Handles FRED API communication with rate limiting."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.stlouisfed.org/fred",
                 rate_limit: int = 100, period: int = 60):
        """
        Initialize the FRED API client.
        
        Args:
            api_key: API key for authenticating with the FRED API
            base_url: Base URL for the FRED API
            rate_limit: Maximum number of requests per period
            period: Time period in seconds for rate limiting
        """
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.period = period
        self.request_times: List[float] = []
    
    async def make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a rate-limited request to the FRED API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters for the request
            
        Returns:
            JSON response from the API
            
        Raises:
            FREDAPIError: If the request fails
        """
        # Enforce rate limiting
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < self.period]
        
        if len(self.request_times) >= self.rate_limit:
            wait_time = self.period - (now - self.request_times[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                
        # Add current request time
        self.request_times.append(time.time())
        
        # Construct URL
        url = f"{self.base_url}/{endpoint}"
        
        # Add API key
        params["api_key"] = self.api_key
        params["file_type"] = "json"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise FREDAPIError(f"API error ({response.status}): {error_text}")
                    
                    data = await response.json()
                    return data
        except aiohttp.ClientError as e:
            raise FREDAPIError(f"Request failed: {str(e)}")
    
    async def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get information about a specific FRED data series.
        
        Args:
            series_id: The FRED series identifier
            
        Returns:
            Series information
            
        Raises:
            FREDAPIError: If the request fails
        """
        params = {
            "series_id": series_id
        }
        try:
            return await self.make_request("series", params)
        except Exception as e:
            raise FREDAPIError(f"Failed to get series info: {str(e)}")
