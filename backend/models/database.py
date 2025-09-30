from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Survey(Base):
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_pincode = Column(String(6), nullable=False, index=True)
    village_name = Column(String(100))
    district_name = Column(String(100), index=True)
    state_name = Column(String(100), index=True)
    
    # Representative information
    mla_name = Column(String(200))
    mp_name = Column(String(200))
    
    # Opinion text and sentiment
    mla_opinion_text = Column(Text)
    mla_opinion_sentiment = Column(String(20))  # positive, negative, neutral
    mla_sentiment_score = Column(Float)
    
    mp_opinion_text = Column(Text)
    mp_opinion_sentiment = Column(String(20))  # positive, negative, neutral
    mp_sentiment_score = Column(Float)
    
    # Satisfaction rating
    satisfaction_score = Column(Integer)  # 1-10 scale
    
    # Metadata
    preferred_language = Column(String(20), default="english")
    channel = Column(String(20), default="web")  # web, sms, voice, whatsapp
    consent = Column(Boolean, default=True)
    
    # Location data
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Timestamps
    timestamp = Column(DateTime, default=func.now(), index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, index=True)
    question_type = Column(String(50))  # mla_name, mp_name, opinion_mla, etc.
    response_text = Column(Text)
    sentiment = Column(String(20))
    sentiment_score = Column(Float)
    language = Column(String(20))
    timestamp = Column(DateTime, default=func.now())

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(100), index=True)
    language = Column(String(20), default="english")
    channel = Column(String(20), default="web")
    
    # Location context
    pincode = Column(String(6))
    district = Column(String(100))
    state = Column(String(100))
    
    # Session metadata
    total_messages = Column(Integer, default=0)
    session_start = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    message_type = Column(String(20))  # user, bot
    content = Column(Text, nullable=False)
    intent = Column(String(50))
    confidence = Column(Float)
    data_source = Column(String(20))  # api, scraping, mock, fallback
    language = Column(String(20))
    
    # Response metadata
    response_time_ms = Column(Float)
    tokens_used = Column(Integer)
    
    timestamp = Column(DateTime, default=func.now(), index=True)

class APIUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    api_name = Column(String(50), index=True)  # data_gov, agmarknet, etc.
    endpoint = Column(String(200))
    method = Column(String(10))
    status_code = Column(Integer)
    response_time_ms = Column(Float)
    success = Column(Boolean)
    error_message = Column(Text)
    
    # Request metadata
    request_params = Column(JSON)
    user_agent = Column(String(200))
    ip_address = Column(String(45))
    
    timestamp = Column(DateTime, default=func.now(), index=True)

class ScrapingLog(Base):
    __tablename__ = "scraping_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    target_site = Column(String(100), index=True)  # pmay, agmarknet, etc.
    url = Column(String(500))
    scraping_type = Column(String(50))  # scheme_info, commodity_price, etc.
    success = Column(Boolean)
    data_extracted = Column(Boolean)
    error_message = Column(Text)
    
    # Performance metrics
    page_load_time_ms = Column(Float)
    extraction_time_ms = Column(Float)
    total_time_ms = Column(Float)
    
    # Metadata
    user_agent = Column(String(200))
    browser_version = Column(String(50))
    
    timestamp = Column(DateTime, default=func.now(), index=True)

class CacheEntry(Base):
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(200), unique=True, index=True)
    cache_type = Column(String(50), index=True)  # api_response, scraping_result, etc.
    data = Column(JSON, nullable=False)
    
    # Cache metadata
    ttl_seconds = Column(Integer)
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=func.now())
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, index=True)

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), index=True)
    metric_value = Column(Float)
    metric_unit = Column(String(20))
    
    # Metadata
    component = Column(String(50))  # api, scraping, database, etc.
    environment = Column(String(20))  # development, production
    
    timestamp = Column(DateTime, default=func.now(), index=True)

class ErrorLog(Base):
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(100), index=True)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    
    # Context information
    component = Column(String(50))  # router, service, scraper, etc.
    function_name = Column(String(100))
    request_id = Column(String(100))
    user_id = Column(String(100))
    session_id = Column(String(100))
    
    # Request context
    request_url = Column(String(500))
    request_method = Column(String(10))
    request_params = Column(JSON)
    
    # Environment
    environment = Column(String(20))
    server_instance = Column(String(50))
    
    timestamp = Column(DateTime, default=func.now(), index=True)

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    message_id = Column(Integer)
    
    # Feedback details
    feedback_type = Column(String(20))  # helpful, not_helpful, incorrect, etc.
    rating = Column(Integer)  # 1-5 scale
    comment = Column(Text)
    
    # Context
    intent = Column(String(50))
    data_source = Column(String(20))
    language = Column(String(20))
    
    timestamp = Column(DateTime, default=func.now(), index=True)

class DataQuality(Base):
    __tablename__ = "data_quality"
    
    id = Column(Integer, primary_key=True, index=True)
    data_source = Column(String(50), index=True)  # api, scraping, mock
    data_type = Column(String(50), index=True)  # scheme_info, health_facility, etc.
    
    # Quality metrics
    completeness_score = Column(Float)  # 0-1
    accuracy_score = Column(Float)  # 0-1
    freshness_score = Column(Float)  # 0-1
    consistency_score = Column(Float)  # 0-1
    
    # Validation results
    total_records = Column(Integer)
    valid_records = Column(Integer)
    invalid_records = Column(Integer)
    missing_fields = Column(JSON)
    
    # Metadata
    validation_rules = Column(JSON)
    last_validation = Column(DateTime, default=func.now())
    
    timestamp = Column(DateTime, default=func.now(), index=True)
