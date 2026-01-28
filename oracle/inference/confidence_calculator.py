"""Confidence calculation for predictions."""
import numpy as np
from typing import Dict, List
from loguru import logger


class ConfidenceCalculator:
    """Calculate confidence scores for predictions."""
    
    @staticmethod
    def calculate_prediction_confidence(
        predictions: np.ndarray,
        historical_accuracy: float = None,
        data_quality: float = 1.0,
        model_age_days: int = 0
    ) -> Dict[str, float]:
        """Calculate confidence for predictions.
        
        Args:
            predictions: Array of predictions
            historical_accuracy: Historical model accuracy (0-1)
            data_quality: Quality of input data (0-1)
            model_age_days: Days since model was trained
            
        Returns:
            Dictionary with confidence metrics
        """
        # Base confidence from historical accuracy
        if historical_accuracy is not None:
            base_confidence = historical_accuracy
        else:
            base_confidence = 0.5
        
        # Adjust for data quality
        quality_factor = data_quality
        
        # Adjust for model age (decay over time)
        age_factor = max(0.5, 1.0 - (model_age_days / 365.0))
        
        # Calculate prediction variance (lower variance = higher confidence)
        if len(predictions) > 1:
            variance = np.var(predictions)
            variance_factor = 1.0 / (1.0 + variance)
        else:
            variance_factor = 1.0
        
        # Combined confidence
        confidence = base_confidence * quality_factor * age_factor * variance_factor
        confidence = np.clip(confidence, 0.0, 1.0)
        
        return {
            "overall_confidence": float(confidence),
            "base_confidence": float(base_confidence),
            "quality_factor": float(quality_factor),
            "age_factor": float(age_factor),
            "variance_factor": float(variance_factor)
        }
    
    @staticmethod
    def calculate_anomaly_confidence(
        anomaly_score: float,
        baseline_confidence: float,
        historical_false_positive_rate: float = 0.05
    ) -> Dict[str, float]:
        """Calculate confidence for anomaly detection.
        
        Args:
            anomaly_score: Anomaly score from detector
            baseline_confidence: Confidence in baseline
            historical_false_positive_rate: Historical FP rate
            
        Returns:
            Dictionary with confidence metrics
        """
        # Normalize anomaly score to 0-1 range
        normalized_score = abs(anomaly_score)
        if normalized_score > 1.0:
            normalized_score = 1.0 / (1.0 + normalized_score)
        
        # Adjust for baseline confidence
        baseline_factor = baseline_confidence
        
        # Adjust for historical false positives
        fp_factor = 1.0 - historical_false_positive_rate
        
        # Combined confidence
        confidence = normalized_score * baseline_factor * fp_factor
        confidence = np.clip(confidence, 0.0, 1.0)
        
        return {
            "overall_confidence": float(confidence),
            "anomaly_strength": float(normalized_score),
            "baseline_factor": float(baseline_factor),
            "fp_adjustment": float(fp_factor)
        }
    
    @staticmethod
    def calculate_pattern_match_confidence(
        similarity_score: float,
        pattern_occurrence_count: int,
        pattern_confidence: float
    ) -> float:
        """Calculate confidence for pattern matching.
        
        Args:
            similarity_score: Similarity to pattern (0-1)
            pattern_occurrence_count: How many times pattern was observed
            pattern_confidence: Confidence in the pattern itself
            
        Returns:
            Overall confidence score
        """
        # Base confidence from similarity
        base = similarity_score
        
        # Boost from occurrence count (more observations = higher confidence)
        occurrence_factor = min(1.0, pattern_occurrence_count / 100.0)
        
        # Pattern's own confidence
        pattern_factor = pattern_confidence
        
        # Combined confidence
        confidence = base * (0.5 + 0.5 * occurrence_factor) * pattern_factor
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    @staticmethod
    def get_confidence_level(confidence: float) -> str:
        """Get human-readable confidence level.
        
        Args:
            confidence: Confidence score (0-1)
            
        Returns:
            Confidence level string
        """
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= 0.75:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        elif confidence >= 0.4:
            return "low"
        else:
            return "very_low"
    
    @staticmethod
    def should_trust_prediction(
        confidence: float,
        threshold: float = 0.7
    ) -> bool:
        """Determine if prediction should be trusted.
        
        Args:
            confidence: Confidence score
            threshold: Minimum confidence threshold
            
        Returns:
            True if prediction should be trusted
        """
        return confidence >= threshold
