#!/usr/bin/env python3
"""
Rural Survey & FAQ Bot - Startup Script
This script initializes and starts the complete backend system
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rural_bot_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def check_environment():
    """Check if environment is properly configured"""
    logger.info("🔍 Checking environment configuration...")
    
    # Check if .env file exists
    env_file = backend_dir / '.env'
    if not env_file.exists():
        logger.warning("⚠️  .env file not found. Creating from .env.example...")
        env_example = backend_dir / '.env.example'
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            logger.info("✅ Created .env file from template")
        else:
            logger.error("❌ .env.example file not found!")
            return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check critical environment variables
    required_vars = ['DATABASE_URL', 'PORT']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️  Missing environment variables: {missing_vars}")
        logger.info("💡 Using default values for missing variables")
    
    logger.info("✅ Environment configuration checked")
    return True

async def initialize_services():
    """Initialize all services"""
    logger.info("🚀 Initializing services...")
    
    try:
        # Initialize database
        from services.database import init_db
        await init_db()
        logger.info("✅ Database initialized")
        
        # Initialize mock data
        from services.mock_data import initialize_mock_data
        await initialize_mock_data()
        logger.info("✅ Mock data service initialized")
        
        # Test service health
        from services.api_client import APIClient
        from services.web_scraper import WebScraper
        from services.intent_detector import IntentDetector
        from services.sentiment_analyzer import SentimentAnalyzer
        
        # Quick health checks
        api_client = APIClient()
        async with api_client:
            api_health = await api_client.health_check()
            logger.info(f"📡 API Client Status: {api_health.get('status', 'unknown')}")
        
        web_scraper = WebScraper()
        scraper_health = await web_scraper.health_check()
        logger.info(f"🕷️  Web Scraper Status: {scraper_health.get('status', 'unknown')}")
        
        intent_detector = IntentDetector()
        logger.info("🧠 Intent Detector: Ready")
        
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_health = await sentiment_analyzer.health_check()
        logger.info(f"😊 Sentiment Analyzer Status: {sentiment_health.get('status', 'unknown')}")
        
        logger.info("✅ All services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {str(e)}")
        return False

async def run_tests():
    """Run basic system tests"""
    logger.info("🧪 Running system tests...")
    
    try:
        from test_comprehensive import run_tests as run_comprehensive_tests
        await run_comprehensive_tests()
        logger.info("✅ All tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tests failed: {str(e)}")
        return False

def start_server():
    """Start the FastAPI server"""
    logger.info("🌐 Starting FastAPI server...")
    
    try:
        import uvicorn
        from app import app
        
        port = int(os.getenv('PORT', 8000))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"🚀 Server starting on http://{host}:{port}")
        logger.info("📖 API Documentation available at http://localhost:8000/docs")
        logger.info("🔍 Health check available at http://localhost:8000/health")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=os.getenv('DEBUG', 'False').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'info').lower()
        )
        
    except Exception as e:
        logger.error(f"❌ Server startup failed: {str(e)}")
        sys.exit(1)

async def main():
    """Main startup function"""
    print("🌾 Rural Survey & FAQ Bot - Starting Up...")
    print("=" * 50)
    
    # Check environment
    if not await check_environment():
        logger.error("❌ Environment check failed")
        sys.exit(1)
    
    # Initialize services
    if not await initialize_services():
        logger.error("❌ Service initialization failed")
        sys.exit(1)
    
    # Run tests (optional, can be skipped in production)
    run_tests_flag = os.getenv('RUN_TESTS', 'True').lower() == 'true'
    if run_tests_flag:
        if not await run_tests():
            logger.warning("⚠️  Some tests failed, but continuing with startup")
    else:
        logger.info("⏭️  Skipping tests (RUN_TESTS=False)")
    
    print("\n🎉 Initialization Complete!")
    print("=" * 50)
    print("🌟 Rural Survey & FAQ Bot Features:")
    print("   • Multi-language support (English, Hindi, Telugu)")
    print("   • Government scheme information")
    print("   • Health facility locator")
    print("   • Agricultural commodity prices")
    print("   • Political representative information")
    print("   • Survey collection with sentiment analysis")
    print("   • Fallback to mock data when APIs unavailable")
    print("=" * 50)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
        print("\n👋 Rural Survey & FAQ Bot stopped")
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        sys.exit(1)
