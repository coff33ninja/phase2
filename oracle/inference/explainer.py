"""Model decision explainer."""
from typing import Dict, List
import numpy as np
from loguru import logger


class ModelExplainer:
    """Explain model predictions and decisions."""
    
    @staticmethod
    def explain_prediction(
        prediction: float,
        baseline: float,
        features: Dict[str, float],
        feature_importance: Dict[str, float] = None
    ) -> Dict:
        """Explain a prediction.
        
        Args:
            prediction: Predicted value
            baseline: Baseline value
            features: Input features
            feature_importance: Feature importance scores
            
        Returns:
            Explanation dictionary
        """
        deviation = prediction - baseline
        deviation_pct = (deviation / baseline * 100) if baseline != 0 else 0
        
        explanation = {
            "prediction": float(prediction),
            "baseline": float(baseline),
            "deviation": float(deviation),
            "deviation_percent": float(deviation_pct),
            "direction": "increase" if deviation > 0 else "decrease" if deviation < 0 else "stable",
            "magnitude": "large" if abs(deviation_pct) > 20 else "moderate" if abs(deviation_pct) > 10 else "small"
        }
        
        # Add feature contributions if available
        if feature_importance:
            top_features = sorted(
                feature_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:5]
            
            explanation["top_contributing_features"] = [
                {
                    "feature": feat,
                    "importance": float(imp),
                    "value": float(features.get(feat, 0))
                }
                for feat, imp in top_features
            ]
        
        # Generate human-readable explanation
        explanation["summary"] = ModelExplainer._generate_summary(explanation)
        
        return explanation
    
    @staticmethod
    def explain_anomaly(
        anomaly_score: float,
        current_value: float,
        baseline: float,
        std_deviation: float,
        contributing_factors: List[str] = None
    ) -> Dict:
        """Explain an anomaly detection.
        
        Args:
            anomaly_score: Anomaly score
            current_value: Current metric value
            baseline: Expected baseline value
            std_deviation: Standard deviation
            contributing_factors: List of contributing factors
            
        Returns:
            Explanation dictionary
        """
        deviation = current_value - baseline
        std_devs = deviation / std_deviation if std_deviation > 0 else 0
        
        explanation = {
            "is_anomaly": abs(std_devs) > 3.0,
            "anomaly_score": float(anomaly_score),
            "current_value": float(current_value),
            "expected_value": float(baseline),
            "deviation": float(deviation),
            "std_deviations": float(std_devs),
            "severity": ModelExplainer._get_anomaly_severity(abs(std_devs))
        }
        
        if contributing_factors:
            explanation["contributing_factors"] = contributing_factors
        
        explanation["summary"] = ModelExplainer._generate_anomaly_summary(explanation)
        
        return explanation
    
    @staticmethod
    def explain_pattern_match(
        pattern_name: str,
        similarity: float,
        matched_features: Dict[str, float],
        pattern_description: str = None
    ) -> Dict:
        """Explain a pattern match.
        
        Args:
            pattern_name: Name of matched pattern
            similarity: Similarity score
            matched_features: Features that matched
            pattern_description: Optional pattern description
            
        Returns:
            Explanation dictionary
        """
        explanation = {
            "pattern_name": pattern_name,
            "similarity": float(similarity),
            "match_quality": "excellent" if similarity > 0.9 else "good" if similarity > 0.75 else "fair",
            "matched_features": {k: float(v) for k, v in matched_features.items()}
        }
        
        if pattern_description:
            explanation["description"] = pattern_description
        
        explanation["summary"] = f"Current state matches '{pattern_name}' pattern with {similarity*100:.1f}% similarity"
        
        return explanation
    
    @staticmethod
    def explain_cluster_assignment(
        cluster_id: int,
        cluster_label: str,
        distance_to_center: float,
        cluster_characteristics: Dict = None
    ) -> Dict:
        """Explain cluster assignment.
        
        Args:
            cluster_id: Cluster ID
            cluster_label: Human-readable cluster label
            distance_to_center: Distance to cluster center
            cluster_characteristics: Cluster characteristics
            
        Returns:
            Explanation dictionary
        """
        explanation = {
            "cluster_id": cluster_id,
            "cluster_label": cluster_label,
            "distance_to_center": float(distance_to_center),
            "fit_quality": "tight" if distance_to_center < 0.5 else "moderate" if distance_to_center < 1.0 else "loose"
        }
        
        if cluster_characteristics:
            explanation["characteristics"] = cluster_characteristics
        
        explanation["summary"] = f"System state classified as '{cluster_label}' (cluster {cluster_id})"
        
        return explanation
    
    @staticmethod
    def _generate_summary(explanation: Dict) -> str:
        """Generate human-readable summary.
        
        Args:
            explanation: Explanation dictionary
            
        Returns:
            Summary string
        """
        pred = explanation["prediction"]
        base = explanation["baseline"]
        direction = explanation["direction"]
        magnitude = explanation["magnitude"]
        
        if direction == "stable":
            return f"Prediction ({pred:.1f}) is stable, close to baseline ({base:.1f})"
        else:
            return f"Prediction ({pred:.1f}) shows {magnitude} {direction} from baseline ({base:.1f})"
    
    @staticmethod
    def _generate_anomaly_summary(explanation: Dict) -> str:
        """Generate anomaly summary.
        
        Args:
            explanation: Explanation dictionary
            
        Returns:
            Summary string
        """
        if not explanation["is_anomaly"]:
            return "No anomaly detected - value within normal range"
        
        severity = explanation["severity"]
        current = explanation["current_value"]
        expected = explanation["expected_value"]
        std_devs = explanation["std_deviations"]
        
        return f"{severity.capitalize()} anomaly detected: {current:.1f} vs expected {expected:.1f} ({abs(std_devs):.1f} std devs)"
    
    @staticmethod
    def _get_anomaly_severity(std_devs: float) -> str:
        """Get anomaly severity level.
        
        Args:
            std_devs: Number of standard deviations
            
        Returns:
            Severity level
        """
        if std_devs >= 5.0:
            return "critical"
        elif std_devs >= 4.0:
            return "high"
        elif std_devs >= 3.0:
            return "medium"
        else:
            return "low"
