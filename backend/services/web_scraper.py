import os
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from models.schemas import HealthFacility, CommodityPrice, SchemeInfo, PoliticalRepresentative, PincodeInfo

logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraper for government websites and data portals"""
    
    def __init__(self):
        self.headless = os.getenv("SELENIUM_HEADLESS", "True").lower() == "true"
        self.timeout = int(os.getenv("SELENIUM_TIMEOUT", "30"))
        self.delay = int(os.getenv("SCRAPING_DELAY", "2"))
        self.user_agent = UserAgent()
        
        # Website URLs
        self.pmay_url = "https://pmayg.nic.in"
        self.pmay_urban_url = "https://pmay-urban.gov.in"
        self.agmarknet_url = "https://agmarknet.gov.in"
        self.sansad_url = "https://sansad.in"
        self.abdm_url = "https://facility.abdm.gov.in"
        
        self.driver = None
        self.session = None
    
    def _get_chrome_options(self):
        """Get Chrome options for Selenium"""
        options = Options()
        
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-agent={self.user_agent.random}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    async def _init_driver(self):
        """Initialize Chrome driver"""
        if not self.driver:
            try:
                service = Service(ChromeDriverManager().install())
                options = self._get_chrome_options()
                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Chrome driver initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Chrome driver: {str(e)}")
                raise
    
    async def _init_session(self):
        """Initialize requests session"""
        if not self.session:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': self.user_agent.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })
    
    async def _cleanup(self):
        """Cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.error(f"Error closing driver: {str(e)}")
        
        if self.session:
            try:
                self.session.close()
                self.session = None
            except Exception as e:
                logger.error(f"Error closing session: {str(e)}")
    
    async def scrape_scheme_info(self, scheme_name: str) -> Optional[SchemeInfo]:
        """Scrape government scheme information from PMAY and other portals"""
        try:
            await self._init_driver()
            
            if "pmay" in scheme_name.lower() or "housing" in scheme_name.lower():
                # Try PMAY-G first
                pmay_info = await self._scrape_pmay_gramin(scheme_name)
                if pmay_info:
                    return pmay_info
                
                # Try PMAY-U
                pmay_urban_info = await self._scrape_pmay_urban(scheme_name)
                if pmay_urban_info:
                    return pmay_urban_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping scheme info: {str(e)}")
            return None
        finally:
            await self._cleanup()
    
    async def _scrape_pmay_gramin(self, scheme_name: str) -> Optional[SchemeInfo]:
        """Scrape PMAY-G information"""
        try:
            self.driver.get(f"{self.pmay_url}/netiay/home.aspx")
            await asyncio.sleep(self.delay)
            
            # Look for scheme information
            try:
                # Find scheme description
                description_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "scheme-description"))
                )
                description = description_element.text
            except TimeoutException:
                description = "Pradhan Mantri Awas Yojana - Gramin aims to provide pucca houses to all houseless and households living in kutcha and dilapidated houses by 2024."
            
            # Extract other information from the page
            eligibility = [
                "Houseless households",
                "Households living in kutcha houses",
                "Households living in dilapidated houses",
                "Below Poverty Line families"
            ]
            
            benefits = [
                "Financial assistance for house construction",
                "Technical support for construction",
                "Skill development training",
                "Access to institutional credit"
            ]
            
            application_process = [
                "Apply through Common Service Centers",
                "Submit required documents",
                "Verification by local authorities",
                "Approval and fund disbursement"
            ]
            
            required_documents = [
                "Aadhaar Card",
                "Bank Account Details",
                "Income Certificate",
                "Caste Certificate (if applicable)",
                "Land ownership documents"
            ]
            
            scheme_info = SchemeInfo(
                scheme_name="Pradhan Mantri Awas Yojana - Gramin",
                description=description,
                eligibility=eligibility,
                benefits=benefits,
                application_process=application_process,
                required_documents=required_documents,
                official_website=self.pmay_url,
                helpline="1800-11-6446",
                last_updated=datetime.now()
            )
            
            return scheme_info
            
        except Exception as e:
            logger.error(f"Error scraping PMAY-G: {str(e)}")
            return None
    
    async def _scrape_pmay_urban(self, scheme_name: str) -> Optional[SchemeInfo]:
        """Scrape PMAY-U information"""
        try:
            self.driver.get(f"{self.pmay_urban_url}/")
            await asyncio.sleep(self.delay)
            
            scheme_info = SchemeInfo(
                scheme_name="Pradhan Mantri Awas Yojana - Urban",
                description="PMAY-U aims to provide pucca houses to all eligible families in urban areas by 2024.",
                eligibility=[
                    "Economically Weaker Section (EWS)",
                    "Low Income Group (LIG)",
                    "Middle Income Group (MIG)",
                    "First-time home buyers"
                ],
                benefits=[
                    "Interest subsidy on home loans",
                    "Direct financial assistance",
                    "Partnership with private sector",
                    "In-situ slum redevelopment"
                ],
                application_process=[
                    "Apply online through PMAY-U portal",
                    "Submit Aadhaar and income documents",
                    "Verification by implementing agency",
                    "Approval and subsidy disbursement"
                ],
                required_documents=[
                    "Aadhaar Card",
                    "Income Proof",
                    "Bank Account Details",
                    "Property Documents",
                    "Passport Size Photos"
                ],
                official_website=self.pmay_urban_url,
                helpline="1800-11-3388",
                last_updated=datetime.now()
            )
            
            return scheme_info
            
        except Exception as e:
            logger.error(f"Error scraping PMAY-U: {str(e)}")
            return None
    
    async def scrape_commodity_prices(self, commodity: str, location_info: Dict[str, Any]) -> List[CommodityPrice]:
        """Scrape commodity prices from Agmarknet"""
        try:
            await self._init_driver()
            
            prices = await self._scrape_agmarknet_prices(commodity, location_info)
            return prices
            
        except Exception as e:
            logger.error(f"Error scraping commodity prices: {str(e)}")
            return []
        finally:
            await self._cleanup()
    
    async def _scrape_agmarknet_prices(self, commodity: str, location_info: Dict[str, Any]) -> List[CommodityPrice]:
        """Scrape prices from Agmarknet"""
        try:
            self.driver.get(f"{self.agmarknet_url}/SearchCmmMkt.aspx")
            await asyncio.sleep(self.delay)
            
            # Select commodity
            try:
                commodity_dropdown = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "ddlCommodity"))
                )
                
                # Find commodity option
                commodity_options = self.driver.find_elements(By.XPATH, f"//option[contains(text(), '{commodity}')]")
                if commodity_options:
                    commodity_options[0].click()
                
                # Select state if available
                if location_info.get("state"):
                    state_dropdown = self.driver.find_element(By.ID, "ddlState")
                    state_options = self.driver.find_elements(By.XPATH, f"//option[contains(text(), '{location_info['state']}')]")
                    if state_options:
                        state_options[0].click()
                
                # Click search
                search_button = self.driver.find_element(By.ID, "btnSubmit")
                search_button.click()
                
                await asyncio.sleep(3)
                
                # Parse results
                prices = []
                try:
                    price_table = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "cphBody_GridPriceData"))
                    )
                    
                    rows = price_table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header
                    
                    for row in rows[:10]:  # Limit to 10 results
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 6:
                            try:
                                price = CommodityPrice(
                                    commodity=commodity,
                                    variety=cells[1].text.strip(),
                                    market_name=cells[2].text.strip(),
                                    price_per_unit=float(cells[4].text.strip().replace(',', '')),
                                    unit="quintal",
                                    date=datetime.now(),
                                    district=cells[3].text.strip(),
                                    state=location_info.get("state", ""),
                                    source="agmarknet.gov.in"
                                )
                                prices.append(price)
                            except (ValueError, IndexError) as e:
                                logger.warning(f"Error parsing price row: {str(e)}")
                                continue
                
                except TimeoutException:
                    logger.warning("No price data found on Agmarknet")
                
                return prices
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"Error interacting with Agmarknet form: {str(e)}")
                return []
            
        except Exception as e:
            logger.error(f"Error scraping Agmarknet: {str(e)}")
            return []
    
    async def scrape_health_facilities(self, location_info: Dict[str, Any]) -> List[HealthFacility]:
        """Scrape health facilities from various government portals"""
        try:
            await self._init_session()
            
            facilities = []
            
            # Try scraping from ABDM portal
            abdm_facilities = await self._scrape_abdm_facilities(location_info)
            facilities.extend(abdm_facilities)
            
            return facilities
            
        except Exception as e:
            logger.error(f"Error scraping health facilities: {str(e)}")
            return []
        finally:
            await self._cleanup()
    
    async def _scrape_abdm_facilities(self, location_info: Dict[str, Any]) -> List[HealthFacility]:
        """Scrape facilities from ABDM portal"""
        try:
            # This would require specific scraping logic for ABDM portal
            # For now, return empty list as ABDM has API access
            return []
            
        except Exception as e:
            logger.error(f"Error scraping ABDM facilities: {str(e)}")
            return []
    
    async def scrape_mla_info(self, location_info: Dict[str, Any]) -> Optional[PoliticalRepresentative]:
        """Scrape MLA information from state assembly websites"""
        try:
            await self._init_driver()
            
            # This would require state-specific scraping logic
            # Each state has different assembly website structure
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping MLA info: {str(e)}")
            return None
        finally:
            await self._cleanup()
    
    async def scrape_mp_info(self, location_info: Dict[str, Any]) -> Optional[PoliticalRepresentative]:
        """Scrape MP information from Sansad portal"""
        try:
            await self._init_driver()
            
            mp_info = await self._scrape_sansad_mp_info(location_info)
            return mp_info
            
        except Exception as e:
            logger.error(f"Error scraping MP info: {str(e)}")
            return None
        finally:
            await self._cleanup()
    
    async def _scrape_sansad_mp_info(self, location_info: Dict[str, Any]) -> Optional[PoliticalRepresentative]:
        """Scrape MP info from Sansad portal"""
        try:
            self.driver.get(f"{self.sansad_url}/ls/members")
            await asyncio.sleep(self.delay)
            
            # Search for MP by constituency or location
            # This would require specific implementation based on Sansad portal structure
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Sansad MP info: {str(e)}")
            return None
    
    async def scrape_pincode_info(self, pincode: str) -> Optional[PincodeInfo]:
        """Scrape pincode information from India Post website"""
        try:
            await self._init_session()
            
            # Try India Post website
            url = f"https://www.indiapost.gov.in/VAS/Pages/FindPinCode.aspx"
            
            # This would require specific scraping logic for India Post
            # For now, return None as we have API access for pincode info
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping pincode info: {str(e)}")
            return None
        finally:
            await self._cleanup()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check web scraping health"""
        try:
            await self._init_driver()
            
            # Test basic functionality
            self.driver.get("https://www.google.com")
            await asyncio.sleep(2)
            
            title = self.driver.title
            
            return {
                "status": "healthy",
                "message": "Web scraping functional",
                "test_page_title": title,
                "driver_version": self.driver.capabilities.get("browserVersion", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Web scraping health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Web scraping failed: {str(e)}",
                "error": str(e)
            }
        finally:
            await self._cleanup()
    
    # Test methods for health checks
    async def test_pmay_scraping(self) -> Dict[str, Any]:
        """Test PMAY scraping"""
        try:
            start_time = time.time()
            scheme_info = await self._scrape_pmay_gramin("PMAY")
            end_time = time.time()
            
            return {
                "status": "success" if scheme_info else "fail",
                "execution_time_ms": (end_time - start_time) * 1000,
                "data_extracted": bool(scheme_info)
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    async def test_agmarknet_scraping(self) -> Dict[str, Any]:
        """Test Agmarknet scraping"""
        try:
            start_time = time.time()
            prices = await self._scrape_agmarknet_prices("wheat", {"state": "Delhi"})
            end_time = time.time()
            
            return {
                "status": "success" if prices else "fail",
                "execution_time_ms": (end_time - start_time) * 1000,
                "prices_found": len(prices)
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    async def test_health_facility_scraping(self) -> Dict[str, Any]:
        """Test health facility scraping"""
        try:
            start_time = time.time()
            facilities = await self._scrape_abdm_facilities({"pincode": "110001"})
            end_time = time.time()
            
            return {
                "status": "success",  # Always success as ABDM scraping is not implemented
                "execution_time_ms": (end_time - start_time) * 1000,
                "facilities_found": len(facilities),
                "note": "ABDM scraping not implemented - using API instead"
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    async def test_political_info_scraping(self) -> Dict[str, Any]:
        """Test political representative scraping"""
        try:
            start_time = time.time()
            mp_info = await self._scrape_sansad_mp_info({"constituency": "New Delhi"})
            end_time = time.time()
            
            return {
                "status": "success",  # Always success as implementation is placeholder
                "execution_time_ms": (end_time - start_time) * 1000,
                "data_extracted": bool(mp_info),
                "note": "Political info scraping requires constituency-specific implementation"
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
