import os
import logging
import re
from typing import Dict, List, Optional, Any
import asyncio

from models.schemas import Intent

logger = logging.getLogger(__name__)

class IntentDetector:
    """Service for detecting user intents from natural language queries"""
    
    def __init__(self):
        self.confidence_threshold = 0.5
        
        # Intent patterns and keywords
        self.intent_patterns = {
            "survey_mla_name": {
                "keywords": ["mla", "विधायक", "member legislative assembly", "local representative", "assembly member"],
                "patterns": [
                    r"\b(who is|what is|tell me about|find|search).*(mla|विधायक|member legislative assembly)\b",
                    r"\b(mla|विधायक).*(name|information|details|contact)\b",
                    r"\b(my|our|local).*(mla|विधायक|representative)\b"
                ],
                "entities": ["location", "constituency"]
            },
            "survey_mp_name": {
                "keywords": ["mp", "सांसद", "member parliament", "parliament member", "lok sabha"],
                "patterns": [
                    r"\b(who is|what is|tell me about|find|search).*(mp|सांसद|member parliament)\b",
                    r"\b(mp|सांसद).*(name|information|details|contact)\b",
                    r"\b(my|our|local).*(mp|सांसद|parliament member)\b"
                ],
                "entities": ["location", "constituency"]
            },
            "opinion_mla": {
                "keywords": ["opinion", "feedback", "review", "satisfaction", "performance", "work", "राय"],
                "patterns": [
                    r"\b(opinion|feedback|review|satisfaction).*(mla|विधायक)\b",
                    r"\b(mla|विधायक).*(work|performance|good|bad|excellent|poor)\b",
                    r"\b(how is|what do you think).*(mla|विधायक)\b"
                ],
                "entities": ["sentiment", "representative_name"]
            },
            "opinion_mp": {
                "keywords": ["opinion", "feedback", "review", "satisfaction", "performance", "work", "राय"],
                "patterns": [
                    r"\b(opinion|feedback|review|satisfaction).*(mp|सांसद)\b",
                    r"\b(mp|सांसद).*(work|performance|good|bad|excellent|poor)\b",
                    r"\b(how is|what do you think).*(mp|सांसद)\b"
                ],
                "entities": ["sentiment", "representative_name"]
            },
            "ask_scheme_info": {
                "keywords": ["scheme", "yojana", "योजना", "pmay", "housing", "awas", "आवास", "benefit", "subsidy"],
                "patterns": [
                    r"\b(what is|tell me about|information about|details of).*(scheme|yojana|योजना)\b",
                    r"\b(pmay|pradhan mantri awas yojana|housing scheme|आवास योजना)\b",
                    r"\b(government scheme|सरकारी योजना|benefit|subsidy|लाभ)\b",
                    r"\b(how to apply|eligibility|documents required).*(scheme|yojana)\b"
                ],
                "entities": ["scheme_name"]
            },
            "ask_phc_location": {
                "keywords": ["hospital", "health", "phc", "doctor", "medical", "clinic", "अस्पताल", "स्वास्थ्य"],
                "patterns": [
                    r"\b(find|search|locate|where is).*(hospital|health center|phc|clinic|अस्पताल)\b",
                    r"\b(nearest|nearby|closest).*(hospital|health|medical|doctor|अस्पताल)\b",
                    r"\b(health facility|medical facility|primary health center)\b",
                    r"\b(emergency|ambulance|108)\b"
                ],
                "entities": ["location", "facility_type"]
            },
            "ask_commodity_price": {
                "keywords": ["price", "rate", "cost", "mandi", "market", "wheat", "rice", "dal", "कीमत", "दाम", "मंडी"],
                "patterns": [
                    r"\b(price|rate|cost|कीमत|दाम).*(wheat|rice|dal|onion|potato|गेहूं|चावल|दाल)\b",
                    r"\b(mandi|market|मंडी).*(price|rate|भाव)\b",
                    r"\b(current|today|latest).*(price|rate|कीमत)\b",
                    r"\b(commodity|crop|फसल).*(price|market|मंडी)\b"
                ],
                "entities": ["commodity_name", "location", "market_name"]
            },
            "ask_pincode_help": {
                "keywords": ["pincode", "postal code", "zip code", "pin", "पिन कोड", "district", "village"],
                "patterns": [
                    r"\b(pincode|postal code|pin code|पिन कोड).*(information|details|find)\b",
                    r"\b(which district|what district).*(pincode|pin|पिन)\b",
                    r"\b(village|district|state).*(pincode|pin code)\b",
                    r"\b\d{6}\b.*\b(information|details|location)\b"
                ],
                "entities": ["pincode", "location"]
            },
            "general_faq": {
                "keywords": ["how to", "apply", "documents", "process", "procedure", "कैसे", "आवेदन", "दस्तावेज"],
                "patterns": [
                    r"\b(how to|कैसे).*(apply|आवेदन|register|get)\b",
                    r"\b(documents|papers|दस्तावेज).*(required|needed|चाहिए)\b",
                    r"\b(process|procedure|प्रक्रिया|steps)\b",
                    r"\b(ration card|voter id|pan card|aadhaar|राशन कार्ड)\b"
                ],
                "entities": ["document_type", "service_type"]
            },
            "fallback_handoff": {
                "keywords": ["help", "support", "contact", "complaint", "problem", "मदद", "सहायता"],
                "patterns": [
                    r"\b(help|support|assistance|मदद|सहायता)\b",
                    r"\b(complaint|problem|issue|समस्या|शिकायत)\b",
                    r"\b(contact|call|phone|संपर्क)\b"
                ],
                "entities": []
            }
        }
        
        # Common entities extraction patterns
        self.entity_patterns = {
            "pincode": r"\b\d{6}\b",
            "phone": r"\b\d{10}\b|\b\d{3}-\d{3}-\d{4}\b",
            "location": r"\b(delhi|mumbai|bangalore|chennai|kolkata|hyderabad|pune|ahmedabad|jaipur|lucknow)\b",
            "commodity": r"\b(wheat|rice|dal|onion|potato|tomato|sugar|oil|गेहूं|चावल|दाल|प्याज|आलू)\b",
            "scheme": r"\b(pmay|jan aushadhi|ayushman bharat|kisan|pradhan mantri|आवास योजना)\b"
        }
    
    async def detect_intent(self, text: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        """Detect intent from user input text"""
        try:
            text_lower = text.lower()
            
            # Calculate confidence scores for each intent
            intent_scores = {}
            
            for intent_name, intent_config in self.intent_patterns.items():
                score = await self._calculate_intent_score(text_lower, intent_config)
                if score > 0:
                    intent_scores[intent_name] = score
            
            # Find the best matching intent
            if intent_scores:
                best_intent = max(intent_scores, key=intent_scores.get)
                confidence = intent_scores[best_intent]
                
                # Extract entities for the detected intent
                entities = await self._extract_entities(text, best_intent, context)
                
                return Intent(
                    name=best_intent,
                    confidence=confidence,
                    entities=entities
                )
            else:
                # Default to fallback if no intent matches
                return Intent(
                    name="fallback_handoff",
                    confidence=0.1,
                    entities={}
                )
        
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            return Intent(
                name="fallback_handoff",
                confidence=0.0,
                entities={}
            )
    
    async def _calculate_intent_score(self, text: str, intent_config: Dict[str, Any]) -> float:
        """Calculate confidence score for an intent"""
        score = 0.0
        
        # Check keyword matches
        keyword_matches = 0
        for keyword in intent_config["keywords"]:
            if keyword.lower() in text:
                keyword_matches += 1
        
        if keyword_matches > 0:
            score += (keyword_matches / len(intent_config["keywords"])) * 0.6
        
        # Check pattern matches
        pattern_matches = 0
        for pattern in intent_config["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                pattern_matches += 1
        
        if pattern_matches > 0:
            score += (pattern_matches / len(intent_config["patterns"])) * 0.4
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _extract_entities(self, text: str, intent: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract entities from text based on intent"""
        entities = {}
        
        try:
            # Extract common entities
            for entity_type, pattern in self.entity_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    entities[entity_type] = matches[0] if len(matches) == 1 else matches
            
            # Intent-specific entity extraction
            if intent in ["survey_mla_name", "survey_mp_name", "opinion_mla", "opinion_mp"]:
                # Extract representative names
                name_patterns = [
                    r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b",  # First Last
                    r"\b([A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+)\b"  # First M. Last
                ]
                for pattern in name_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        entities["representative_name"] = matches[0]
                        break
            
            elif intent == "ask_scheme_info":
                # Extract scheme names
                scheme_keywords = ["pmay", "awas", "housing", "jan aushadhi", "ayushman", "kisan"]
                for keyword in scheme_keywords:
                    if keyword in text.lower():
                        entities["scheme_name"] = keyword
                        break
            
            elif intent == "ask_commodity_price":
                # Extract commodity names
                commodity_keywords = ["wheat", "rice", "dal", "onion", "potato", "tomato", "sugar"]
                for commodity in commodity_keywords:
                    if commodity in text.lower():
                        entities["commodity_name"] = commodity
                        break
            
            elif intent == "ask_phc_location":
                # Extract facility types
                facility_types = ["hospital", "phc", "clinic", "health center"]
                for facility in facility_types:
                    if facility in text.lower():
                        entities["facility_type"] = facility
                        break
            
            # Add context information if available
            if context:
                for key, value in context.items():
                    if key not in entities and value:
                        entities[key] = value
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {}
    
    async def get_intent_suggestions(self, partial_text: str) -> List[Dict[str, Any]]:
        """Get intent suggestions based on partial text"""
        try:
            suggestions = []
            text_lower = partial_text.lower()
            
            for intent_name, intent_config in self.intent_patterns.items():
                # Check if any keywords match
                matching_keywords = [kw for kw in intent_config["keywords"] if kw in text_lower]
                
                if matching_keywords:
                    suggestions.append({
                        "intent": intent_name,
                        "confidence": len(matching_keywords) / len(intent_config["keywords"]),
                        "matching_keywords": matching_keywords,
                        "description": self._get_intent_description(intent_name)
                    })
            
            # Sort by confidence
            suggestions.sort(key=lambda x: x["confidence"], reverse=True)
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting intent suggestions: {str(e)}")
            return []
    
    def _get_intent_description(self, intent_name: str) -> str:
        """Get human-readable description for intent"""
        descriptions = {
            "survey_mla_name": "Find information about your local MLA",
            "survey_mp_name": "Find information about your Member of Parliament",
            "opinion_mla": "Share feedback about your MLA's performance",
            "opinion_mp": "Share feedback about your MP's performance",
            "ask_scheme_info": "Get information about government schemes",
            "ask_phc_location": "Find nearby health facilities and hospitals",
            "ask_commodity_price": "Check current commodity prices in mandis",
            "ask_pincode_help": "Get information about pincodes and locations",
            "general_faq": "General questions about government services",
            "fallback_handoff": "Get help and support"
        }
        
        return descriptions.get(intent_name, "General assistance")
    
    async def validate_intent(self, intent: Intent, context: Optional[Dict[str, Any]] = None) -> bool:
        """Validate if detected intent is reasonable given context"""
        try:
            # Check confidence threshold
            if intent.confidence < self.confidence_threshold:
                return False
            
            # Context-based validation
            if context:
                # If location context is available, location-based intents are more likely
                location_intents = ["ask_phc_location", "ask_commodity_price", "survey_mla_name", "survey_mp_name"]
                if any(key in context for key in ["pincode", "district", "state"]) and intent.name in location_intents:
                    return True
                
                # If previous conversation was about surveys, survey intents are more likely
                if context.get("previous_intent") in ["survey_mla_name", "survey_mp_name"] and intent.name.startswith("opinion_"):
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating intent: {str(e)}")
            return False
    
    async def get_required_entities(self, intent_name: str) -> List[str]:
        """Get list of required entities for an intent"""
        required_entities = {
            "survey_mla_name": ["location"],
            "survey_mp_name": ["location"],
            "opinion_mla": ["representative_name"],
            "opinion_mp": ["representative_name"],
            "ask_scheme_info": [],
            "ask_phc_location": ["location"],
            "ask_commodity_price": ["commodity_name"],
            "ask_pincode_help": ["pincode"],
            "general_faq": [],
            "fallback_handoff": []
        }
        
        return required_entities.get(intent_name, [])
    
    async def extract_missing_entities(self, intent: Intent, required_entities: List[str]) -> List[str]:
        """Find missing required entities"""
        missing = []
        
        for entity in required_entities:
            if entity not in intent.entities or not intent.entities[entity]:
                missing.append(entity)
        
        return missing
    
    async def generate_clarification_question(self, intent_name: str, missing_entities: List[str], language: str = "english") -> str:
        """Generate clarification question for missing entities"""
        try:
            questions = {
                "english": {
                    "location": "Could you please tell me your location (pincode, district, or state)?",
                    "pincode": "Please provide your 6-digit pincode.",
                    "commodity_name": "Which commodity price would you like to know about? (wheat, rice, dal, etc.)",
                    "representative_name": "Could you please tell me the name of your representative?",
                    "scheme_name": "Which government scheme would you like to know about?"
                },
                "hindi": {
                    "location": "कृपया अपना स्थान बताएं (पिन कोड, जिला, या राज्य)?",
                    "pincode": "कृपया अपना 6 अंकों का पिन कोड दें।",
                    "commodity_name": "आप किस वस्तु की कीमत जानना चाहते हैं? (गेहूं, चावल, दाल, आदि)",
                    "representative_name": "कृपया अपने प्रतिनिधि का नाम बताएं।",
                    "scheme_name": "आप किस सरकारी योजना के बारे में जानना चाहते हैं?"
                }
            }
            
            lang_questions = questions.get(language, questions["english"])
            
            if missing_entities:
                entity = missing_entities[0]  # Ask for first missing entity
                return lang_questions.get(entity, "Could you please provide more information?")
            
            return "How can I help you further?"
            
        except Exception as e:
            logger.error(f"Error generating clarification question: {str(e)}")
            return "Could you please provide more details?"
    
    async def update_intent_patterns(self, new_patterns: Dict[str, Any]):
        """Update intent patterns (for learning/improvement)"""
        try:
            for intent_name, pattern_data in new_patterns.items():
                if intent_name in self.intent_patterns:
                    # Add new keywords
                    if "keywords" in pattern_data:
                        self.intent_patterns[intent_name]["keywords"].extend(pattern_data["keywords"])
                    
                    # Add new patterns
                    if "patterns" in pattern_data:
                        self.intent_patterns[intent_name]["patterns"].extend(pattern_data["patterns"])
            
            logger.info("Intent patterns updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating intent patterns: {str(e)}")
    
    async def get_intent_statistics(self) -> Dict[str, Any]:
        """Get statistics about intent detection"""
        try:
            stats = {
                "total_intents": len(self.intent_patterns),
                "intents": {},
                "confidence_threshold": self.confidence_threshold
            }
            
            for intent_name, config in self.intent_patterns.items():
                stats["intents"][intent_name] = {
                    "keywords_count": len(config["keywords"]),
                    "patterns_count": len(config["patterns"]),
                    "entities_count": len(config["entities"])
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting intent statistics: {str(e)}")
            return {"error": str(e)}
