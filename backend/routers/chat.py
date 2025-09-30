from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import asyncio

from services.intent_detector import IntentDetector
from services.api_client import APIClient
from services.web_scraper import WebScraper
from services.mock_data import MockDataService
from services.response_generator import ResponseGenerator
from models.schemas import ChatRequest, ChatResponse, Intent

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
intent_detector = IntentDetector()
api_client = APIClient()
web_scraper = WebScraper()
mock_data_service = MockDataService()
response_generator = ResponseGenerator()

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Main chatbot endpoint that handles all types of queries
    """
    try:
        logger.info(f"Received question: {request.question}")
        
        # Detect intent
        intent = await intent_detector.detect_intent(request.question)
        logger.info(f"Detected intent: {intent.name} (confidence: {intent.confidence})")
        
        # Route to appropriate handler based on intent
        response_data = None
        
        if intent.name == "survey_mla_name":
            response_data = await handle_survey_mla(request, intent)
        elif intent.name == "survey_mp_name":
            response_data = await handle_survey_mp(request, intent)
        elif intent.name == "ask_scheme_info":
            response_data = await handle_scheme_info(request, intent)
        elif intent.name == "ask_phc_location":
            response_data = await handle_phc_location(request, intent)
        elif intent.name == "ask_commodity_price":
            response_data = await handle_commodity_price(request, intent)
        elif intent.name == "ask_pincode_help":
            response_data = await handle_pincode_help(request, intent)
        elif intent.name == "general_faq":
            response_data = await handle_general_faq(request, intent)
        else:
            response_data = await handle_fallback(request, intent)
        
        # Generate response
        response = await response_generator.generate_response(
            intent=intent,
            data=response_data,
            language=request.language,
            context=request.context
        )
        
        return ChatResponse(
            response=response["message"],
            intent=intent.name,
            confidence=intent.confidence,
            data_source=response["source"],
            language=request.language,
            suggestions=response.get("suggestions", []),
            metadata=response.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        
        # Return fallback response
        fallback_response = await mock_data_service.get_fallback_response(request.question)
        
        return ChatResponse(
            response=fallback_response["message"],
            intent="fallback_handoff",
            confidence=0.0,
            data_source="mock",
            language=request.language,
            suggestions=["Try asking about government schemes", "Ask for health facilities near you"],
            metadata={"error": "Service temporarily unavailable"}
        )

async def handle_survey_mla(request: ChatRequest, intent: Intent) -> Dict[str, Any]:
    """Handle MLA survey questions"""
    try:
        # Extract location from context or question
        location_info = await extract_location_info(request)
        
        # Try API first
        try:
            mla_info = await api_client.get_mla_info(location_info)
            if mla_info:
                return {"type": "mla_info", "data": mla_info, "source": "api"}
        except Exception as e:
            logger.warning(f"API failed for MLA info: {str(e)}")
        
        # Try web scraping
        try:
            mla_info = await web_scraper.scrape_mla_info(location_info)
            if mla_info:
                return {"type": "mla_info", "data": mla_info, "source": "scraping"}
        except Exception as e:
            logger.warning(f"Web scraping failed for MLA info: {str(e)}")
        
        # Fallback to mock data
        mock_data = await mock_data_service.get_mla_info(location_info)
        return {"type": "mla_info", "data": mock_data, "source": "mock"}
        
    except Exception as e:
        logger.error(f"Error handling MLA survey: {str(e)}")
        raise

async def handle_survey_mp(request: ChatRequest, intent: Intent) -> Dict[str, Any]:
    """Handle MP survey questions"""
    try:
        location_info = await extract_location_info(request)
        
        # Try API first
        try:
            mp_info = await api_client.get_mp_info(location_info)
            if mp_info:
                return {"type": "mp_info", "data": mp_info, "source": "api"}
        except Exception as e:
            logger.warning(f"API failed for MP info: {str(e)}")
        
        # Try web scraping
        try:
            mp_info = await web_scraper.scrape_mp_info(location_info)
            if mp_info:
                return {"type": "mp_info", "data": mp_info, "source": "scraping"}
        except Exception as e:
            logger.warning(f"Web scraping failed for MP info: {str(e)}")
        
        # Fallback to mock data
        mock_data = await mock_data_service.get_mp_info(location_info)
        return {"type": "mp_info", "data": mock_data, "source": "mock"}
        
    except Exception as e:
        logger.error(f"Error handling MP survey: {str(e)}")
        raise

async def handle_scheme_info(request: ChatRequest, intent: Intent) -> Dict[str, Any]:
    """Handle government scheme information queries"""
    try:
        scheme_name = intent.entities.get("scheme_name", "PMAY")
        
        # Try API first
        try:
            scheme_info = await api_client.get_scheme_info(scheme_name)
            if scheme_info:
                return {"type": "scheme_info", "data": scheme_info, "source": "api"}
        except Exception as e:
            logger.warning(f"API failed for scheme info: {str(e)}")
        
        # Try web scraping
        try:
            scheme_info = await web_scraper.scrape_scheme_info(scheme_name)
            if scheme_info:
                return {"type": "scheme_info", "data": scheme_info, "source": "scraping"}
        except Exception as e:
            logger.warning(f"Web scraping failed for scheme info: {str(e)}")
        
        # Fallback to mock data
        mock_data = await mock_data_service.get_scheme_info(scheme_name)
        return {"type": "scheme_info", "data": mock_data, "source": "mock"}
        
    except Exception as e:
        logger.error(f"Error handling scheme info: {str(e)}")
        raise

async def handle_phc_location(request: ChatRequest, intent: Intent) -> Dict[str, Any]:
    """Handle PHC/health facility location queries"""
    try:
        location_info = await extract_location_info(request)
        
        # Try API first
        try:
            phc_info = await api_client.get_health_facilities(location_info)
            if phc_info:
                return {"type": "phc_info", "data": phc_info, "source": "api"}
        except Exception as e:
            logger.warning(f"API failed for PHC info: {str(e)}")
        
        # Try web scraping
        try:
            phc_info = await web_scraper.scrape_health_facilities(location_info)
            if phc_info:
                return {"type": "phc_info", "data": phc_info, "source": "scraping"}
        except Exception as e:
            logger.warning(f"Web scraping failed for PHC info: {str(e)}")
        
        # Fallback to mock data
        mock_data = await mock_data_service.get_health_facilities(location_info)
        return {"type": "phc_info", "data": mock_data, "source": "mock"}
        
    except Exception as e:
        logger.error(f"Error handling PHC location: {str(e)}")
        raise

async def handle_commodity_price(request: ChatRequest, intent: Intent) -> Dict[str, Any]:
    """Handle commodity price queries"""
    try:
        commodity_name = intent.entities.get("commodity_name", "wheat")
        location_info = await extract_location_info(request)
        
        # Try API first
        try:
            price_info = await api_client.get_commodity_prices(commodity_name, location_info)
            if price_info:
                return {"type": "price_info", "data": price_info, "source": "api"}
        except Exception as e:
            logger.warning(f"API failed for commodity prices: {str(e)}")
        
        # Try web scraping
        try:
            price_info = await web_scraper.scrape_commodity_prices(commodity_name, location_info)
            if price_info:
                return {"type": "price_info", "data": price_info, "source": "scraping"}
        except Exception as e:
            logger.warning(f"Web scraping failed for commodity prices: {str(e)}")
        
        # Fallback to mock data
        mock_data = await mock_data_service.get_commodity_prices(commodity_name, location_info)
        return {"type": "price_info", "data": mock_data, "source": "mock"}
        
    except Exception as e:
        logger.error(f"Error handling commodity price: {str(e)}")
        raise

async def handle_pincode_help(request: ChatRequest, intent: Intent) -> Dict[str, Any]:
    """Handle pincode information queries"""
    try:
        pincode = intent.entities.get("pincode")
        if not pincode:
            # Try to extract pincode from question
            import re
            pincode_match = re.search(r'\b\d{6}\b', request.question)
            if pincode_match:
                pincode = pincode_match.group()
        
        if not pincode:
            return {"type": "error", "data": {"message": "Please provide a valid 6-digit pincode"}, "source": "validation"}
        
        # Try API first
        try:
            pincode_info = await api_client.get_pincode_info(pincode)
            if pincode_info:
                return {"type": "pincode_info", "data": pincode_info, "source": "api"}
        except Exception as e:
            logger.warning(f"API failed for pincode info: {str(e)}")
        
        # Try web scraping
        try:
            pincode_info = await web_scraper.scrape_pincode_info(pincode)
            if pincode_info:
                return {"type": "pincode_info", "data": pincode_info, "source": "scraping"}
        except Exception as e:
            logger.warning(f"Web scraping failed for pincode info: {str(e)}")
        
        # Fallback to mock data
        mock_data = await mock_data_service.get_pincode_info(pincode)
        return {"type": "pincode_info", "data": mock_data, "source": "mock"}
        
    except Exception as e:
        logger.error(f"Error handling pincode help: {str(e)}")
        raise

async def handle_general_faq(request: ChatRequest, intent: Intent) -> Dict[str, Any]:
    """Handle general FAQ queries"""
    try:
        # Try to find relevant FAQ
        faq_response = await mock_data_service.get_general_faq(request.question)
        return {"type": "faq", "data": faq_response, "source": "knowledge_base"}
        
    except Exception as e:
        logger.error(f"Error handling general FAQ: {str(e)}")
        raise

async def handle_fallback(request: ChatRequest, intent: Intent) -> Dict[str, Any]:
    """Handle fallback cases"""
    try:
        fallback_response = await mock_data_service.get_fallback_response(request.question)
        return {"type": "fallback", "data": fallback_response, "source": "fallback"}
        
    except Exception as e:
        logger.error(f"Error handling fallback: {str(e)}")
        raise

async def extract_location_info(request: ChatRequest) -> Dict[str, Any]:
    """Extract location information from request"""
    location_info = {}
    
    # Check context for location info
    if request.context:
        location_info.update({
            "pincode": request.context.get("pincode"),
            "village": request.context.get("village"),
            "district": request.context.get("district"),
            "state": request.context.get("state"),
            "latitude": request.context.get("latitude"),
            "longitude": request.context.get("longitude")
        })
    
    # Try to extract from question text
    import re
    
    # Extract pincode
    pincode_match = re.search(r'\b\d{6}\b', request.question)
    if pincode_match and not location_info.get("pincode"):
        location_info["pincode"] = pincode_match.group()
    
    return {k: v for k, v in location_info.items() if v is not None}

@router.get("/intents")
async def get_supported_intents():
    """Get list of supported intents"""
    return {
        "intents": [
            {
                "name": "survey_mla_name",
                "description": "Ask about MLA information",
                "examples": ["Who is my MLA?", "Tell me about my local MLA"]
            },
            {
                "name": "survey_mp_name", 
                "description": "Ask about MP information",
                "examples": ["Who is my MP?", "Tell me about my Member of Parliament"]
            },
            {
                "name": "ask_scheme_info",
                "description": "Get information about government schemes",
                "examples": ["What is PMAY scheme?", "Tell me about housing scheme"]
            },
            {
                "name": "ask_phc_location",
                "description": "Find nearby health facilities",
                "examples": ["Find hospitals near me", "Where is the nearest PHC?"]
            },
            {
                "name": "ask_commodity_price",
                "description": "Get current commodity prices",
                "examples": ["What is wheat price today?", "Current rice prices in mandi"]
            },
            {
                "name": "ask_pincode_help",
                "description": "Get pincode information",
                "examples": ["Information about pincode 110001", "Which district is 560001?"]
            },
            {
                "name": "general_faq",
                "description": "General questions and FAQ",
                "examples": ["How to apply for ration card?", "What documents needed for Aadhaar?"]
            }
        ]
    }
