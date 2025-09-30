from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class Language(str, Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    TELUGU = "telugu"

class Channel(str, Enum):
    WEB = "web"
    SMS = "sms"
    VOICE = "voice"
    WHATSAPP = "whatsapp"

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Intent(BaseModel):
    name: str
    confidence: float
    entities: Dict[str, Any] = {}

class Sentiment(BaseModel):
    label: SentimentLabel
    score: float
    confidence: float

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    language: Language = Language.ENGLISH
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    data_source: str  # "api", "scraping", "mock", "fallback"
    language: Language
    suggestions: List[str] = []
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SurveyRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    language: Language = Language.ENGLISH
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class SurveySubmission(BaseModel):
    user_pincode: str = Field(..., pattern=r'^\d{6}$')
    village_name: Optional[str] = None
    district_name: Optional[str] = None
    state_name: Optional[str] = None
    mla_name: Optional[str] = None
    mp_name: Optional[str] = None
    mla_opinion_text: Optional[str] = Field(None, max_length=2000)
    mp_opinion_text: Optional[str] = Field(None, max_length=2000)
    satisfaction_score: Optional[int] = Field(None, ge=1, le=10)
    preferred_language: Language = Language.ENGLISH
    channel: Channel = Channel.WEB
    consent: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @validator('user_pincode')
    def validate_pincode(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Pincode must be exactly 6 digits')
        return v

class SurveyResponse(BaseModel):
    success: bool
    message: str
    survey_id: Optional[str] = None
    mla_sentiment: Optional[SentimentLabel] = None
    mp_sentiment: Optional[SentimentLabel] = None
    language: Language
    next_steps: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SurveyStats(BaseModel):
    total_surveys: int
    mla_sentiment_distribution: Dict[str, int]
    mp_sentiment_distribution: Dict[str, int]
    average_satisfaction_score: float
    language_distribution: Dict[str, int]
    channel_distribution: Dict[str, int]
    district_filter: Optional[str] = None
    state_filter: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# API Response Models
class HealthFacility(BaseModel):
    name: str
    type: str  # PHC, CHC, Hospital, etc.
    address: str
    pincode: str
    district: str
    state: str
    phone: Optional[str] = None
    services: List[str] = []
    distance_km: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CommodityPrice(BaseModel):
    commodity: str
    variety: str
    market_name: str
    mandi_id: Optional[str] = None
    price_per_unit: float
    unit: str  # kg, quintal, etc.
    date: datetime
    district: str
    state: str
    source: str

class SchemeInfo(BaseModel):
    scheme_name: str
    description: str
    eligibility: List[str]
    benefits: List[str]
    application_process: List[str]
    required_documents: List[str]
    official_website: Optional[str] = None
    helpline: Optional[str] = None
    last_updated: datetime

class PoliticalRepresentative(BaseModel):
    name: str
    position: str  # MLA, MP
    constituency: str
    party: Optional[str] = None
    contact_info: Dict[str, str] = {}
    office_address: Optional[str] = None
    achievements: List[str] = []
    source: str

class PincodeInfo(BaseModel):
    pincode: str
    post_office: str
    district: str
    state: str
    region: str
    division: str
    circle: str
    taluk: Optional[str] = None
    villages: List[str] = []

# Mock Data Models
class MockHealthFacility(BaseModel):
    facilities: List[HealthFacility]
    disclaimer: str = "This is mock data for demonstration purposes"
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class MockCommodityPrices(BaseModel):
    prices: List[CommodityPrice]
    disclaimer: str = "This is mock data for demonstration purposes"
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class MockSchemeInfo(BaseModel):
    schemes: List[SchemeInfo]
    disclaimer: str = "This is mock data for demonstration purposes"
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class MockPincodeDirectory(BaseModel):
    pincodes: List[PincodeInfo]
    disclaimer: str = "This is mock data for demonstration purposes"
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Error Models
class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

# Health Check Models
class ServiceHealth(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: Optional[float] = None
    last_check: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = {}

class SystemHealth(BaseModel):
    overall_status: str
    services: Dict[str, ServiceHealth]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Configuration Models
class APIConfiguration(BaseModel):
    data_gov_api_enabled: bool
    huggingface_api_enabled: bool
    google_maps_api_enabled: bool
    openai_api_enabled: bool
    rate_limit_per_minute: int
    timeout_seconds: int

class ScrapingConfiguration(BaseModel):
    selenium_headless: bool
    timeout_seconds: int
    delay_between_requests: int
    max_retries: int
    user_agent: str

class MockDataConfiguration(BaseModel):
    use_mock_data: bool
    mock_probability: float
    fallback_to_mock: bool
    mock_data_refresh_hours: int

# Testing Models
class TestResult(BaseModel):
    test_name: str
    status: str  # "pass", "fail", "skip"
    execution_time_ms: float
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TestSuite(BaseModel):
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    execution_time_ms: float
    results: List[TestResult]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
