from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from services.database import get_db_session
from services.sentiment_analyzer import SentimentAnalyzer
from models.schemas import SurveyRequest, SurveyResponse, SurveySubmission, SurveyStats
from models.database import Survey, SurveyResponse as DBSurveyResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
sentiment_analyzer = SentimentAnalyzer()

@router.post("/submit", response_model=SurveyResponse)
async def submit_survey(survey: SurveySubmission, db_session=Depends(get_db_session)):
    """
    Submit a completed survey with MLA/MP opinions
    """
    try:
        logger.info(f"Receiving survey submission for pincode: {survey.user_pincode}")
        
        # Analyze sentiment of opinions
        mla_sentiment = None
        mp_sentiment = None
        
        if survey.mla_opinion_text:
            mla_sentiment = await sentiment_analyzer.analyze_sentiment(
                survey.mla_opinion_text, 
                survey.preferred_language
            )
        
        if survey.mp_opinion_text:
            mp_sentiment = await sentiment_analyzer.analyze_sentiment(
                survey.mp_opinion_text,
                survey.preferred_language
            )
        
        # Create survey record
        survey_record = Survey(
            user_pincode=survey.user_pincode,
            village_name=survey.village_name,
            district_name=survey.district_name,
            state_name=survey.state_name,
            mla_name=survey.mla_name,
            mp_name=survey.mp_name,
            mla_opinion_text=survey.mla_opinion_text,
            mla_opinion_sentiment=mla_sentiment.label if mla_sentiment else None,
            mla_sentiment_score=mla_sentiment.score if mla_sentiment else None,
            mp_opinion_text=survey.mp_opinion_text,
            mp_opinion_sentiment=mp_sentiment.label if mp_sentiment else None,
            mp_sentiment_score=mp_sentiment.score if mp_sentiment else None,
            satisfaction_score=survey.satisfaction_score,
            preferred_language=survey.preferred_language,
            channel=survey.channel,
            consent=survey.consent,
            latitude=survey.latitude,
            longitude=survey.longitude,
            timestamp=datetime.utcnow()
        )
        
        # Save to database
        db_session.add(survey_record)
        await db_session.commit()
        await db_session.refresh(survey_record)
        
        logger.info(f"Survey submitted successfully with ID: {survey_record.id}")
        
        # Generate response message based on language
        response_message = generate_survey_response_message(
            survey.preferred_language,
            survey.mla_name,
            survey.mp_name,
            mla_sentiment,
            mp_sentiment
        )
        
        return SurveyResponse(
            success=True,
            message=response_message,
            survey_id=str(survey_record.id),
            mla_sentiment=mla_sentiment.label if mla_sentiment else None,
            mp_sentiment=mp_sentiment.label if mp_sentiment else None,
            language=survey.preferred_language,
            next_steps=[
                "Your feedback has been recorded",
                "You can now ask questions about government services",
                "Type 'help' to see what I can assist you with"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error submitting survey: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit survey: {str(e)}")

@router.get("/stats", response_model=SurveyStats)
async def get_survey_stats(
    district: Optional[str] = None,
    state: Optional[str] = None,
    db_session=Depends(get_db_session)
):
    """
    Get survey statistics and analytics
    """
    try:
        # Build query
        query = db_session.query(Survey)
        
        if district:
            query = query.filter(Survey.district_name.ilike(f"%{district}%"))
        if state:
            query = query.filter(Survey.state_name.ilike(f"%{state}%"))
        
        surveys = await query.all()
        
        # Calculate statistics
        total_surveys = len(surveys)
        
        # Sentiment distribution
        mla_sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        mp_sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        
        satisfaction_scores = []
        languages = {}
        channels = {}
        
        for survey in surveys:
            # MLA sentiment
            if survey.mla_opinion_sentiment:
                mla_sentiments[survey.mla_opinion_sentiment] += 1
            
            # MP sentiment
            if survey.mp_opinion_sentiment:
                mp_sentiments[survey.mp_opinion_sentiment] += 1
            
            # Satisfaction scores
            if survey.satisfaction_score:
                satisfaction_scores.append(survey.satisfaction_score)
            
            # Languages
            if survey.preferred_language:
                languages[survey.preferred_language] = languages.get(survey.preferred_language, 0) + 1
            
            # Channels
            if survey.channel:
                channels[survey.channel] = channels.get(survey.channel, 0) + 1
        
        # Calculate averages
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        return SurveyStats(
            total_surveys=total_surveys,
            mla_sentiment_distribution=mla_sentiments,
            mp_sentiment_distribution=mp_sentiments,
            average_satisfaction_score=round(avg_satisfaction, 2),
            language_distribution=languages,
            channel_distribution=channels,
            district_filter=district,
            state_filter=state
        )
        
    except Exception as e:
        logger.error(f"Error getting survey stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get survey stats: {str(e)}")

@router.get("/recent")
async def get_recent_surveys(
    limit: int = 10,
    district: Optional[str] = None,
    db_session=Depends(get_db_session)
):
    """
    Get recent survey submissions (anonymized)
    """
    try:
        query = db_session.query(Survey).order_by(Survey.timestamp.desc())
        
        if district:
            query = query.filter(Survey.district_name.ilike(f"%{district}%"))
        
        surveys = await query.limit(limit).all()
        
        # Anonymize data
        recent_surveys = []
        for survey in surveys:
            recent_surveys.append({
                "id": str(survey.id),
                "district": survey.district_name,
                "state": survey.state_name,
                "mla_sentiment": survey.mla_opinion_sentiment,
                "mp_sentiment": survey.mp_opinion_sentiment,
                "satisfaction_score": survey.satisfaction_score,
                "language": survey.preferred_language,
                "channel": survey.channel,
                "timestamp": survey.timestamp.isoformat(),
                # Don't include personal information or actual opinions
            })
        
        return {"recent_surveys": recent_surveys}
        
    except Exception as e:
        logger.error(f"Error getting recent surveys: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent surveys: {str(e)}")

@router.post("/start")
async def start_survey(request: Dict[str, Any]):
    """
    Start a new survey session
    """
    try:
        language = request.get("language", "english")
        channel = request.get("channel", "web")
        
        # Generate survey introduction based on language
        intro_message = generate_survey_intro(language)
        
        return {
            "message": intro_message,
            "language": language,
            "channel": channel,
            "steps": [
                {
                    "step": 1,
                    "question": get_localized_question("mla_name", language),
                    "type": "text",
                    "required": True
                },
                {
                    "step": 2,
                    "question": get_localized_question("mp_name", language),
                    "type": "text",
                    "required": True
                },
                {
                    "step": 3,
                    "question": get_localized_question("mla_opinion", language),
                    "type": "text",
                    "required": False
                },
                {
                    "step": 4,
                    "question": get_localized_question("mp_opinion", language),
                    "type": "text",
                    "required": False
                },
                {
                    "step": 5,
                    "question": get_localized_question("satisfaction", language),
                    "type": "rating",
                    "scale": "1-10",
                    "required": True
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error starting survey: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start survey: {str(e)}")

def generate_survey_intro(language: str) -> str:
    """Generate survey introduction message"""
    intros = {
        "english": "Namaste! I would like to conduct a short survey about your local representatives. This will help improve government services. Your responses are confidential. Would you like to participate?",
        "hindi": "नमस्ते! मैं आपके स्थानीय प्रतिनिधियों के बारे में एक छोटा सर्वेक्षण करना चाहूंगा। इससे सरकारी सेवाओं में सुधार होगा। आपके उत्तर गोपनीय हैं। क्या आप भाग लेना चाहेंगे?",
        "telugu": "నమస్కారం! మీ స్థానిక ప్రతినిధుల గురించి ఒక చిన్న సర్వే చేయాలని అనుకుంటున్నాను. ఇది ప్రభుత్వ సేవలను మెరుగుపరచడంలో సహాయపడుతుంది. మీ సమాధానాలు గోప్యంగా ఉంటాయి. మీరు పాల్గొనాలని అనుకుంటున్నారా?"
    }
    return intros.get(language, intros["english"])

def get_localized_question(question_type: str, language: str) -> str:
    """Get localized survey questions"""
    questions = {
        "english": {
            "mla_name": "What is the name of your MLA (Member of Legislative Assembly)?",
            "mp_name": "What is the name of your MP (Member of Parliament)?",
            "mla_opinion": "Please share your opinion about your MLA's work (optional):",
            "mp_opinion": "Please share your opinion about your MP's work (optional):",
            "satisfaction": "On a scale of 1-10, how satisfied are you with your local representatives?"
        },
        "hindi": {
            "mla_name": "आपके विधायक (MLA) का नाम क्या है?",
            "mp_name": "आपके सांसद (MP) का नाम क्या है?",
            "mla_opinion": "कृपया अपने विधायक के काम के बारे में अपनी राय साझा करें (वैकल्पिक):",
            "mp_opinion": "कृपया अपने सांसद के काम के बारे में अपनी राय साझा करें (वैकल्पिक):",
            "satisfaction": "1-10 के पैमाने पर, आप अपने स्थानीय प्रतिनिधियों से कितने संतुष्ट हैं?"
        },
        "telugu": {
            "mla_name": "మీ MLA (శాసనసభ సభ్యుడు) పేరు ఏమిటి?",
            "mp_name": "మీ MP (పార్లమెంట్ సభ్యుడు) పేరు ఏమిటి?",
            "mla_opinion": "దయచేసి మీ MLA పని గురించి మీ అభిప్రాయం పంచుకోండి (ఐచ్ఛికం):",
            "mp_opinion": "దయచేసి మీ MP పని గురించి మీ అభిప్రాయం పంచుకోండి (ఐచ్ఛికం):",
            "satisfaction": "1-10 స్కేల్‌లో, మీ స్థానిక ప్రతినిధులతో మీరు ఎంత సంతృప్తిగా ఉన్నారు?"
        }
    }
    return questions.get(language, questions["english"]).get(question_type, "")

def generate_survey_response_message(
    language: str,
    mla_name: str,
    mp_name: str,
    mla_sentiment,
    mp_sentiment
) -> str:
    """Generate response message after survey submission"""
    messages = {
        "english": f"Thank you for participating in the survey! Your feedback about {mla_name} (MLA) and {mp_name} (MP) has been recorded. This information will help improve government services in your area.",
        "hindi": f"सर्वेक्षण में भाग लेने के लिए धन्यवाद! {mla_name} (विधायक) और {mp_name} (सांसद) के बारे में आपकी प्रतिक्रिया दर्ज की गई है। यह जानकारी आपके क्षेत्र में सरकारी सेवाओं को बेहतर बनाने में मदद करेगी।",
        "telugu": f"సర్వేలో పాల్గొన్నందుకు ధన్యవాదాలు! {mla_name} (MLA) మరియు {mp_name} (MP) గురించి మీ అభిప్రాయం నమోదు చేయబడింది. ఈ సమాచారం మీ ప్రాంతంలో ప్రభుత్వ సేవలను మెరుగుపరచడంలో సహాయపడుతుంది."
    }
    return messages.get(language, messages["english"])

@router.get("/export")
async def export_survey_data(
    format: str = "json",
    district: Optional[str] = None,
    state: Optional[str] = None,
    db_session=Depends(get_db_session)
):
    """
    Export survey data for analysis (anonymized)
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
        
        query = db_session.query(Survey)
        
        if district:
            query = query.filter(Survey.district_name.ilike(f"%{district}%"))
        if state:
            query = query.filter(Survey.state_name.ilike(f"%{state}%"))
        
        surveys = await query.all()
        
        # Anonymize and export data
        export_data = []
        for survey in surveys:
            export_data.append({
                "survey_id": str(survey.id),
                "pincode": survey.user_pincode,
                "district": survey.district_name,
                "state": survey.state_name,
                "mla_sentiment": survey.mla_opinion_sentiment,
                "mla_sentiment_score": survey.mla_sentiment_score,
                "mp_sentiment": survey.mp_opinion_sentiment,
                "mp_sentiment_score": survey.mp_sentiment_score,
                "satisfaction_score": survey.satisfaction_score,
                "language": survey.preferred_language,
                "channel": survey.channel,
                "timestamp": survey.timestamp.isoformat(),
                # Exclude personal information and actual text opinions
            })
        
        if format == "json":
            return {"data": export_data, "total_records": len(export_data)}
        else:
            # For CSV, you would implement CSV conversion here
            return {"message": "CSV export not implemented yet", "data": export_data}
        
    except Exception as e:
        logger.error(f"Error exporting survey data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export survey data: {str(e)}")
