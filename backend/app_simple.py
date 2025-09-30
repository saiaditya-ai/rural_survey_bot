from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Rural Survey & FAQ Bot",
    description="AI-powered chatbot for rural surveys and government service information",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    language: str = "english"
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    data_source: str
    language: str
    suggestions: List[str] = []
    metadata: Dict[str, Any] = {}

@app.get("/")
async def root():
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
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "available",
            "mock_data": "loaded",
            "intent_detection": "ready"
        }
    }

@app.post("/api/v1/chat/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    try:
        logger.info(f"Received question: {request.question}")
        
        intent = detect_simple_intent(request.question)
        
        response_data = generate_simple_response(intent, request.question, request.language)
        
        return ChatResponse(
            response=response_data["message"],
            intent=intent,
            confidence=0.8,
            data_source="mock",
            language=request.language,
            suggestions=response_data.get("suggestions", []),
            metadata={"timestamp": datetime.now().isoformat()}
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return ChatResponse(
            response="I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            intent="fallback",
            confidence=0.0,
            data_source="error",
            language=request.language,
            suggestions=["Try asking about government schemes", "Ask for health facilities"],
            metadata={"error": str(e)}
        )

def detect_simple_intent(question: str) -> str:
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["mla", "विधायक", "member legislative"]):
        return "survey_mla_name"
    elif any(word in question_lower for word in ["mp", "सांसद", "member parliament"]):
        return "survey_mp_name"
    elif any(word in question_lower for word in ["scheme", "yojana", "योजना", "pmay", "housing"]):
        return "ask_scheme_info"
    elif any(word in question_lower for word in ["hospital", "health", "phc", "doctor", "अस्पताल"]):
        return "ask_phc_location"
    elif any(word in question_lower for word in ["price", "mandi", "wheat", "rice", "कीमत"]):
        return "ask_commodity_price"
    elif any(word in question_lower for word in ["pincode", "pin code", "पिन कोड"]):
        return "ask_pincode_help"
    else:
        return "general_faq"

def generate_simple_response(intent: str, question: str, language: str) -> Dict[str, Any]:
    responses = {
        "english": {
            "survey_mla_name": {
                "message": "To find your MLA information, I need your constituency or pincode. Your MLA represents your area in the state assembly and works on local issues like infrastructure, healthcare, and education.",
                "suggestions": ["Provide your pincode", "Tell me your district", "Ask about MP information"]
            },
            "survey_mp_name": {
                "message": "To find your MP information, I need your constituency or pincode. Your MP represents your area in Parliament and works on national policies and legislation.",
                "suggestions": ["Provide your pincode", "Tell me your constituency", "Ask about MLA information"]
            },
            "ask_scheme_info": {
                "message": "Here's information about government schemes:\n\n**PMAY (Pradhan Mantri Awas Yojana)**: Provides financial assistance for housing to EWS, LIG, and MIG families. Benefits include interest subsidy on home loans up to ₹2.67 lakh.\n\n**Eligibility**: First-time home buyers, families without pucca house\n**Documents**: Aadhaar, Income certificate, Bank details\n**Apply**: Visit pmayg.nic.in or nearest CSC",
                "suggestions": ["Check eligibility criteria", "Find application centers", "Ask about other schemes"]
            },
            "ask_phc_location": {
                "message": "To find health facilities near you, I need your location. Here are some general options:\n\n**Emergency**: Call 108 for ambulance\n**Primary Health Centers**: Available in most villages and towns\n**District Hospitals**: Available in each district\n**Government Hospitals**: Available in major cities\n\nFor specific locations, please provide your pincode or district name.",
                "suggestions": ["Provide your pincode", "Call 108 for emergency", "Ask about specific hospitals"]
            },
            "ask_commodity_price": {
                "message": "For current commodity prices, I recommend:\n\n**Agmarknet**: Visit agmarknet.gov.in for official mandi prices\n**Local Mandi**: Contact your nearest agricultural market\n**Kisan Call Center**: Call 1800-180-1551 for farming advice\n\nCommon commodities tracked: Wheat, Rice, Dal, Onion, Potato, Tomato, Sugar",
                "suggestions": ["Visit agmarknet.gov.in", "Call Kisan helpline", "Ask about specific commodity"]
            },
            "ask_pincode_help": {
                "message": "I can help you with pincode information. Please provide your 6-digit pincode, and I can tell you:\n\n• District and State\n• Post Office details\n• Region information\n• Nearby services\n\nExample: 110001 (New Delhi), 560001 (Bangalore), 400001 (Mumbai)",
                "suggestions": ["Provide your pincode", "Ask about district info", "Find local services"]
            },
            "general_faq": {
                "message": "I can help you with:\n\n**Government Schemes**: PMAY, Jan Aushadhi, Ayushman Bharat\n**Health Services**: Find hospitals, PHCs, emergency numbers\n**Agricultural Info**: Commodity prices, Kisan schemes\n**Representatives**: Find your MLA and MP\n**Documents**: Aadhaar, Ration card, Voter ID processes\n\nWhat specific information do you need?",
                "suggestions": ["Ask about specific scheme", "Find health facilities", "Get representative info"]
            }
        },
        "hindi": {
            "survey_mla_name": {
                "message": "आपके विधायक (MLA) की जानकारी के लिए मुझे आपका निर्वाचन क्षेत्र या पिन कोड चाहिए। विधायक स्थानीय मुद्दों जैसे सड़क, स्वास्थ्य और शिक्षा पर काम करते हैं।",
                "suggestions": ["अपना पिन कोड बताएं", "अपने जिले का नाम बताएं", "सांसद की जानकारी पूछें"]
            },
            "survey_mp_name": {
                "message": "आपके सांसद (MP) की जानकारी के लिए मुझे आपका निर्वाचन क्षेत्र या पिन कोड चाहिए। सांसद राष्ट्रीय नीतियों और कानूनों पर काम करते हैं।",
                "suggestions": ["अपना पिन कोड बताएं", "अपने क्षेत्र का नाम बताएं", "विधायक की जानकारी पूछें"]
            },
            "ask_scheme_info": {
                "message": "सरकारी योजनाओं की जानकारी:\n\n**PMAY (प्रधानमंत्री आवास योजना)**: आर्थिक रूप से कमजोर, निम्न और मध्यम आय वर्ग के परिवारों को घर बनाने के लिए सहायता। होम लोन पर ब्याज सब्सिडी उपलब्ध है।\n\n**पात्रता**: पहली बार घर खरीदने वाले परिवार जिनके पास पक्का घर नहीं है\n**दस्तावेज़**: आधार कार्ड, आय प्रमाण पत्र, बैंक विवरण\n**आवेदन**: pmayg.nic.in या निकटतम CSC केंद्र पर जाएं",
                "suggestions": ["पात्रता कैसे जांचें", "आवेदन कहाँ करें", "अन्य योजनाओं की जानकारी दें"]
            },
            "ask_phc_location": {
                "message": "आपके पास स्वास्थ्य सुविधाएँ खोजने के लिए मुझे आपका स्थान चाहिए। सामान्य जानकारी:\n\n**आपातकालीन सेवा**: 108 पर कॉल करें\n**प्राथमिक स्वास्थ्य केंद्र (PHC)**: प्रत्येक गाँव/कस्बे में उपलब्ध\n**जिला अस्पताल**: हर जिले में उपलब्ध\n**सरकारी अस्पताल**: बड़े शहरों में उपलब्ध\n\nकृपया अपने पिन कोड या जिले का नाम बताएं।",
                "suggestions": ["अपना पिन कोड बताएं", "108 पर कॉल करें", "विशेष अस्पताल पूछें"]
            },
            "ask_commodity_price": {
                "message": "वर्तमान मंडी दर जानने के लिए:\n\n**Agmarknet**: आधिकारिक मंडी दरों के लिए agmarknet.gov.in देखें\n**स्थानीय मंडी**: निकटतम कृषि बाजार से संपर्क करें\n**किसान कॉल सेंटर**: सलाह के लिए 1800-180-1551 पर कॉल करें\n\nसामान्य वस्तुएँ: गेहूँ, चावल, दाल, प्याज़, आलू, टमाटर, चीनी",
                "suggestions": ["agmarknet.gov.in देखें", "किसान हेल्पलाइन पर कॉल करें", "विशेष फसल की कीमत पूछें"]
            },
            "ask_pincode_help": {
                "message": "मैं पिन कोड जानकारी में मदद कर सकता हूँ। कृपया अपना 6 अंकों का पिन कोड बताएं। मैं जिला, राज्य, डाकघर और स्थानीय सेवाओं की जानकारी दे सकता हूँ।\n\nउदाहरण: 110001 (नई दिल्ली), 560001 (बेंगलुरु), 400001 (मुंबई)",
                "suggestions": ["अपना पिन कोड बताएं", "जिले की जानकारी पूछें", "स्थानीय सेवाएँ पूछें"]
            },
            "general_faq": {
                "message": "मैं निम्न विषयों में मदद कर सकता हूँ:\n\n**सरकारी योजनाएँ**: PMAY, जन औषधि, आयुष्मान भारत\n**स्वास्थ्य सेवाएँ**: अस्पताल, PHC, आपातकालीन नंबर\n**कृषि जानकारी**: मंडी दरें, किसान योजनाएँ\n**जन प्रतिनिधि**: विधायक और सांसद की जानकारी\n**दस्तावेज़**: आधार, राशन कार्ड, मतदाता पहचान पत्र प्रक्रिया\n\nकृपया बताएं कि आपको किस प्रकार की जानकारी चाहिए।",
                "suggestions": ["किसी योजना के बारे में पूछें", "स्वास्थ्य सुविधा पूछें", "प्रतिनिधि जानकारी पूछें"]
            }
        },
        "telugu": {
            "survey_mla_name": {
                "message": "మీ MLA వివరాలు తెలుసుకోవడానికి మీ నియోజకవర్గం లేదా పిన్ కోడ్ అవసరం. MLA స్థానిక మౌలిక వసతులు, ఆరోగ్యం, విద్య విషయాల్లో పని చేస్తారు.",
                "suggestions": ["మీ పిన్ కోడ్ చెప్పండి", "మీ జిల్లాను చెప్పండి", "MP వివరాలు అడగండి"]
            },
            "survey_mp_name": {
                "message": "మీ MP వివరాలు తెలుసుకోవడానికి మీ నియోజకవర్గం లేదా పిన్ కోడ్ అవసరం. MP పార్లమెంట్‌లో జాతీయ విధానాలు మరియు చట్టాలపై పని చేస్తారు.",
                "suggestions": ["మీ పిన్ కోడ్ చెప్పండి", "మీ నియోజకవర్గాన్ని చెప్పండి", "MLA వివరాలు అడగండి"]
            },
            "ask_scheme_info": {
                "message": "ప్రభుత్వ పథకాల సమాచారం:\n\n**PMAY (ప్రధాన్ మంత్రి ఆవాస్ యోజన)**: EWS, LIG, MIG కుటుంబాలకు గృహ నిర్మాణానికి సహాయం. హౌసింగ్ లోన్‌పై వడ్డీ సబ్సిడీ లభిస్తుంది.\n\n**అర్హత**: మొదటిసారి ఇల్లు కొనుగోలు చేసే కుటుంబాలు, పక్కా ఇల్లు లేనివారు\n**పత్రాలు**: ఆధార్, ఆదాయ ధృవీకరణ పత్రం, బ్యాంక్ వివరాలు\n**అప్లై**: pmayg.nic.in లేదా సమీప CSC కేంద్రం",
                "suggestions": ["అర్హత ఎలా తెలుసుకోవాలి", "ఎక్కడ అప్లై చేయాలి", "ఇతర పథకాల సమాచారం"]
            },
            "ask_phc_location": {
                "message": "మీ దగ్గర ఆరోగ్య సేవలు తెలుసుకోవడానికి మీ స్థానం అవసరం. సాధారణ సమాచారం:\n\n**అత్యవసర సేవ**: 108కి కాల్ చేయండి\n**ప్రాథమిక ఆరోగ్య కేంద్రాలు (PHC)**: చాలా గ్రామాలు మరియు పట్టణాల్లో అందుబాటులో ఉన్నాయి\n**జిల్లా ఆసుపత్రులు**: ప్రతి జిల్లాలో ఉన్నాయి\n**ప్రభుత్వ ఆసుపత్రులు**: ప్రధాన నగరాల్లో ఉన్నాయి\n\nదయచేసి మీ పిన్ కోడ్ లేదా జిల్లా పేరు చెప్పండి.",
                "suggestions": ["మీ పిన్ కోడ్ చెప్పండి", "108కి కాల్ చేయండి", "ప్రత్యేక ఆసుపత్రి గురించి అడగండి"]
            },
            "ask_commodity_price": {
                "message": "ప్రస్తుత మండి ధరలు తెలుసుకోవడానికి:\n\n**Agmarknet**: అధికారిక మండి ధరల కోసం agmarknet.gov.in చూడండి\n**స్థానిక మండి**: సమీపంలోని వ్యవసాయ మార్కెట్‌ను సంప్రదించండి\n**కిసాన్ కాల్ సెంటర్**: సలహా కోసం 1800-180-1551కి కాల్ చేయండి\n\nసాధారణ వస్తువులు: గోధుమ, బియ్యం, పప్పులు, ఉల్లిపాయ, బంగాళాదుంప, టమోటా, చెక్కెర",
                "suggestions": ["agmarknet.gov.in చూడండి", "కిసాన్ హెల్ప్‌లైన్‌కు కాల్ చేయండి", "ప్రత్యేక పంట ధర అడగండి"]
            },
            "ask_pincode_help": {
                "message": "పిన్ కోడ్ సమాచారం కోసం మీ 6 అంకెల పిన్ కోడ్ చెప్పండి. జిల్లా, రాష్ట్రం, పోస్టాఫీస్ మరియు సమీప సేవల గురించి చెప్పగలను.\n\nఉదాహరణలు: 110001 (న్యూ ఢిల్లీ), 560001 (బెంగళూరు), 400001 (ముంబై)",
                "suggestions": ["మీ పిన్ కోడ్ చెప్పండి", "జిల్లా సమాచారం అడగండి", "స్థానిక సేవలు తెలుసుకోండి"]
            },
            "general_faq": {
                "message": "నేను ఈ విషయాల్లో సహాయం చేయగలను:\n\n**ప్రభుత్వ పథకాలు**: PMAY, జన ఔషధి, ఆయుష్మాన్ భారత్\n**ఆరోగ్య సేవలు**: ఆసుపత్రులు, PHC, అత్యవసర నంబర్లు\n**వ్యవసాయ సమాచారం**: మండి ధరలు, రైతు పథకాలు\n**ప్రజా ప్రతినిధులు**: MLA మరియు MP వివరాలు\n**పత్రాలు**: ఆధార్, రేషన్ కార్డు, ఓటర్ ఐడి ప్రక్రియ\n\nమీకు ఏ సమాచారం కావాలి?",
                "suggestions": ["ఒక ప్రత్యేక పథకం గురించి అడగండి", "ఆరోగ్య సేవలు తెలుసుకోండి", "ప్రతినిధి వివరాలు అడగండి"]
            }
        }
    }
    
    selected_language = responses.get(language, responses["english"])
    return selected_language.get(intent, {
        "message": "I understand your question. For specific information, please contact your local government office or visit india.gov.in",
        "suggestions": ["Contact local office", "Visit india.gov.in", "Try specific question"]
    })

@app.get("/api/v1/chat/intents")
async def get_supported_intents():
    return {
        "intents": [
            {
                "name": "survey_mla_name",
                "description": "Find information about your local MLA",
                "examples": ["Who is my MLA?", "Tell me about my local MLA"]
            },
            {
                "name": "survey_mp_name", 
                "description": "Find information about your Member of Parliament",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
