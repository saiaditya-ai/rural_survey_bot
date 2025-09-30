import os
import logging
import re
from typing import Dict, List, Optional, Any
import asyncio

from models.schemas import Sentiment, SentimentLabel

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Service for analyzing sentiment of user opinions and feedback"""
    
    def __init__(self):
        self.confidence_threshold = 0.6
        
        # Sentiment lexicons for different languages
        self.sentiment_lexicons = {
            "english": {
                "positive": [
                    "good", "great", "excellent", "amazing", "wonderful", "fantastic", "awesome",
                    "helpful", "useful", "effective", "satisfied", "happy", "pleased", "impressed",
                    "outstanding", "brilliant", "superb", "marvelous", "terrific", "fabulous",
                    "appreciate", "grateful", "thankful", "commend", "praise", "recommend",
                    "love", "like", "enjoy", "admire", "respect", "support", "approve"
                ],
                "negative": [
                    "bad", "terrible", "awful", "horrible", "disgusting", "pathetic", "useless",
                    "disappointed", "frustrated", "angry", "upset", "annoyed", "irritated",
                    "dissatisfied", "unhappy", "displeased", "concerned", "worried", "troubled",
                    "hate", "dislike", "despise", "condemn", "criticize", "complain", "oppose",
                    "poor", "worst", "failure", "problem", "issue", "corrupt", "incompetent"
                ],
                "neutral": [
                    "okay", "fine", "average", "normal", "standard", "typical", "regular",
                    "moderate", "fair", "reasonable", "acceptable", "adequate", "sufficient"
                ]
            },
            "hindi": {
                "positive": [
                    "अच्छा", "बहुत अच्छा", "उत्कृष्ट", "शानदार", "बेहतरीन", "प्रभावी", "उपयोगी",
                    "खुश", "संतुष्ट", "प्रसन्न", "धन्यवाद", "आभारी", "सराहना", "समर्थन",
                    "पसंद", "प्रेम", "सम्मान", "तारीफ", "प्रशंसा", "बधाई", "काम का"
                ],
                "negative": [
                    "बुरा", "गलत", "खराब", "भयानक", "निराश", "परेशान", "गुस्सा", "चिंतित",
                    "असंतुष्ट", "नाखुश", "शिकायत", "समस्या", "परेशानी", "विरोध", "नापसंद",
                    "घृणा", "आपत्ति", "दुखी", "कष्ट", "तकलीफ", "भ्रष्ट", "अक्षम"
                ],
                "neutral": [
                    "ठीक", "सामान्य", "औसत", "साधारण", "मध्यम", "उचित", "स्वीकार्य"
                ]
            },
            "telugu": {
                "positive": [
                    "మంచి", "చాలా మంచి", "అద్భుతం", "అమోఘం", "అందం", "సంతోషం", "ఆనందం",
                    "కృతజ్ఞత", "ధన్యవాదాలు", "మెచ్చుకోవాలి", "మద్దతు", "ఇష్టం", "ప్రేమ"
                ],
                "negative": [
                    "చెడు", "దారుణం", "భయంకరం", "నిరాశ", "కోపం", "దుఃఖం", "సమస్య",
                    "ఇబ్బంది", "వ్యతిరేకత", "అసంతృప్తి", "ఫిర్యాదు", "ఇష్టం లేదు"
                ],
                "neutral": [
                    "సరే", "సాధారణం", "మధ్యమం", "ఆమోదయోగ్యం", "సరిపోతుంది"
                ]
            }
        }
        
        # Sentiment modifiers
        self.intensifiers = {
            "english": ["very", "extremely", "really", "quite", "absolutely", "completely", "totally"],
            "hindi": ["बहुत", "अत्यधिक", "काफी", "पूरी तरह", "बिल्कुल", "सच में"],
            "telugu": ["చాలా", "అత్యంత", "పూర్తిగా", "నిజంగా", "మరీ"]
        }
        
        self.negators = {
            "english": ["not", "no", "never", "nothing", "nobody", "nowhere", "neither", "nor"],
            "hindi": ["नहीं", "न", "कभी नहीं", "कुछ नहीं", "कोई नहीं"],
            "telugu": ["లేదు", "కాదు", "ఎప్పుడూ లేదు", "ఏమీ లేదు"]
        }
        
        # Contextual patterns
        self.context_patterns = {
            "work_performance": {
                "positive": ["doing good work", "working well", "effective work", "good job"],
                "negative": ["not working", "poor work", "ineffective", "bad job"]
            },
            "service_quality": {
                "positive": ["good service", "helpful service", "quick response", "efficient"],
                "negative": ["poor service", "slow response", "unhelpful", "inefficient"]
            },
            "accessibility": {
                "positive": ["easily accessible", "available", "reachable", "approachable"],
                "negative": ["not accessible", "unavailable", "unreachable", "difficult to reach"]
            }
        }
    
    async def analyze_sentiment(self, text: str, language: str = "english") -> Sentiment:
        """Analyze sentiment of given text"""
        try:
            if not text or not text.strip():
                return Sentiment(
                    label=SentimentLabel.NEUTRAL,
                    score=0.0,
                    confidence=0.0
                )
            
            text_clean = self._preprocess_text(text)
            
            # Get sentiment scores
            sentiment_scores = await self._calculate_sentiment_scores(text_clean, language)
            
            # Determine final sentiment
            sentiment_label, confidence = self._determine_sentiment(sentiment_scores)
            
            # Calculate final score
            if sentiment_label == SentimentLabel.POSITIVE:
                score = sentiment_scores["positive"]
            elif sentiment_label == SentimentLabel.NEGATIVE:
                score = -sentiment_scores["negative"]  # Negative score for negative sentiment
            else:
                score = 0.0
            
            return Sentiment(
                label=sentiment_label,
                score=score,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return Sentiment(
                label=SentimentLabel.NEUTRAL,
                score=0.0,
                confidence=0.0
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\-]', '', text)
        
        return text
    
    async def _calculate_sentiment_scores(self, text: str, language: str) -> Dict[str, float]:
        """Calculate sentiment scores for positive, negative, and neutral"""
        scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        
        # Get lexicon for the language
        lexicon = self.sentiment_lexicons.get(language, self.sentiment_lexicons["english"])
        intensifiers = self.intensifiers.get(language, self.intensifiers["english"])
        negators = self.negators.get(language, self.negators["english"])
        
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return scores
        
        # Track sentiment words and their contexts
        sentiment_matches = {"positive": 0, "negative": 0, "neutral": 0}
        
        for i, word in enumerate(words):
            # Check for negation in previous words
            is_negated = False
            if i > 0:
                for j in range(max(0, i-3), i):  # Check 3 words before
                    if words[j] in negators:
                        is_negated = True
                        break
            
            # Check for intensifiers in previous words
            intensity_multiplier = 1.0
            if i > 0:
                for j in range(max(0, i-2), i):  # Check 2 words before
                    if words[j] in intensifiers:
                        intensity_multiplier = 1.5
                        break
            
            # Check sentiment
            for sentiment_type, sentiment_words in lexicon.items():
                if word in sentiment_words:
                    weight = intensity_multiplier
                    
                    # Apply negation
                    if is_negated:
                        if sentiment_type == "positive":
                            sentiment_matches["negative"] += weight
                        elif sentiment_type == "negative":
                            sentiment_matches["positive"] += weight
                        else:
                            sentiment_matches["neutral"] += weight
                    else:
                        sentiment_matches[sentiment_type] += weight
        
        # Calculate normalized scores
        total_sentiment_words = sum(sentiment_matches.values())
        
        if total_sentiment_words > 0:
            for sentiment_type in scores:
                scores[sentiment_type] = sentiment_matches[sentiment_type] / total_sentiment_words
        
        # Apply contextual analysis
        context_scores = await self._analyze_contextual_sentiment(text)
        
        # Combine lexical and contextual scores
        for sentiment_type in scores:
            if sentiment_type in context_scores:
                scores[sentiment_type] = (scores[sentiment_type] + context_scores[sentiment_type]) / 2
        
        return scores
    
    async def _analyze_contextual_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment based on contextual patterns"""
        context_scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        
        pattern_matches = {"positive": 0, "negative": 0}
        
        for context_type, patterns in self.context_patterns.items():
            for sentiment_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if pattern in text:
                        pattern_matches[sentiment_type] += 1
        
        total_matches = sum(pattern_matches.values())
        
        if total_matches > 0:
            context_scores["positive"] = pattern_matches["positive"] / total_matches
            context_scores["negative"] = pattern_matches["negative"] / total_matches
            context_scores["neutral"] = 1.0 - (context_scores["positive"] + context_scores["negative"])
        
        return context_scores
    
    def _determine_sentiment(self, scores: Dict[str, float]) -> tuple[SentimentLabel, float]:
        """Determine final sentiment label and confidence"""
        max_score = max(scores.values())
        
        if max_score < 0.1:  # Very low scores indicate neutral
            return SentimentLabel.NEUTRAL, max_score
        
        # Find the sentiment with highest score
        if scores["positive"] == max_score:
            sentiment = SentimentLabel.POSITIVE
        elif scores["negative"] == max_score:
            sentiment = SentimentLabel.NEGATIVE
        else:
            sentiment = SentimentLabel.NEUTRAL
        
        # Calculate confidence based on score difference
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            confidence = sorted_scores[0] - sorted_scores[1]
        else:
            confidence = sorted_scores[0]
        
        # Ensure confidence is within reasonable bounds
        confidence = min(max(confidence, 0.0), 1.0)
        
        return sentiment, confidence
    
    async def analyze_batch_sentiments(self, texts: List[str], language: str = "english") -> List[Sentiment]:
        """Analyze sentiment for multiple texts"""
        try:
            tasks = [self.analyze_sentiment(text, language) for text in texts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            sentiments = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in batch sentiment analysis: {str(result)}")
                    sentiments.append(Sentiment(
                        label=SentimentLabel.NEUTRAL,
                        score=0.0,
                        confidence=0.0
                    ))
                else:
                    sentiments.append(result)
            
            return sentiments
            
        except Exception as e:
            logger.error(f"Error in batch sentiment analysis: {str(e)}")
            return [Sentiment(label=SentimentLabel.NEUTRAL, score=0.0, confidence=0.0) for _ in texts]
    
    async def get_sentiment_summary(self, sentiments: List[Sentiment]) -> Dict[str, Any]:
        """Get summary statistics for a list of sentiments"""
        try:
            if not sentiments:
                return {
                    "total_count": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "average_score": 0.0,
                    "confidence_average": 0.0
                }
            
            positive_count = sum(1 for s in sentiments if s.label == SentimentLabel.POSITIVE)
            negative_count = sum(1 for s in sentiments if s.label == SentimentLabel.NEGATIVE)
            neutral_count = sum(1 for s in sentiments if s.label == SentimentLabel.NEUTRAL)
            
            total_score = sum(s.score for s in sentiments)
            total_confidence = sum(s.confidence for s in sentiments)
            
            return {
                "total_count": len(sentiments),
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_percentage": (positive_count / len(sentiments)) * 100,
                "negative_percentage": (negative_count / len(sentiments)) * 100,
                "neutral_percentage": (neutral_count / len(sentiments)) * 100,
                "average_score": total_score / len(sentiments),
                "confidence_average": total_confidence / len(sentiments)
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment summary: {str(e)}")
            return {"error": str(e)}
    
    async def detect_language(self, text: str) -> str:
        """Detect language of the text (basic implementation)"""
        try:
            # Simple language detection based on character sets and common words
            
            # Check for Hindi (Devanagari script)
            if re.search(r'[\u0900-\u097F]', text):
                return "hindi"
            
            # Check for Telugu script
            if re.search(r'[\u0C00-\u0C7F]', text):
                return "telugu"
            
            # Check for common Hindi words in Roman script
            hindi_words = ["hai", "hain", "ka", "ki", "ke", "mein", "aur", "yeh", "woh"]
            text_lower = text.lower()
            hindi_word_count = sum(1 for word in hindi_words if word in text_lower)
            
            if hindi_word_count >= 2:
                return "hindi"
            
            # Default to English
            return "english"
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return "english"
    
    async def add_custom_sentiment_words(self, language: str, sentiment_type: str, words: List[str]):
        """Add custom sentiment words to the lexicon"""
        try:
            if language not in self.sentiment_lexicons:
                self.sentiment_lexicons[language] = {"positive": [], "negative": [], "neutral": []}
            
            if sentiment_type in self.sentiment_lexicons[language]:
                self.sentiment_lexicons[language][sentiment_type].extend(words)
                logger.info(f"Added {len(words)} {sentiment_type} words to {language} lexicon")
            
        except Exception as e:
            logger.error(f"Error adding custom sentiment words: {str(e)}")
    
    async def get_sentiment_explanation(self, text: str, sentiment: Sentiment, language: str = "english") -> Dict[str, Any]:
        """Get explanation for why a particular sentiment was detected"""
        try:
            explanation = {
                "detected_sentiment": sentiment.label.value,
                "confidence": sentiment.confidence,
                "score": sentiment.score,
                "contributing_factors": []
            }
            
            # Find words that contributed to sentiment
            lexicon = self.sentiment_lexicons.get(language, self.sentiment_lexicons["english"])
            words = text.lower().split()
            
            for word in words:
                for sentiment_type, sentiment_words in lexicon.items():
                    if word in sentiment_words:
                        explanation["contributing_factors"].append({
                            "word": word,
                            "sentiment": sentiment_type,
                            "type": "lexical"
                        })
            
            # Find contextual patterns
            for context_type, patterns in self.context_patterns.items():
                for sentiment_type, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        if pattern in text.lower():
                            explanation["contributing_factors"].append({
                                "pattern": pattern,
                                "sentiment": sentiment_type,
                                "type": "contextual",
                                "context": context_type
                            })
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error getting sentiment explanation: {str(e)}")
            return {"error": str(e)}
    
    async def calibrate_sentiment_threshold(self, labeled_data: List[Dict[str, Any]]):
        """Calibrate sentiment analysis threshold based on labeled data"""
        try:
            # This would be used to improve accuracy based on feedback
            # For now, just log the attempt
            logger.info(f"Calibration requested with {len(labeled_data)} samples")
            
            # In a real implementation, you would:
            # 1. Analyze the labeled data
            # 2. Calculate optimal thresholds
            # 3. Update the confidence_threshold
            # 4. Possibly adjust lexicon weights
            
        except Exception as e:
            logger.error(f"Error calibrating sentiment threshold: {str(e)}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.sentiment_lexicons.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check sentiment analyzer health"""
        try:
            # Test basic functionality
            test_text = "This is a good service"
            test_result = await self.analyze_sentiment(test_text)
            
            return {
                "status": "healthy",
                "supported_languages": self.get_supported_languages(),
                "lexicon_sizes": {
                    lang: {sentiment: len(words) for sentiment, words in lexicon.items()}
                    for lang, lexicon in self.sentiment_lexicons.items()
                },
                "test_result": {
                    "text": test_text,
                    "sentiment": test_result.label.value,
                    "confidence": test_result.confidence
                }
            }
            
        except Exception as e:
            logger.error(f"Sentiment analyzer health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
