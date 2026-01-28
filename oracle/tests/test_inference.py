"""Tests for inference engine."""
import pytest
import numpy as np

from inference.confidence_calculator import ConfidenceCalculator
from inference.explainer import ModelExplainer


class TestConfidenceCalculator:
    """Test confidence calculator."""
    
    def test_prediction_confidence(self):
        """Test prediction confidence calculation."""
        predictions = np.array([45.0, 46.0, 44.0, 45.5])
        
        confidence = ConfidenceCalculator.calculate_prediction_confidence(
            predictions,
            historical_accuracy=0.85,
            data_quality=0.9,
            model_age_days=10
        )
        
        assert 0.0 <= confidence["overall_confidence"] <= 1.0
        assert "base_confidence" in confidence
        assert "quality_factor" in confidence
    
    def test_anomaly_confidence(self):
        """Test anomaly confidence calculation."""
        confidence = ConfidenceCalculator.calculate_anomaly_confidence(
            anomaly_score=-0.5,
            baseline_confidence=0.8,
            historical_false_positive_rate=0.05
        )
        
        assert 0.0 <= confidence["overall_confidence"] <= 1.0
        assert "anomaly_strength" in confidence
    
    def test_pattern_match_confidence(self):
        """Test pattern match confidence."""
        confidence = ConfidenceCalculator.calculate_pattern_match_confidence(
            similarity_score=0.85,
            pattern_occurrence_count=50,
            pattern_confidence=0.9
        )
        
        assert 0.0 <= confidence <= 1.0
    
    def test_confidence_level(self):
        """Test confidence level categorization."""
        assert ConfidenceCalculator.get_confidence_level(0.95) == "very_high"
        assert ConfidenceCalculator.get_confidence_level(0.80) == "high"
        assert ConfidenceCalculator.get_confidence_level(0.65) == "medium"
        assert ConfidenceCalculator.get_confidence_level(0.45) == "low"
        assert ConfidenceCalculator.get_confidence_level(0.30) == "very_low"
    
    def test_should_trust_prediction(self):
        """Test prediction trust decision."""
        assert ConfidenceCalculator.should_trust_prediction(0.8, threshold=0.7)
        assert not ConfidenceCalculator.should_trust_prediction(0.6, threshold=0.7)


class TestModelExplainer:
    """Test model explainer."""
    
    def test_explain_prediction(self):
        """Test prediction explanation."""
        explanation = ModelExplainer.explain_prediction(
            prediction=55.0,
            baseline=50.0,
            features={"cpu": 45.0, "ram": 60.0}
        )
        
        assert "prediction" in explanation
        assert "baseline" in explanation
        assert "deviation" in explanation
        assert "direction" in explanation
        assert "summary" in explanation
    
    def test_explain_anomaly(self):
        """Test anomaly explanation."""
        explanation = ModelExplainer.explain_anomaly(
            anomaly_score=-0.8,
            current_value=150.0,
            baseline=50.0,
            std_deviation=10.0
        )
        
        assert "is_anomaly" in explanation
        assert "severity" in explanation
        assert "std_deviations" in explanation
        assert "summary" in explanation
    
    def test_explain_pattern_match(self):
        """Test pattern match explanation."""
        explanation = ModelExplainer.explain_pattern_match(
            pattern_name="work_mode",
            similarity=0.85,
            matched_features={"cpu": 45.0, "ram": 60.0}
        )
        
        assert "pattern_name" in explanation
        assert "similarity" in explanation
        assert "match_quality" in explanation
        assert "summary" in explanation
    
    def test_explain_cluster_assignment(self):
        """Test cluster assignment explanation."""
        explanation = ModelExplainer.explain_cluster_assignment(
            cluster_id=2,
            cluster_label="heavy_work",
            distance_to_center=0.3
        )
        
        assert "cluster_id" in explanation
        assert "cluster_label" in explanation
        assert "fit_quality" in explanation
        assert "summary" in explanation
    
    def test_anomaly_severity(self):
        """Test anomaly severity classification."""
        assert ModelExplainer._get_anomaly_severity(5.5) == "critical"
        assert ModelExplainer._get_anomaly_severity(4.2) == "high"
        assert ModelExplainer._get_anomaly_severity(3.5) == "medium"
        assert ModelExplainer._get_anomaly_severity(2.0) == "low"
