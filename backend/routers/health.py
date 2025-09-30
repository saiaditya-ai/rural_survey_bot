from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/status")
async def health_status():
    """
    Get detailed health status of all services
    """
    try:
        from services.api_client import APIClient
        from services.web_scraper import WebScraper
        from services.database import check_db_connection
        from services.mock_data import MockDataService
        
        api_client = APIClient()
        web_scraper = WebScraper()
        mock_data_service = MockDataService()
        
        # Check database connection
        db_status = await check_db_connection()
        
        # Check API services
        api_status = await api_client.health_check()
        
        # Check web scraping capability
        scraper_status = await web_scraper.health_check()
        
        # Check mock data availability
        mock_status = await mock_data_service.health_check()
        
        overall_status = "healthy" if all([
            db_status["status"] == "healthy",
            api_status["status"] == "healthy" or api_status["status"] == "degraded",
            scraper_status["status"] == "healthy",
            mock_status["status"] == "healthy"
        ]) else "unhealthy"
        
        return {
            "overall_status": overall_status,
            "timestamp": "2025-09-30T14:12:20+05:30",
            "services": {
                "database": db_status,
                "api_client": api_status,
                "web_scraper": scraper_status,
                "mock_data": mock_status
            },
            "features": {
                "multi_language_support": True,
                "sentiment_analysis": True,
                "intent_detection": True,
                "fallback_system": True,
                "web_scraping": True,
                "api_integration": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking health status: {str(e)}")
        return {
            "overall_status": "unhealthy",
            "timestamp": "2025-09-30T14:12:20+05:30",
            "error": str(e),
            "services": {
                "database": {"status": "unknown"},
                "api_client": {"status": "unknown"},
                "web_scraper": {"status": "unknown"},
                "mock_data": {"status": "unknown"}
            }
        }

@router.get("/metrics")
async def get_metrics():
    """
    Get system metrics and performance data
    """
    try:
        import psutil
        import os
        from datetime import datetime, timedelta
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application metrics (you would implement these based on your needs)
        metrics = {
            "system": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "application": {
                "uptime_seconds": 0,  # You would track this
                "total_requests": 0,  # You would track this
                "successful_requests": 0,  # You would track this
                "failed_requests": 0,  # You would track this
                "average_response_time_ms": 0,  # You would track this
                "active_connections": 0  # You would track this
            },
            "services": {
                "api_calls_successful": 0,  # You would track this
                "api_calls_failed": 0,  # You would track this
                "scraping_operations_successful": 0,  # You would track this
                "scraping_operations_failed": 0,  # You would track this
                "mock_data_requests": 0,  # You would track this
                "database_queries": 0  # You would track this
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/test-apis")
async def test_api_endpoints():
    """
    Test all external API endpoints
    """
    try:
        from services.api_client import APIClient
        
        api_client = APIClient()
        
        test_results = {
            "data_gov_api": await api_client.test_data_gov_api(),
            "health_facility_api": await api_client.test_health_facility_api(),
            "pincode_api": await api_client.test_pincode_api(),
            "agmarknet_api": await api_client.test_agmarknet_api(),
            "timestamp": "2025-09-30T14:12:20+05:30"
        }
        
        # Calculate overall API health
        successful_tests = sum(1 for result in test_results.values() 
                             if isinstance(result, dict) and result.get("status") == "success")
        total_tests = len([k for k in test_results.keys() if k != "timestamp"])
        
        test_results["overall_api_health"] = "healthy" if successful_tests == total_tests else "degraded"
        test_results["success_rate"] = f"{successful_tests}/{total_tests}"
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error testing API endpoints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test API endpoints: {str(e)}")

@router.get("/test-scraping")
async def test_web_scraping():
    """
    Test web scraping functionality
    """
    try:
        from services.web_scraper import WebScraper
        
        web_scraper = WebScraper()
        
        test_results = {
            "pmay_scraping": await web_scraper.test_pmay_scraping(),
            "agmarknet_scraping": await web_scraper.test_agmarknet_scraping(),
            "health_facility_scraping": await web_scraper.test_health_facility_scraping(),
            "political_info_scraping": await web_scraper.test_political_info_scraping(),
            "timestamp": "2025-09-30T14:12:20+05:30"
        }
        
        # Calculate overall scraping health
        successful_tests = sum(1 for result in test_results.values() 
                             if isinstance(result, dict) and result.get("status") == "success")
        total_tests = len([k for k in test_results.keys() if k != "timestamp"])
        
        test_results["overall_scraping_health"] = "healthy" if successful_tests == total_tests else "degraded"
        test_results["success_rate"] = f"{successful_tests}/{total_tests}"
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error testing web scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test web scraping: {str(e)}")

@router.get("/test-database")
async def test_database():
    """
    Test database connectivity and operations
    """
    try:
        from services.database import get_db_session, test_database_operations
        
        test_results = await test_database_operations()
        
        return {
            "database_tests": test_results,
            "timestamp": "2025-09-30T14:12:20+05:30"
        }
        
    except Exception as e:
        logger.error(f"Error testing database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test database: {str(e)}")

@router.get("/logs")
async def get_recent_logs(lines: int = 100):
    """
    Get recent application logs
    """
    try:
        import os
        
        log_file = "rural_bot.log"
        
        if not os.path.exists(log_file):
            return {"logs": [], "message": "Log file not found"}
        
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "logs": [line.strip() for line in recent_lines],
            "total_lines": len(recent_lines),
            "timestamp": "2025-09-30T14:12:20+05:30"
        }
        
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@router.post("/clear-cache")
async def clear_cache():
    """
    Clear application cache
    """
    try:
        from services.cache_manager import CacheManager
        
        cache_manager = CacheManager()
        cleared_items = await cache_manager.clear_all()
        
        return {
            "message": "Cache cleared successfully",
            "cleared_items": cleared_items,
            "timestamp": "2025-09-30T14:12:20+05:30"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/configuration")
async def get_configuration():
    """
    Get current application configuration (sanitized)
    """
    try:
        import os
        
        config = {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug": os.getenv("DEBUG", "True"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "port": os.getenv("PORT", "8000"),
            "default_language": os.getenv("DEFAULT_LANGUAGE", "english"),
            "supported_languages": os.getenv("SUPPORTED_LANGUAGES", "english,hindi,telugu").split(","),
            "use_mock_data": os.getenv("USE_MOCK_DATA", "True"),
            "selenium_headless": os.getenv("SELENIUM_HEADLESS", "True"),
            "selenium_timeout": os.getenv("SELENIUM_TIMEOUT", "30"),
            "cache_ttl": os.getenv("CACHE_TTL", "3600"),
            "api_rate_limit": os.getenv("API_RATE_LIMIT", "100"),
            "scraping_delay": os.getenv("SCRAPING_DELAY", "2"),
            # Don't include sensitive information like API keys
            "api_keys_configured": {
                "data_gov": bool(os.getenv("DATA_GOV_API_KEY")),
                "huggingface": bool(os.getenv("HUGGINGFACE_API_KEY")),
                "google_maps": bool(os.getenv("GOOGLE_MAPS_API_KEY")),
                "openai": bool(os.getenv("OPENAI_API_KEY"))
            }
        }
        
        return {
            "configuration": config,
            "timestamp": "2025-09-30T14:12:20+05:30"
        }
        
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")
