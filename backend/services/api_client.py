import os
import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
from urllib.parse import urlencode, quote

from models.schemas import HealthFacility, CommodityPrice, SchemeInfo, PoliticalRepresentative, PincodeInfo

logger = logging.getLogger(__name__)

class APIClient:
    """Client for handling all external API integrations"""
    
    def __init__(self):
        self.data_gov_api_key = os.getenv("DATA_GOV_API_KEY")
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.timeout = int(os.getenv("API_TIMEOUT", "30"))
        self.rate_limit = int(os.getenv("API_RATE_LIMIT", "100"))
        
        # API endpoints
        self.data_gov_base = "https://api.data.gov.in"
        self.health_facility_api = "https://facility.abdm.gov.in/api"
        self.pincode_api = "https://api.postalpincode.in"
        self.agmarknet_api = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
        
        # Session for connection pooling
        self.session = None
        
        # Rate limiting
        self.last_request_time = {}
        self.request_counts = {}
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': 'Rural-Survey-Bot/2.0 (Government Service Bot)',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _rate_limit_check(self, api_name: str):
        """Check and enforce rate limiting"""
        current_time = time.time()
        
        # Reset counter every minute
        if api_name not in self.last_request_time or \
           current_time - self.last_request_time[api_name] > 60:
            self.request_counts[api_name] = 0
            self.last_request_time[api_name] = current_time
        
        # Check if we've exceeded rate limit
        if self.request_counts.get(api_name, 0) >= self.rate_limit:
            wait_time = 60 - (current_time - self.last_request_time[api_name])
            if wait_time > 0:
                logger.warning(f"Rate limit reached for {api_name}, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.request_counts[api_name] = 0
                self.last_request_time[api_name] = time.time()
        
        self.request_counts[api_name] = self.request_counts.get(api_name, 0) + 1
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"API request failed: {response.status} - {url}")
                    return {"error": f"HTTP {response.status}", "url": url}
        except asyncio.TimeoutError:
            logger.error(f"API request timeout: {url}")
            return {"error": "timeout", "url": url}
        except Exception as e:
            logger.error(f"API request error: {str(e)} - {url}")
            return {"error": str(e), "url": url}
    
    async def get_health_facilities(self, location_info: Dict[str, Any]) -> List[HealthFacility]:
        """Get health facilities from ABDM and Data.gov.in APIs"""
        facilities = []
        
        try:
            await self._rate_limit_check("health_facilities")
            
            # Try ABDM API first
            if location_info.get("pincode"):
                abdm_facilities = await self._get_abdm_facilities(location_info["pincode"])
                facilities.extend(abdm_facilities)
            
            # Try Data.gov.in health directory
            if self.data_gov_api_key and location_info.get("district"):
                datagov_facilities = await self._get_datagov_health_facilities(location_info)
                facilities.extend(datagov_facilities)
            
            # Remove duplicates and sort by distance if available
            unique_facilities = []
            seen_names = set()
            
            for facility in facilities:
                if facility.name not in seen_names:
                    unique_facilities.append(facility)
                    seen_names.add(facility.name)
            
            return unique_facilities[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error getting health facilities: {str(e)}")
            return []
    
    async def _get_abdm_facilities(self, pincode: str) -> List[HealthFacility]:
        """Get facilities from ABDM API"""
        try:
            url = f"{self.health_facility_api}/facilities/search"
            params = {
                "pincode": pincode,
                "limit": 20
            }
            
            response = await self._make_request("GET", url, params=params)
            
            if "error" in response:
                return []
            
            facilities = []
            for item in response.get("facilities", []):
                facility = HealthFacility(
                    name=item.get("name", "Unknown"),
                    type=item.get("type", "Health Facility"),
                    address=item.get("address", ""),
                    pincode=pincode,
                    district=item.get("district", ""),
                    state=item.get("state", ""),
                    phone=item.get("phone"),
                    services=item.get("services", []),
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude")
                )
                facilities.append(facility)
            
            return facilities
            
        except Exception as e:
            logger.error(f"Error getting ABDM facilities: {str(e)}")
            return []
    
    async def _get_datagov_health_facilities(self, location_info: Dict[str, Any]) -> List[HealthFacility]:
        """Get facilities from Data.gov.in API"""
        try:
            if not self.data_gov_api_key:
                return []
            
            url = f"{self.data_gov_base}/resource/health-facilities"
            params = {
                "api-key": self.data_gov_api_key,
                "format": "json",
                "limit": 20
            }
            
            if location_info.get("district"):
                params["filters[district]"] = location_info["district"]
            if location_info.get("state"):
                params["filters[state]"] = location_info["state"]
            
            response = await self._make_request("GET", url, params=params)
            
            if "error" in response:
                return []
            
            facilities = []
            for item in response.get("records", []):
                facility = HealthFacility(
                    name=item.get("facility_name", "Unknown"),
                    type=item.get("facility_type", "Health Facility"),
                    address=item.get("address", ""),
                    pincode=item.get("pincode", ""),
                    district=item.get("district", ""),
                    state=item.get("state", ""),
                    phone=item.get("contact_number"),
                    services=item.get("services", "").split(",") if item.get("services") else []
                )
                facilities.append(facility)
            
            return facilities
            
        except Exception as e:
            logger.error(f"Error getting Data.gov.in health facilities: {str(e)}")
            return []
    
    async def get_commodity_prices(self, commodity: str, location_info: Dict[str, Any]) -> List[CommodityPrice]:
        """Get commodity prices from Agmarknet and other APIs"""
        prices = []
        
        try:
            await self._rate_limit_check("commodity_prices")
            
            # Try Agmarknet API (if available)
            agmarknet_prices = await self._get_agmarknet_prices(commodity, location_info)
            prices.extend(agmarknet_prices)
            
            # Try Data.gov.in commodity prices
            if self.data_gov_api_key:
                datagov_prices = await self._get_datagov_commodity_prices(commodity, location_info)
                prices.extend(datagov_prices)
            
            return prices[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error getting commodity prices: {str(e)}")
            return []
    
    async def _get_agmarknet_prices(self, commodity: str, location_info: Dict[str, Any]) -> List[CommodityPrice]:
        """Get prices from Agmarknet (this would need web scraping as they don't have a public API)"""
        # This is a placeholder - actual implementation would require web scraping
        # which we'll handle in the web_scraper service
        return []
    
    async def _get_datagov_commodity_prices(self, commodity: str, location_info: Dict[str, Any]) -> List[CommodityPrice]:
        """Get commodity prices from Data.gov.in"""
        try:
            if not self.data_gov_api_key:
                return []
            
            url = f"{self.data_gov_base}/resource/commodity-prices"
            params = {
                "api-key": self.data_gov_api_key,
                "format": "json",
                "limit": 20,
                "filters[commodity]": commodity
            }
            
            if location_info.get("state"):
                params["filters[state]"] = location_info["state"]
            
            response = await self._make_request("GET", url, params=params)
            
            if "error" in response:
                return []
            
            prices = []
            for item in response.get("records", []):
                price = CommodityPrice(
                    commodity=item.get("commodity", commodity),
                    variety=item.get("variety", "Common"),
                    market_name=item.get("market", "Unknown Market"),
                    mandi_id=item.get("mandi_id"),
                    price_per_unit=float(item.get("price", 0)),
                    unit=item.get("unit", "kg"),
                    date=datetime.fromisoformat(item.get("date", datetime.now().isoformat())),
                    district=item.get("district", ""),
                    state=item.get("state", ""),
                    source="data.gov.in"
                )
                prices.append(price)
            
            return prices
            
        except Exception as e:
            logger.error(f"Error getting Data.gov.in commodity prices: {str(e)}")
            return []
    
    async def get_scheme_info(self, scheme_name: str) -> Optional[SchemeInfo]:
        """Get government scheme information"""
        try:
            await self._rate_limit_check("scheme_info")
            
            # Try Data.gov.in schemes API
            if self.data_gov_api_key:
                scheme_info = await self._get_datagov_scheme_info(scheme_name)
                if scheme_info:
                    return scheme_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting scheme info: {str(e)}")
            return None
    
    async def _get_datagov_scheme_info(self, scheme_name: str) -> Optional[SchemeInfo]:
        """Get scheme info from Data.gov.in"""
        try:
            if not self.data_gov_api_key:
                return None
            
            url = f"{self.data_gov_base}/resource/government-schemes"
            params = {
                "api-key": self.data_gov_api_key,
                "format": "json",
                "q": scheme_name
            }
            
            response = await self._make_request("GET", url, params=params)
            
            if "error" in response or not response.get("records"):
                return None
            
            item = response["records"][0]  # Take first match
            
            scheme = SchemeInfo(
                scheme_name=item.get("scheme_name", scheme_name),
                description=item.get("description", ""),
                eligibility=item.get("eligibility", "").split(";") if item.get("eligibility") else [],
                benefits=item.get("benefits", "").split(";") if item.get("benefits") else [],
                application_process=item.get("application_process", "").split(";") if item.get("application_process") else [],
                required_documents=item.get("documents", "").split(";") if item.get("documents") else [],
                official_website=item.get("website"),
                helpline=item.get("helpline"),
                last_updated=datetime.now()
            )
            
            return scheme
            
        except Exception as e:
            logger.error(f"Error getting Data.gov.in scheme info: {str(e)}")
            return None
    
    async def get_pincode_info(self, pincode: str) -> Optional[PincodeInfo]:
        """Get pincode information"""
        try:
            await self._rate_limit_check("pincode_info")
            
            # Try postal pincode API
            pincode_info = await self._get_postal_pincode_info(pincode)
            if pincode_info:
                return pincode_info
            
            # Try Data.gov.in pincode API
            if self.data_gov_api_key:
                datagov_info = await self._get_datagov_pincode_info(pincode)
                if datagov_info:
                    return datagov_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting pincode info: {str(e)}")
            return None
    
    async def _get_postal_pincode_info(self, pincode: str) -> Optional[PincodeInfo]:
        """Get pincode info from postal API"""
        try:
            url = f"{self.pincode_api}/pincode/{pincode}"
            response = await self._make_request("GET", url)
            
            if "error" in response or response.get("Status") != "Success":
                return None
            
            post_offices = response.get("PostOffice", [])
            if not post_offices:
                return None
            
            main_office = post_offices[0]
            
            pincode_info = PincodeInfo(
                pincode=pincode,
                post_office=main_office.get("Name", ""),
                district=main_office.get("District", ""),
                state=main_office.get("State", ""),
                region=main_office.get("Region", ""),
                division=main_office.get("Division", ""),
                circle=main_office.get("Circle", ""),
                taluk=main_office.get("Taluk"),
                villages=[office.get("Name", "") for office in post_offices]
            )
            
            return pincode_info
            
        except Exception as e:
            logger.error(f"Error getting postal pincode info: {str(e)}")
            return None
    
    async def _get_datagov_pincode_info(self, pincode: str) -> Optional[PincodeInfo]:
        """Get pincode info from Data.gov.in"""
        try:
            if not self.data_gov_api_key:
                return None
            
            url = f"{self.data_gov_base}/resource/pincode-directory"
            params = {
                "api-key": self.data_gov_api_key,
                "format": "json",
                "filters[pincode]": pincode
            }
            
            response = await self._make_request("GET", url, params=params)
            
            if "error" in response or not response.get("records"):
                return None
            
            item = response["records"][0]
            
            pincode_info = PincodeInfo(
                pincode=pincode,
                post_office=item.get("post_office", ""),
                district=item.get("district", ""),
                state=item.get("state", ""),
                region=item.get("region", ""),
                division=item.get("division", ""),
                circle=item.get("circle", ""),
                taluk=item.get("taluk"),
                villages=[]
            )
            
            return pincode_info
            
        except Exception as e:
            logger.error(f"Error getting Data.gov.in pincode info: {str(e)}")
            return None
    
    async def get_mla_info(self, location_info: Dict[str, Any]) -> Optional[PoliticalRepresentative]:
        """Get MLA information (placeholder - would need specific API or scraping)"""
        # This would require scraping from state assembly websites
        # or using specific political representative APIs
        return None
    
    async def get_mp_info(self, location_info: Dict[str, Any]) -> Optional[PoliticalRepresentative]:
        """Get MP information (placeholder - would need specific API or scraping)"""
        # This would require scraping from Lok Sabha website
        # or using specific political representative APIs
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all API services"""
        health_results = {
            "status": "healthy",
            "services": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Test basic connectivity
        test_results = []
        
        # Test postal pincode API
        try:
            test_response = await self._get_postal_pincode_info("110001")
            test_results.append({
                "service": "postal_api",
                "status": "healthy" if test_response else "degraded",
                "response_time_ms": 0  # You could measure this
            })
        except Exception as e:
            test_results.append({
                "service": "postal_api",
                "status": "unhealthy",
                "error": str(e)
            })
        
        # Test Data.gov.in API if key is available
        if self.data_gov_api_key:
            try:
                url = f"{self.data_gov_base}/resource/test"
                response = await self._make_request("GET", url, params={"api-key": self.data_gov_api_key})
                test_results.append({
                    "service": "data_gov_api",
                    "status": "healthy" if "error" not in response else "degraded"
                })
            except Exception as e:
                test_results.append({
                    "service": "data_gov_api",
                    "status": "unhealthy",
                    "error": str(e)
                })
        
        # Determine overall status
        healthy_services = sum(1 for result in test_results if result["status"] == "healthy")
        total_services = len(test_results)
        
        if healthy_services == total_services:
            health_results["status"] = "healthy"
        elif healthy_services > 0:
            health_results["status"] = "degraded"
        else:
            health_results["status"] = "unhealthy"
        
        health_results["services"] = {result["service"]: result for result in test_results}
        
        return health_results
    
    # Test methods for health checks
    async def test_data_gov_api(self) -> Dict[str, Any]:
        """Test Data.gov.in API"""
        if not self.data_gov_api_key:
            return {"status": "skip", "message": "API key not configured"}
        
        try:
            start_time = time.time()
            url = f"{self.data_gov_base}/resource/test"
            response = await self._make_request("GET", url, params={"api-key": self.data_gov_api_key})
            end_time = time.time()
            
            return {
                "status": "success" if "error" not in response else "fail",
                "response_time_ms": (end_time - start_time) * 1000,
                "details": response
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    async def test_health_facility_api(self) -> Dict[str, Any]:
        """Test health facility API"""
        try:
            start_time = time.time()
            facilities = await self._get_abdm_facilities("110001")
            end_time = time.time()
            
            return {
                "status": "success" if facilities else "fail",
                "response_time_ms": (end_time - start_time) * 1000,
                "facilities_found": len(facilities)
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    async def test_pincode_api(self) -> Dict[str, Any]:
        """Test pincode API"""
        try:
            start_time = time.time()
            pincode_info = await self._get_postal_pincode_info("110001")
            end_time = time.time()
            
            return {
                "status": "success" if pincode_info else "fail",
                "response_time_ms": (end_time - start_time) * 1000,
                "pincode_resolved": bool(pincode_info)
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    async def test_agmarknet_api(self) -> Dict[str, Any]:
        """Test Agmarknet API (placeholder)"""
        # Agmarknet doesn't have a public API, so this would test web scraping capability
        return {"status": "skip", "message": "Agmarknet requires web scraping"}
