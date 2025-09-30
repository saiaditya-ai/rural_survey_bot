from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Import routers
from routers import chat, survey, health
from services.database import init_db
from services.mock_data import initialize_mock_data

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rural_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    logger.info("Starting Rural Survey Bot...")
    
    # Initialize database
    await init_db()
    
    # Initialize mock data
    await initialize_mock_data()
    
    logger.info("Rural Survey Bot started successfully!")
    yield
    
    logger.info("Shutting down Rural Survey Bot...")

app = FastAPI(
    title="Rural Survey & FAQ Bot",
    description="AI-powered chatbot for rural surveys and government service information",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(survey.router, prefix="/api/v1/survey", tags=["Survey"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Rural Survey & FAQ Bot API is running!",
        "version": "2.0.0",
        "status": "healthy",
        "features": [
            "Multi-language support (English, Hindi, Regional)",
            "Government scheme information",
            "Health facility locator",
            "Agricultural commodity prices",
            "Political representative information",
            "Survey collection with sentiment analysis",
            "Fallback to mock data when APIs unavailable"
        ]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": "2025-09-30T14:12:20+05:30",
        "services": {
            "database": "connected",
            "mock_data": "loaded",
            "apis": "available"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )
