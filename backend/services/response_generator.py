import os
import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.schemas import Intent, HealthFacility, CommodityPrice, SchemeInfo, PoliticalRepresentative

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Service for generating natural language responses based on intent and data"""
    
    def __init__(self):
        self.default_language = os.getenv("DEFAULT_LANGUAGE", "english")
        
        # Response templates for different intents and languages
        self.response_templates = {
            "english": {
                "mla_info": [
                    "Your MLA is {name} from {constituency}. You can contact them at {contact}.",
                    "The Member of Legislative Assembly for your area is {name}. Their office is located at {address}.",
                    "Your local MLA {name} represents {constituency} constituency. Contact: {contact}"
                ],
                "mp_info": [
                    "Your Member of Parliament is {name} from {constituency}. Contact: {contact}",
                    "The MP for your area is {name}. You can reach them at {contact}.",
                    "Your parliamentary representative is {name} from {constituency} constituency."
                ],
                "scheme_info": [
                    "The {scheme_name} provides the following benefits: {benefits}. To apply, {process}",
                    "Here's information about {scheme_name}: {description}. Eligibility: {eligibility}",
                    "{scheme_name} offers {benefits}. Required documents: {documents}"
                ],
                "health_facilities": [
                    "I found {count} health facilities near you: {facilities}",
                    "Here are nearby health centers: {facilities}. The closest is {nearest}",
                    "Available health facilities in your area: {facilities}"
                ],
                "commodity_prices": [
                    "Current {commodity} prices: {prices}. Latest update: {date}",
                    "Today's {commodity} rates in nearby markets: {prices}",
                    "Market prices for {commodity}: {prices}"
                ],
                "pincode_info": [
                    "Pincode {pincode} belongs to {district} district, {state}. Post office: {post_office}",
                    "Information for {pincode}: District - {district}, State - {state}",
                    "{pincode} is located in {district}, {state}. Region: {region}"
                ],
                "general_faq": [
                    "Here's the information you requested: {answer}",
                    "Based on your question: {answer}",
                    "{answer}. For more details, visit {website}"
                ],
                "fallback": [
                    "I'm sorry, I couldn't find specific information. Please contact local authorities.",
                    "For this query, I recommend visiting your nearest government office.",
                    "I apologize, but I need more information to help you better."
                ]
            },
            "hindi": {
                "mla_info": [
                    "आपके विधायक {name} हैं {constituency} से। संपर्क: {contact}",
                    "आपके क्षेत्र के विधायक {name} हैं। उनका कार्यालय {address} में है।",
                    "आपके स्थानीय विधायक {name} {constituency} का प्रतिनिधित्व करते हैं।"
                ],
                "mp_info": [
                    "आपके सांसद {name} हैं {constituency} से। संपर्क: {contact}",
                    "आपके क्षेत्र के सांसद {name} हैं। संपर्क: {contact}",
                    "आपके संसदीय प्रतिनिधि {name} {constituency} से हैं।"
                ],
                "scheme_info": [
                    "{scheme_name} के लाभ: {benefits}। आवेदन प्रक्रिया: {process}",
                    "{scheme_name} की जानकारी: {description}। पात्रता: {eligibility}",
                    "{scheme_name} प्रदान करता है: {benefits}। आवश्यक दस्तावेज: {documents}"
                ],
                "health_facilities": [
                    "आपके पास {count} स्वास्थ्य सुविधाएं मिलीं: {facilities}",
                    "निकटतम स्वास्थ्य केंद्र: {facilities}। सबसे पास: {nearest}",
                    "आपके क्षेत्र में उपलब्ध स्वास्थ्य सुविधाएं: {facilities}"
                ],
                "commodity_prices": [
                    "वर्तमान {commodity} की कीमतें: {prices}। अपडेट: {date}",
                    "आज की {commodity} दरें: {prices}",
                    "{commodity} के बाजार भाव: {prices}"
                ],
                "fallback": [
                    "खुशी, मुझे विशिष्ट जानकारी नहीं मिली। कृपया स्थानीय अधिकारियों से संपर्क करें।",
                    "इस प्रश्न के लिए, मैं निकटतम सरकारी कार्यालय जाने की सलाह देता हूं।"
                ]
            }
        }
        
        # Suggestion templates
        self.suggestion_templates = {
            "english": {
                "after_mla_info": ["Ask about your MP", "Get scheme information", "Find health facilities"],
                "after_scheme_info": ["Check eligibility", "Find application centers", "Get required documents"],
                "after_health_info": ["Get directions", "Check services available", "Find contact numbers"],
                "general": ["Ask about government schemes", "Find your representatives", "Check commodity prices"]
            },
            "hindi": {
                "after_mla_info": ["अपने सांसद के बारे में पूछें", "योजना की जानकारी लें", "स्वास्थ्य सुविधाएं खोजें"],
                "after_scheme_info": ["पात्रता जांचें", "आवेदन केंद्र खोजें", "आवश्यक दस्तावेज देखें"],
                "general": ["सरकारी योजनाओं के बारे में पूछें", "अपने प्रतिनिधि खोजें", "कमोडिटी की कीमतें देखें"]
            }
        }
    
    async def generate_response(self, intent: Intent, data: Dict[str, Any], language: str = "english", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate natural language response based on intent and data"""
        try:
            response_data = {
                "message": "",
                "source": data.get("source", "unknown"),
                "suggestions": [],
                "metadata": {}
            }
            
            # Route to specific response generator
            if intent.name in ["survey_mla_name", "opinion_mla"]:
                response_data = await self._generate_mla_response(data, language, context)
            elif intent.name in ["survey_mp_name", "opinion_mp"]:
                response_data = await self._generate_mp_response(data, language, context)
            elif intent.name == "ask_scheme_info":
                response_data = await self._generate_scheme_response(data, language, context)
            elif intent.name == "ask_phc_location":
                response_data = await self._generate_health_response(data, language, context)
            elif intent.name == "ask_commodity_price":
                response_data = await self._generate_price_response(data, language, context)
            elif intent.name == "ask_pincode_help":
                response_data = await self._generate_pincode_response(data, language, context)
            elif intent.name == "general_faq":
                response_data = await self._generate_faq_response(data, language, context)
            else:
                response_data = await self._generate_fallback_response(data, language, context)
            
            # Add source disclaimer if using mock data
            if response_data["source"] == "mock":
                disclaimer = self._get_mock_disclaimer(language)
                response_data["message"] += f"\n\n{disclaimer}"
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return await self._generate_error_response(language)
    
    async def _generate_mla_response(self, data: Dict[str, Any], language: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate MLA information response"""
        try:
            templates = self.response_templates.get(language, self.response_templates["english"])
            
            if data["type"] == "mla_info" and data["data"]:
                mla_info = data["data"]
                template = random.choice(templates["mla_info"])
                
                message = template.format(
                    name=mla_info.get("name", "Unknown"),
                    constituency=mla_info.get("constituency", "Unknown"),
                    contact=mla_info.get("contact_info", {}).get("phone", "Not available"),
                    address=mla_info.get("office_address", "Not available")
                )
                
                suggestions = self.suggestion_templates.get(language, self.suggestion_templates["english"]).get("after_mla_info", [])
                
                return {
                    "message": message,
                    "source": data["source"],
                    "suggestions": suggestions,
                    "metadata": {"representative_type": "MLA", "constituency": mla_info.get("constituency")}
                }
            else:
                fallback_msg = "I couldn't find information about your MLA. Please provide your constituency or district."
                if language == "hindi":
                    fallback_msg = "मुझे आपके विधायक की जानकारी नहीं मिली। कृपया अपना निर्वाचन क्षेत्र या जिला बताएं।"
                
                return {
                    "message": fallback_msg,
                    "source": "fallback",
                    "suggestions": ["Provide your pincode", "Tell me your district"],
                    "metadata": {}
                }
                
        except Exception as e:
            logger.error(f"Error generating MLA response: {str(e)}")
            return await self._generate_error_response(language)
    
    async def _generate_mp_response(self, data: Dict[str, Any], language: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate MP information response"""
        try:
            templates = self.response_templates.get(language, self.response_templates["english"])
            
            if data["type"] == "mp_info" and data["data"]:
                mp_info = data["data"]
                template = random.choice(templates["mp_info"])
                
                message = template.format(
                    name=mp_info.get("name", "Unknown"),
                    constituency=mp_info.get("constituency", "Unknown"),
                    contact=mp_info.get("contact_info", {}).get("phone", "Not available")
                )
                
                suggestions = self.suggestion_templates.get(language, self.suggestion_templates["english"]).get("after_mla_info", [])
                
                return {
                    "message": message,
                    "source": data["source"],
                    "suggestions": suggestions,
                    "metadata": {"representative_type": "MP", "constituency": mp_info.get("constituency")}
                }
            else:
                fallback_msg = "I couldn't find information about your MP. Please provide your constituency."
                if language == "hindi":
                    fallback_msg = "मुझे आपके सांसद की जानकारी नहीं मिली। कृपया अपना निर्वाचन क्षेत्र बताएं।"
                
                return {
                    "message": fallback_msg,
                    "source": "fallback",
                    "suggestions": ["Provide your pincode", "Tell me your constituency"],
                    "metadata": {}
                }
                
        except Exception as e:
            logger.error(f"Error generating MP response: {str(e)}")
            return await self._generate_error_response(language)
    
    async def _generate_scheme_response(self, data: Dict[str, Any], language: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate scheme information response"""
        try:
            templates = self.response_templates.get(language, self.response_templates["english"])
            
            if data["type"] == "scheme_info" and data["data"]:
                scheme_info = data["data"]
                template = random.choice(templates["scheme_info"])
                
                benefits = ", ".join(scheme_info.get("benefits", [])[:3])  # First 3 benefits
                eligibility = ", ".join(scheme_info.get("eligibility", [])[:2])  # First 2 criteria
                documents = ", ".join(scheme_info.get("required_documents", [])[:3])  # First 3 documents
                
                message = template.format(
                    scheme_name=scheme_info.get("scheme_name", "Government Scheme"),
                    description=scheme_info.get("description", ""),
                    benefits=benefits,
                    eligibility=eligibility,
                    documents=documents,
                    process=scheme_info.get("application_process", [{}])[0] if scheme_info.get("application_process") else "Visit local office"
                )
                
                suggestions = self.suggestion_templates.get(language, self.suggestion_templates["english"]).get("after_scheme_info", [])
                
                return {
                    "message": message,
                    "source": data["source"],
                    "suggestions": suggestions,
                    "metadata": {
                        "scheme_name": scheme_info.get("scheme_name"),
                        "official_website": scheme_info.get("official_website"),
                        "helpline": scheme_info.get("helpline")
                    }
                }
            else:
                fallback_msg = "I couldn't find specific scheme information. Please specify the scheme name."
                if language == "hindi":
                    fallback_msg = "मुझे विशिष्ट योजना की जानकारी नहीं मिली। कृपया योजना का नाम बताएं।"
                
                return {
                    "message": fallback_msg,
                    "source": "fallback",
                    "suggestions": ["Ask about PMAY", "Ask about Jan Aushadhi", "Ask about Ayushman Bharat"],
                    "metadata": {}
                }
                
        except Exception as e:
            logger.error(f"Error generating scheme response: {str(e)}")
            return await self._generate_error_response(language)
    
    async def _generate_health_response(self, data: Dict[str, Any], language: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate health facilities response"""
        try:
            templates = self.response_templates.get(language, self.response_templates["english"])
            
            if data["type"] == "phc_info" and data["data"]:
                facilities = data["data"]
                if isinstance(facilities, list) and facilities:
                    facility_names = [f["name"] for f in facilities[:3]]  # Top 3 facilities
                    facilities_text = ", ".join(facility_names)
                    nearest = facilities[0]["name"] if facilities else "Unknown"
                    
                    template = random.choice(templates["health_facilities"])
                    message = template.format(
                        count=len(facilities),
                        facilities=facilities_text,
                        nearest=nearest
                    )
                    
                    # Add contact information for nearest facility
                    if facilities[0].get("phone"):
                        contact_msg = f"\nNearest facility contact: {facilities[0]['phone']}"
                        if language == "hindi":
                            contact_msg = f"\nनिकटतम सुविधा संपर्क: {facilities[0]['phone']}"
                        message += contact_msg
                    
                    suggestions = self.suggestion_templates.get(language, self.suggestion_templates["english"]).get("after_health_info", [])
                    
                    return {
                        "message": message,
                        "source": data["source"],
                        "suggestions": suggestions,
                        "metadata": {
                            "facilities_count": len(facilities),
                            "nearest_facility": facilities[0]["name"],
                            "emergency_number": "108"
                        }
                    }
            
            fallback_msg = "I couldn't find health facilities in your area. For emergencies, call 108."
            if language == "hindi":
                fallback_msg = "मुझे आपके क्षेत्र में स्वास्थ्य सुविधाएं नहीं मिलीं। आपातकाल के लिए 108 पर कॉल करें।"
            
            return {
                "message": fallback_msg,
                "source": "fallback",
                "suggestions": ["Provide your pincode", "Ask for district hospital"],
                "metadata": {"emergency_number": "108"}
            }
                
        except Exception as e:
            logger.error(f"Error generating health response: {str(e)}")
            return await self._generate_error_response(language)
    
    async def _generate_price_response(self, data: Dict[str, Any], language: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate commodity price response"""
        try:
            templates = self.response_templates.get(language, self.response_templates["english"])
            
            if data["type"] == "price_info" and data["data"]:
                prices = data["data"]
                if isinstance(prices, list) and prices:
                    commodity = prices[0].get("commodity", "commodity")
                    price_text = []
                    
                    for price in prices[:3]:  # Top 3 prices
                        market = price.get("market_name", "Unknown Market")
                        rate = price.get("price_per_unit", 0)
                        unit = price.get("unit", "kg")
                        price_text.append(f"{market}: ₹{rate}/{unit}")
                    
                    prices_formatted = ", ".join(price_text)
                    date = prices[0].get("date", datetime.now()).strftime("%Y-%m-%d")
                    
                    template = random.choice(templates["commodity_prices"])
                    message = template.format(
                        commodity=commodity,
                        prices=prices_formatted,
                        date=date
                    )
                    
                    return {
                        "message": message,
                        "source": data["source"],
                        "suggestions": ["Check other commodities", "Find nearest mandi", "Get price trends"],
                        "metadata": {
                            "commodity": commodity,
                            "price_count": len(prices),
                            "last_updated": date
                        }
                    }
            
            fallback_msg = "I couldn't find current commodity prices. Please try again later."
            if language == "hindi":
                fallback_msg = "मुझे वर्तमान कमोडिटी की कीमतें नहीं मिलीं। कृपया बाद में पुनः प्रयास करें।"
            
            return {
                "message": fallback_msg,
                "source": "fallback",
                "suggestions": ["Specify commodity name", "Provide your location"],
                "metadata": {}
            }
                
        except Exception as e:
            logger.error(f"Error generating price response: {str(e)}")
            return await self._generate_error_response(language)
    
    async def _generate_pincode_response(self, data: Dict[str, Any], language: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate pincode information response"""
        try:
            templates = self.response_templates.get(language, self.response_templates["english"])
            
            if data["type"] == "pincode_info" and data["data"]:
                pincode_info = data["data"]
                template = random.choice(templates["pincode_info"])
                
                message = template.format(
                    pincode=pincode_info.get("pincode", ""),
                    district=pincode_info.get("district", "Unknown"),
                    state=pincode_info.get("state", "Unknown"),
                    post_office=pincode_info.get("post_office", "Unknown"),
                    region=pincode_info.get("region", "Unknown")
                )
                
                return {
                    "message": message,
                    "source": data["source"],
                    "suggestions": ["Find health facilities here", "Check local representatives", "Get scheme information"],
                    "metadata": {
                        "pincode": pincode_info.get("pincode"),
                        "district": pincode_info.get("district"),
                        "state": pincode_info.get("state")
                    }
                }
            
            fallback_msg = "I couldn't find information for this pincode. Please check and try again."
            if language == "hindi":
                fallback_msg = "मुझे इस पिन कोड की जानकारी नहीं मिली। कृपया जांचें और पुनः प्रयास करें।"
            
            return {
                "message": fallback_msg,
                "source": "fallback",
                "suggestions": ["Verify pincode", "Try with district name"],
                "metadata": {}
            }
                
        except Exception as e:
            logger.error(f"Error generating pincode response: {str(e)}")
            return await self._generate_error_response(language)
    
    async def _generate_faq_response(self, data: Dict[str, Any], language: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate FAQ response"""
        try:
            templates = self.response_templates.get(language, self.response_templates["english"])
            
            if data["type"] == "faq" and data["data"]:
                faq_data = data["data"]
                template = random.choice(templates["general_faq"])
                
                message = template.format(
                    answer=faq_data.get("answer", ""),
                    website="india.gov.in"
                )
                
                return {
                    "message": message,
                    "source": data["source"],
                    "suggestions": self.suggestion_templates.get(language, self.suggestion_templates["english"]).get("general", []),
                    "metadata": {
                        "category": faq_data.get("category", "general"),
                        "source": faq_data.get("source", "knowledge_base")
                    }
                }
            
            fallback_msg = "I understand your question but need more specific information to help you better."
            if language == "hindi":
                fallback_msg = "मैं आपका प्रश्न समझता हूं लेकिन आपकी बेहतर सहायता के लिए अधिक विशिष्ट जानकारी चाहिए।"
            
            return {
                "message": fallback_msg,
                "source": "fallback",
                "suggestions": ["Ask about specific schemes", "Provide more details", "Contact local office"],
                "metadata": {}
            }
                
        except Exception as e:
            logger.error(f"Error generating FAQ response: {str(e)}")
            return await self._generate_error_response(language)
    
    async def _generate_fallback_response(self, data: Dict[str, Any], language: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback response"""
        try:
            templates = self.response_templates.get(language, self.response_templates["english"])
            fallback_templates = templates.get("fallback", ["I'm sorry, I couldn't help with that."])
            
            message = random.choice(fallback_templates)
            
            return {
                "message": message,
                "source": "fallback",
                "suggestions": self.suggestion_templates.get(language, self.suggestion_templates["english"]).get("general", []),
                "metadata": {"fallback_reason": "intent_not_handled"}
            }
                
        except Exception as e:
            logger.error(f"Error generating fallback response: {str(e)}")
            return await self._generate_error_response(language)
    
    async def _generate_error_response(self, language: str) -> Dict[str, Any]:
        """Generate error response"""
        error_messages = {
            "english": "I'm experiencing technical difficulties. Please try again later or contact local authorities.",
            "hindi": "मुझे तकनीकी समस्या हो रही है। कृपया बाद में पुनः प्रयास करें या स्थानीय अधिकारियों से संपर्क करें।"
        }
        
        return {
            "message": error_messages.get(language, error_messages["english"]),
            "source": "error",
            "suggestions": ["Try again later", "Contact local office"],
            "metadata": {"error": True}
        }
    
    def _get_mock_disclaimer(self, language: str) -> str:
        """Get disclaimer for mock data"""
        disclaimers = {
            "english": "Note: This information is from our sample database for demonstration purposes. For official information, please contact relevant authorities.",
            "hindi": "नोट: यह जानकारी प्रदर्शन उद्देश्यों के लिए हमारे नमूना डेटाबेस से है। आधिकारिक जानकारी के लिए, कृपया संबंधित अधिकारियों से संपर्क करें।"
        }
        
        return disclaimers.get(language, disclaimers["english"])
    
    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.response_templates.keys())
    
    async def add_custom_template(self, language: str, intent: str, templates: List[str]):
        """Add custom response templates"""
        try:
            if language not in self.response_templates:
                self.response_templates[language] = {}
            
            if intent not in self.response_templates[language]:
                self.response_templates[language][intent] = []
            
            self.response_templates[language][intent].extend(templates)
            logger.info(f"Added {len(templates)} templates for {intent} in {language}")
            
        except Exception as e:
            logger.error(f"Error adding custom templates: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check response generator health"""
        try:
            # Test basic functionality
            test_intent = Intent(name="test", confidence=1.0, entities={})
            test_data = {"type": "test", "data": {"message": "test"}, "source": "test"}
            
            test_response = await self.generate_response(test_intent, test_data)
            
            return {
                "status": "healthy",
                "supported_languages": await self.get_supported_languages(),
                "template_counts": {
                    lang: {intent: len(templates) for intent, templates in lang_templates.items()}
                    for lang, lang_templates in self.response_templates.items()
                },
                "test_response": test_response
            }
            
        except Exception as e:
            logger.error(f"Response generator health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
