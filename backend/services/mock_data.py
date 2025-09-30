import os
import json
import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from models.schemas import (
    HealthFacility, CommodityPrice, SchemeInfo, PoliticalRepresentative, 
    PincodeInfo, MockHealthFacility, MockCommodityPrices, MockSchemeInfo, MockPincodeDirectory
)

logger = logging.getLogger(__name__)

class MockDataService:
    """Service for providing mock/fallback data when APIs are unavailable"""
    
    def __init__(self):
        self.use_mock_data = os.getenv("USE_MOCK_DATA", "True").lower() == "true"
        self.mock_probability = float(os.getenv("MOCK_DATA_PROBABILITY", "0.3"))
        self.data_dir = "data/mock"
        
        # In-memory cache for mock data
        self.mock_cache = {}
        
        # Initialize mock data
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock data in memory"""
        try:
            # Health facilities mock data
            self.mock_cache["health_facilities"] = self._generate_health_facilities_data()
            
            # Commodity prices mock data
            self.mock_cache["commodity_prices"] = self._generate_commodity_prices_data()
            
            # Scheme information mock data
            self.mock_cache["scheme_info"] = self._generate_scheme_info_data()
            
            # Pincode directory mock data
            self.mock_cache["pincode_directory"] = self._generate_pincode_directory_data()
            
            # Political representatives mock data
            self.mock_cache["political_representatives"] = self._generate_political_representatives_data()
            
            # General FAQ mock data
            self.mock_cache["general_faq"] = self._generate_general_faq_data()
            
            logger.info("Mock data initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing mock data: {str(e)}")
    
    def _generate_health_facilities_data(self) -> Dict[str, List[HealthFacility]]:
        """Generate mock health facilities data"""
        facilities_by_pincode = {}
        
        # Sample pincodes and their facilities
        sample_data = {
            "110001": [
                {
                    "name": "Ram Manohar Lohia Hospital",
                    "type": "Government Hospital",
                    "address": "Baba Kharak Singh Marg, New Delhi",
                    "pincode": "110001",
                    "district": "New Delhi",
                    "state": "Delhi",
                    "phone": "011-23365525",
                    "services": ["Emergency", "General Medicine", "Surgery", "Cardiology"],
                    "distance_km": 2.5
                },
                {
                    "name": "Central Delhi PHC",
                    "type": "Primary Health Centre",
                    "address": "Connaught Place, New Delhi",
                    "pincode": "110001",
                    "district": "New Delhi",
                    "state": "Delhi",
                    "phone": "011-23341234",
                    "services": ["OPD", "Vaccination", "Maternal Care"],
                    "distance_km": 1.2
                }
            ],
            "560001": [
                {
                    "name": "Bowring and Lady Curzon Hospital",
                    "type": "Government Hospital",
                    "address": "Shivaji Nagar, Bangalore",
                    "pincode": "560001",
                    "district": "Bangalore Urban",
                    "state": "Karnataka",
                    "phone": "080-22227979",
                    "services": ["Emergency", "General Medicine", "Pediatrics"],
                    "distance_km": 3.0
                }
            ],
            "400001": [
                {
                    "name": "JJ Hospital",
                    "type": "Government Hospital",
                    "address": "Byculla, Mumbai",
                    "pincode": "400001",
                    "district": "Mumbai",
                    "state": "Maharashtra",
                    "phone": "022-23735555",
                    "services": ["Emergency", "Trauma", "General Medicine"],
                    "distance_km": 4.5
                }
            ]
        }
        
        for pincode, facilities_data in sample_data.items():
            facilities = []
            for facility_data in facilities_data:
                facility = HealthFacility(**facility_data)
                facilities.append(facility)
            facilities_by_pincode[pincode] = facilities
        
        return facilities_by_pincode
    
    def _generate_commodity_prices_data(self) -> Dict[str, List[CommodityPrice]]:
        """Generate mock commodity prices data"""
        prices_by_commodity = {}
        
        commodities = ["wheat", "rice", "onion", "potato", "tomato", "dal", "sugar"]
        states = ["Delhi", "Maharashtra", "Karnataka", "Punjab", "Uttar Pradesh"]
        
        for commodity in commodities:
            prices = []
            for state in states:
                # Generate random prices with some variation
                base_price = {
                    "wheat": 2500, "rice": 3000, "onion": 2000, "potato": 1500,
                    "tomato": 3500, "dal": 8000, "sugar": 4000
                }.get(commodity, 2000)
                
                price_variation = random.uniform(0.8, 1.2)
                final_price = base_price * price_variation
                
                price = CommodityPrice(
                    commodity=commodity,
                    variety="Common",
                    market_name=f"{state} Mandi",
                    price_per_unit=round(final_price, 2),
                    unit="quintal",
                    date=datetime.now() - timedelta(days=random.randint(0, 7)),
                    district=f"{state} District",
                    state=state,
                    source="mock_data"
                )
                prices.append(price)
            
            prices_by_commodity[commodity] = prices
        
        return prices_by_commodity
    
    def _generate_scheme_info_data(self) -> Dict[str, SchemeInfo]:
        """Generate mock scheme information data"""
        schemes = {}
        
        # PMAY Scheme
        schemes["pmay"] = SchemeInfo(
            scheme_name="Pradhan Mantri Awas Yojana",
            description="PMAY aims to provide affordable housing to all eligible families in urban and rural areas by 2024.",
            eligibility=[
                "Economically Weaker Section (EWS) families",
                "Low Income Group (LIG) families",
                "Middle Income Group (MIG) families",
                "First-time home buyers",
                "Families without pucca house"
            ],
            benefits=[
                "Interest subsidy on home loans up to Rs. 2.67 lakh",
                "Direct financial assistance for house construction",
                "Technical support and guidance",
                "Access to institutional credit"
            ],
            application_process=[
                "Visit nearest Common Service Center or apply online",
                "Fill application form with required details",
                "Submit necessary documents",
                "Verification by local authorities",
                "Approval and fund disbursement"
            ],
            required_documents=[
                "Aadhaar Card",
                "Income Certificate",
                "Bank Account Details",
                "Caste Certificate (if applicable)",
                "Property documents (if any)",
                "Passport size photographs"
            ],
            official_website="https://pmayg.nic.in",
            helpline="1800-11-6446",
            last_updated=datetime.now()
        )
        
        # Jan Aushadhi Scheme
        schemes["jan_aushadhi"] = SchemeInfo(
            scheme_name="Pradhan Mantri Bhartiya Janaushadhi Pariyojana",
            description="PMBJP aims to provide quality medicines at affordable prices to all through dedicated outlets called Janaushadhi Stores.",
            eligibility=[
                "All citizens can benefit from this scheme",
                "No income or category restrictions",
                "Available at Janaushadhi stores across India"
            ],
            benefits=[
                "Medicines at 50-90% lower prices",
                "Quality assured generic medicines",
                "Wide range of medicines available",
                "Easy accessibility through stores"
            ],
            application_process=[
                "Visit nearest Janaushadhi store",
                "Show prescription from registered doctor",
                "Purchase required medicines",
                "No application process required"
            ],
            required_documents=[
                "Doctor's prescription",
                "Identity proof (optional)"
            ],
            official_website="https://janaushadhi.gov.in",
            helpline="1800-180-5080",
            last_updated=datetime.now()
        )
        
        return schemes
    
    def _generate_pincode_directory_data(self) -> Dict[str, PincodeInfo]:
        """Generate mock pincode directory data"""
        pincodes = {}
        
        sample_pincodes = [
            {
                "pincode": "110001",
                "post_office": "Parliament Street",
                "district": "New Delhi",
                "state": "Delhi",
                "region": "Delhi",
                "division": "New Delhi",
                "circle": "Delhi",
                "villages": ["Connaught Place", "Janpath", "Parliament Street"]
            },
            {
                "pincode": "560001",
                "post_office": "Bangalore GPO",
                "district": "Bangalore Urban",
                "state": "Karnataka",
                "region": "Bangalore",
                "division": "Bangalore",
                "circle": "Karnataka",
                "villages": ["Shivaji Nagar", "Bangalore Cantonment", "High Grounds"]
            },
            {
                "pincode": "400001",
                "post_office": "Mumbai GPO",
                "district": "Mumbai",
                "state": "Maharashtra",
                "region": "Mumbai",
                "division": "Mumbai",
                "circle": "Maharashtra",
                "villages": ["Fort", "Ballard Estate", "Kala Ghoda"]
            }
        ]
        
        for pincode_data in sample_pincodes:
            pincode_info = PincodeInfo(**pincode_data)
            pincodes[pincode_data["pincode"]] = pincode_info
        
        return pincodes
    
    def _generate_political_representatives_data(self) -> Dict[str, List[PoliticalRepresentative]]:
        """Generate mock political representatives data"""
        representatives = {}
        
        # Sample data for different constituencies
        sample_data = {
            "new_delhi": [
                {
                    "name": "Sample MLA",
                    "position": "MLA",
                    "constituency": "New Delhi",
                    "party": "Sample Party",
                    "contact_info": {
                        "phone": "011-23456789",
                        "email": "mla.newdelhi@example.com"
                    },
                    "office_address": "Delhi Assembly, New Delhi",
                    "achievements": [
                        "Improved local infrastructure",
                        "Healthcare facility upgrades",
                        "Education initiatives"
                    ],
                    "source": "mock_data"
                },
                {
                    "name": "Sample MP",
                    "position": "MP",
                    "constituency": "New Delhi",
                    "party": "Sample Party",
                    "contact_info": {
                        "phone": "011-23456790",
                        "email": "mp.newdelhi@example.com"
                    },
                    "office_address": "Parliament House, New Delhi",
                    "achievements": [
                        "Policy advocacy",
                        "Development projects",
                        "Public welfare initiatives"
                    ],
                    "source": "mock_data"
                }
            ]
        }
        
        for constituency, reps_data in sample_data.items():
            representatives_list = []
            for rep_data in reps_data:
                rep = PoliticalRepresentative(**rep_data)
                representatives_list.append(rep)
            representatives[constituency] = representatives_list
        
        return representatives
    
    def _generate_general_faq_data(self) -> Dict[str, Dict[str, str]]:
        """Generate mock general FAQ data"""
        faqs = {
            "ration_card": {
                "question": "How to apply for ration card?",
                "answer": "To apply for a ration card: 1) Visit your local Food & Civil Supplies office, 2) Fill the application form, 3) Submit required documents (Aadhaar, address proof, income certificate), 4) Pay the application fee, 5) Wait for verification and approval.",
                "category": "food_security"
            },
            "aadhaar": {
                "question": "What documents are needed for Aadhaar card?",
                "answer": "For Aadhaar enrollment you need: 1) Proof of Identity (PAN card, passport, driving license), 2) Proof of Address (utility bills, bank statement, rent agreement), 3) Date of Birth proof (birth certificate, school certificate). Visit nearest Aadhaar center for enrollment.",
                "category": "identity"
            },
            "voter_id": {
                "question": "How to register for Voter ID?",
                "answer": "To register for Voter ID: 1) Visit National Voters' Service Portal (nvsp.in), 2) Fill Form 6 for new registration, 3) Upload required documents, 4) Submit application online or at local election office, 5) Wait for verification by election officials.",
                "category": "voting"
            },
            "pan_card": {
                "question": "How to apply for PAN card?",
                "answer": "To apply for PAN card: 1) Visit NSDL or UTIITSL website, 2) Fill Form 49A, 3) Upload photograph and signature, 4) Submit identity and address proof, 5) Pay application fee, 6) Submit application online or at PAN center.",
                "category": "taxation"
            }
        }
        
        return faqs
    
    async def get_health_facilities(self, location_info: Dict[str, Any]) -> List[HealthFacility]:
        """Get mock health facilities data"""
        try:
            pincode = location_info.get("pincode")
            
            if pincode and pincode in self.mock_cache["health_facilities"]:
                facilities = self.mock_cache["health_facilities"][pincode]
            else:
                # Return generic facilities for unknown pincodes
                facilities = [
                    HealthFacility(
                        name="District Hospital",
                        type="Government Hospital",
                        address=f"District Hospital, {location_info.get('district', 'Unknown District')}",
                        pincode=pincode or "000000",
                        district=location_info.get("district", "Unknown District"),
                        state=location_info.get("state", "Unknown State"),
                        phone="1800-180-1104",
                        services=["Emergency", "OPD", "General Medicine"],
                        distance_km=5.0
                    ),
                    HealthFacility(
                        name="Primary Health Centre",
                        type="PHC",
                        address=f"PHC, {location_info.get('village', 'Local Area')}",
                        pincode=pincode or "000000",
                        district=location_info.get("district", "Unknown District"),
                        state=location_info.get("state", "Unknown State"),
                        phone="108",
                        services=["OPD", "Vaccination", "Basic Treatment"],
                        distance_km=2.0
                    )
                ]
            
            return facilities
            
        except Exception as e:
            logger.error(f"Error getting mock health facilities: {str(e)}")
            return []
    
    async def get_commodity_prices(self, commodity: str, location_info: Dict[str, Any]) -> List[CommodityPrice]:
        """Get mock commodity prices data"""
        try:
            commodity_lower = commodity.lower()
            
            if commodity_lower in self.mock_cache["commodity_prices"]:
                prices = self.mock_cache["commodity_prices"][commodity_lower]
                
                # Filter by state if provided
                if location_info.get("state"):
                    state_prices = [p for p in prices if p.state.lower() == location_info["state"].lower()]
                    if state_prices:
                        return state_prices
                
                return prices
            else:
                # Generate random price for unknown commodity
                base_price = random.uniform(1000, 5000)
                price = CommodityPrice(
                    commodity=commodity,
                    variety="Common",
                    market_name=f"{location_info.get('state', 'Local')} Mandi",
                    price_per_unit=round(base_price, 2),
                    unit="quintal",
                    date=datetime.now(),
                    district=location_info.get("district", "Unknown District"),
                    state=location_info.get("state", "Unknown State"),
                    source="mock_data"
                )
                return [price]
            
        except Exception as e:
            logger.error(f"Error getting mock commodity prices: {str(e)}")
            return []
    
    async def get_scheme_info(self, scheme_name: str) -> Optional[SchemeInfo]:
        """Get mock scheme information"""
        try:
            scheme_key = scheme_name.lower()
            
            # Try exact match first
            for key, scheme in self.mock_cache["scheme_info"].items():
                if key in scheme_key or scheme_key in key:
                    return scheme
            
            # Return generic scheme info if not found
            return SchemeInfo(
                scheme_name=f"{scheme_name} Scheme",
                description=f"The {scheme_name} scheme is a government initiative aimed at providing benefits to eligible citizens.",
                eligibility=["Indian citizen", "Meet income criteria", "Age requirements as applicable"],
                benefits=["Financial assistance", "Subsidies", "Support services"],
                application_process=["Visit local office", "Fill application form", "Submit documents", "Wait for approval"],
                required_documents=["Aadhaar Card", "Income Certificate", "Address Proof", "Bank Details"],
                official_website="https://india.gov.in",
                helpline="1800-111-555",
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting mock scheme info: {str(e)}")
            return None
    
    async def get_pincode_info(self, pincode: str) -> Optional[PincodeInfo]:
        """Get mock pincode information"""
        try:
            if pincode in self.mock_cache["pincode_directory"]:
                return self.mock_cache["pincode_directory"][pincode]
            else:
                # Generate generic pincode info
                return PincodeInfo(
                    pincode=pincode,
                    post_office=f"Post Office {pincode}",
                    district="Unknown District",
                    state="Unknown State",
                    region="Unknown Region",
                    division="Unknown Division",
                    circle="Unknown Circle",
                    villages=[f"Village {i}" for i in range(1, 4)]
                )
            
        except Exception as e:
            logger.error(f"Error getting mock pincode info: {str(e)}")
            return None
    
    async def get_mla_info(self, location_info: Dict[str, Any]) -> Optional[PoliticalRepresentative]:
        """Get mock MLA information"""
        try:
            constituency = location_info.get("district", "unknown").lower()
            
            if constituency in self.mock_cache["political_representatives"]:
                reps = self.mock_cache["political_representatives"][constituency]
                mla_reps = [rep for rep in reps if rep.position == "MLA"]
                if mla_reps:
                    return mla_reps[0]
            
            # Return generic MLA info
            return PoliticalRepresentative(
                name="Local MLA",
                position="MLA",
                constituency=location_info.get("district", "Unknown Constituency"),
                party="Political Party",
                contact_info={
                    "phone": "1800-XXX-XXXX",
                    "email": "mla@example.com"
                },
                office_address="Assembly Office",
                achievements=["Infrastructure development", "Public welfare programs"],
                source="mock_data"
            )
            
        except Exception as e:
            logger.error(f"Error getting mock MLA info: {str(e)}")
            return None
    
    async def get_mp_info(self, location_info: Dict[str, Any]) -> Optional[PoliticalRepresentative]:
        """Get mock MP information"""
        try:
            constituency = location_info.get("district", "unknown").lower()
            
            if constituency in self.mock_cache["political_representatives"]:
                reps = self.mock_cache["political_representatives"][constituency]
                mp_reps = [rep for rep in reps if rep.position == "MP"]
                if mp_reps:
                    return mp_reps[0]
            
            # Return generic MP info
            return PoliticalRepresentative(
                name="Local MP",
                position="MP",
                constituency=location_info.get("district", "Unknown Constituency"),
                party="Political Party",
                contact_info={
                    "phone": "1800-XXX-XXXX",
                    "email": "mp@example.com"
                },
                office_address="Parliament House",
                achievements=["Policy advocacy", "Development projects"],
                source="mock_data"
            )
            
        except Exception as e:
            logger.error(f"Error getting mock MP info: {str(e)}")
            return None
    
    async def get_general_faq(self, question: str) -> Dict[str, Any]:
        """Get mock general FAQ response"""
        try:
            question_lower = question.lower()
            
            # Search for relevant FAQ
            for key, faq in self.mock_cache["general_faq"].items():
                if any(keyword in question_lower for keyword in key.split("_")):
                    return {
                        "answer": faq["answer"],
                        "category": faq["category"],
                        "source": "knowledge_base"
                    }
            
            # Return generic response
            return {
                "answer": "I understand you have a question about government services. For specific information, please contact your local government office or visit the official government portal at india.gov.in. You can also call the citizen helpline at 1800-111-555.",
                "category": "general",
                "source": "fallback"
            }
            
        except Exception as e:
            logger.error(f"Error getting mock FAQ response: {str(e)}")
            return {
                "answer": "I'm sorry, I couldn't process your question right now. Please try again later or contact local authorities for assistance.",
                "category": "error",
                "source": "error_fallback"
            }
    
    async def get_fallback_response(self, question: str) -> Dict[str, Any]:
        """Get fallback response when all services fail"""
        try:
            fallback_responses = [
                "I'm sorry, I'm having trouble accessing the latest information right now. Please try again in a few minutes or contact your local government office for immediate assistance.",
                "The service is temporarily unavailable. For urgent queries, please call the citizen helpline at 1800-111-555 or visit your nearest Common Service Center.",
                "I apologize for the inconvenience. The system is currently experiencing technical difficulties. Please retry your query or seek assistance from local authorities.",
                "Due to technical issues, I cannot provide real-time information at the moment. For government services, please visit india.gov.in or contact local offices directly."
            ]
            
            return {
                "message": random.choice(fallback_responses),
                "source": "fallback",
                "suggestions": [
                    "Try asking about government schemes",
                    "Ask for health facilities near you",
                    "Inquire about commodity prices",
                    "Get information about your representatives"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating fallback response: {str(e)}")
            return {
                "message": "I'm experiencing technical difficulties. Please contact local authorities for assistance.",
                "source": "error_fallback"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check mock data service health"""
        try:
            # Check if mock data is loaded
            required_keys = ["health_facilities", "commodity_prices", "scheme_info", "pincode_directory"]
            
            missing_keys = [key for key in required_keys if key not in self.mock_cache]
            
            if missing_keys:
                return {
                    "status": "unhealthy",
                    "message": f"Missing mock data: {missing_keys}"
                }
            
            # Check data counts
            data_counts = {key: len(data) for key, data in self.mock_cache.items()}
            
            return {
                "status": "healthy",
                "message": "Mock data service operational",
                "data_counts": data_counts,
                "use_mock_data": self.use_mock_data,
                "mock_probability": self.mock_probability
            }
            
        except Exception as e:
            logger.error(f"Mock data health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Mock data service error: {str(e)}"
            }

# Initialize mock data on module import
async def initialize_mock_data():
    """Initialize mock data service"""
    try:
        mock_service = MockDataService()
        logger.info("Mock data service initialized")
        return mock_service
    except Exception as e:
        logger.error(f"Failed to initialize mock data service: {str(e)}")
        raise
