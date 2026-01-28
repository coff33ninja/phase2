"""Classify user query intent."""
from enum import Enum
from typing import Dict, List
from loguru import logger


class IntentType(Enum):
    """Types of user intents."""
    PERFORMANCE = "performance"
    OPTIMIZATION = "optimization"
    TROUBLESHOOTING = "troubleshooting"
    PREDICTION = "prediction"
    EXPLANATION = "explanation"
    RECOMMENDATION = "recommendation"
    STATUS = "status"
    HISTORY = "history"
    GENERAL = "general"


class IntentClassifier:
    """Classify user query intent using keyword matching."""
    
    # Intent keywords mapping
    INTENT_KEYWORDS = {
        IntentType.PERFORMANCE: [
            "slow", "fast", "speed", "performance", "lag", "laggy",
            "fps", "frame", "stutter", "freeze", "hang", "responsive"
        ],
        IntentType.OPTIMIZATION: [
            "optimize", "improve", "better", "enhance", "boost",
            "increase", "reduce", "lower", "free", "clean"
        ],
        IntentType.TROUBLESHOOTING: [
            "why", "problem", "issue", "error", "wrong", "broken",
            "not working", "fail", "crash", "bug", "fix"
        ],
        IntentType.PREDICTION: [
            "will", "predict", "forecast", "expect", "future",
            "next", "upcoming", "anticipate", "trend"
        ],
        IntentType.EXPLANATION: [
            "what", "how", "explain", "understand", "mean",
            "tell me", "show me", "describe", "clarify"
        ],
        IntentType.RECOMMENDATION: [
            "should", "recommend", "suggest", "advice", "best",
            "what to do", "help me", "guide", "tip"
        ],
        IntentType.STATUS: [
            "status", "current", "now", "right now", "at the moment",
            "currently", "state", "condition"
        ],
        IntentType.HISTORY: [
            "history", "past", "previous", "before", "yesterday",
            "last week", "trend", "over time", "change"
        ]
    }
    
    @classmethod
    def classify(cls, query: str) -> IntentType:
        """Classify user query intent.
        
        Args:
            query: User query string
            
        Returns:
            Detected intent type
        """
        query_lower = query.lower()
        
        # Score each intent
        scores: Dict[IntentType, int] = {
            intent: 0 for intent in IntentType
        }
        
        for intent, keywords in cls.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    scores[intent] += 1
        
        # Get highest scoring intent
        max_score = max(scores.values())
        
        if max_score == 0:
            logger.debug(f"No specific intent detected, using GENERAL")
            return IntentType.GENERAL
        
        # Get intent with highest score
        detected_intent = max(scores.items(), key=lambda x: x[1])[0]
        
        logger.info(f"Detected intent: {detected_intent.value} (score: {max_score})")
        return detected_intent
    
    @classmethod
    def classify_with_confidence(cls, query: str) -> Dict:
        """Classify with confidence scores.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with intent and confidence scores
        """
        query_lower = query.lower()
        
        # Score each intent
        scores: Dict[IntentType, int] = {
            intent: 0 for intent in IntentType
        }
        
        total_matches = 0
        for intent, keywords in cls.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    scores[intent] += 1
                    total_matches += 1
        
        # Calculate confidence scores
        if total_matches == 0:
            return {
                "intent": IntentType.GENERAL,
                "confidence": 0.5,
                "scores": {}
            }
        
        # Normalize scores to confidence (0-1)
        confidence_scores = {
            intent.value: score / total_matches
            for intent, score in scores.items()
            if score > 0
        }
        
        # Get primary intent
        primary_intent = max(scores.items(), key=lambda x: x[1])[0]
        primary_confidence = scores[primary_intent] / total_matches
        
        return {
            "intent": primary_intent,
            "confidence": round(primary_confidence, 2),
            "scores": confidence_scores
        }
    
    @classmethod
    def get_context_requirements(cls, intent: IntentType) -> List[str]:
        """Get required context for intent.
        
        Args:
            intent: Intent type
            
        Returns:
            List of required context components
        """
        requirements = {
            IntentType.PERFORMANCE: ["system_state", "patterns"],
            IntentType.OPTIMIZATION: ["system_state", "patterns", "predictions"],
            IntentType.TROUBLESHOOTING: ["system_state", "anomalies", "patterns"],
            IntentType.PREDICTION: ["patterns", "predictions"],
            IntentType.EXPLANATION: ["system_state", "patterns"],
            IntentType.RECOMMENDATION: ["system_state", "patterns", "predictions"],
            IntentType.STATUS: ["system_state"],
            IntentType.HISTORY: ["patterns"],
            IntentType.GENERAL: ["system_state"]
        }
        
        return requirements.get(intent, ["system_state"])
