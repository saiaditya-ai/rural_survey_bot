import asyncio
import pytest
import json
from datetime import datetime
from typing import Dict, Any

# Test all major components
class TestRuralBot:
    """Comprehensive test suite for Rural Survey Bot"""
    
    @pytest.fixture
    async def setup_services(self):
        """Setup all services for testing"""
        from services.intent_detector import IntentDetector
        from services.api_client import APIClient
        from services.mock_data import MockDataService
        from services.sentiment_analyzer import SentimentAnalyzer
        from services.response_generator import ResponseGenerator
        
        return {
            "intent_detector": IntentDetector(),
            "api_client": APIClient(),
            "mock_data": MockDataService(),
            "sentiment_analyzer": SentimentAnalyzer(),
            "response_generator": ResponseGenerator()
        }
    
    async def test_intent_detection(self, setup_services):
        """Test intent detection for all supported intents"""
        services = await setup_services
        intent_detector = services["intent_detector"]
        
        test_cases = [
            ("Who is my MLA?", "survey_mla_name"),
            ("Tell me about PMAY scheme", "ask_scheme_info"),
            ("Find hospitals near me", "ask_phc_location"),
            ("What is wheat price today?", "ask_commodity_price"),
            ("Information about pincode 110001", "ask_pincode_help"),
            ("How to apply for ration card?", "general_faq")
        ]
        
        for question, expected_intent in test_cases:
            intent = await intent_detector.detect_intent(question)
            assert intent.name == expected_intent
            assert intent.confidence > 0.0
    
    async def test_sentiment_analysis(self, setup_services):
        """Test sentiment analysis"""
        services = await setup_services
        sentiment_analyzer = services["sentiment_analyzer"]
        
        test_cases = [
            ("The MLA is doing excellent work", "positive"),
            ("Very disappointed with the service", "negative"),
            ("The work is okay", "neutral")
        ]
        
        for text, expected_sentiment in test_cases:
            sentiment = await sentiment_analyzer.analyze_sentiment(text)
            assert sentiment.label.value == expected_sentiment
    
    async def test_mock_data_service(self, setup_services):
        """Test mock data service"""
        services = await setup_services
        mock_data = services["mock_data"]
        
        # Test health facilities
        facilities = await mock_data.get_health_facilities({"pincode": "110001"})
        assert len(facilities) > 0
        assert facilities[0].name is not None
        
        # Test commodity prices
        prices = await mock_data.get_commodity_prices("wheat", {"state": "Delhi"})
        assert len(prices) > 0
        assert prices[0].commodity == "wheat"
    
    async def test_api_integration(self, setup_services):
        """Test API integration (basic connectivity)"""
        services = await setup_services
        api_client = services["api_client"]
        
        # Test health check
        health = await api_client.health_check()
        assert "status" in health
        
        # Test pincode API
        pincode_info = await api_client.get_pincode_info("110001")
        # Should return data or None (acceptable for testing)
        assert pincode_info is None or hasattr(pincode_info, 'pincode')
    
    async def test_response_generation(self, setup_services):
        """Test response generation"""
        services = await setup_services
        response_gen = services["response_generator"]
        
        from models.schemas import Intent
        
        # Test scheme info response
        intent = Intent(name="ask_scheme_info", confidence=0.8, entities={})
        data = {
            "type": "scheme_info",
            "data": {
                "scheme_name": "PMAY",
                "description": "Housing scheme",
                "benefits": ["Financial assistance", "Technical support"],
                "eligibility": ["EWS", "LIG"]
            },
            "source": "mock"
        }
        
        response = await response_gen.generate_response(intent, data)
        assert "message" in response
        assert len(response["message"]) > 0
        assert response["source"] == "mock"

# Run specific tests
async def run_tests():
    """Run all tests"""
    test_instance = TestRuralBot()
    
    print("🧪 Running Comprehensive Tests...")
    
    try:
        # Setup services
        services = await test_instance.setup_services()
        print("✅ Services initialized")
        
        # Test intent detection
        await test_instance.test_intent_detection(services)
        print("✅ Intent detection tests passed")
        
        # Test sentiment analysis
        await test_instance.test_sentiment_analysis(services)
        print("✅ Sentiment analysis tests passed")
        
        # Test mock data
        await test_instance.test_mock_data_service(services)
        print("✅ Mock data service tests passed")
        
        # Test API integration
        await test_instance.test_api_integration(services)
        print("✅ API integration tests passed")
        
        # Test response generation
        await test_instance.test_response_generation(services)
        print("✅ Response generation tests passed")
        
        print("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(run_tests())
