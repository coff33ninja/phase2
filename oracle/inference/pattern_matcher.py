"""Pattern matching for current system state."""
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

from patterns.usage_patterns import UsagePatternStore
from patterns.baseline_manager import BaselineManager


class PatternMatcher:
    """Match current system state to learned patterns."""
    
    def __init__(self, pattern_db_path: Path):
        """Initialize pattern matcher.
        
        Args:
            pattern_db_path: Path to pattern database
        """
        self.pattern_store = UsagePatternStore(pattern_db_path)
        self.baseline_manager = BaselineManager(pattern_db_path)
    
    def match_current_state(
        self,
        current_metrics: Dict[str, float],
        time_context: str = None
    ) -> List[Dict]:
        """Match current state to known patterns.
        
        Args:
            current_metrics: Current system metrics
            time_context: Optional time context
            
        Returns:
            List of matching patterns with similarity scores
        """
        if time_context is None:
            time_context = self.baseline_manager.get_time_context()
        
        # Get patterns for current time context
        patterns = self.pattern_store.get_patterns_by_time(time_context)
        
        if not patterns:
            logger.warning(f"No patterns found for {time_context}")
            return []
        
        # Calculate similarity scores
        matches = []
        for pattern in patterns:
            similarity = self._calculate_similarity(
                current_metrics,
                pattern['data']
            )
            
            if similarity > 0.5:  # Threshold for matching
                matches.append({
                    "pattern_type": pattern['pattern_type'],
                    "similarity": similarity,
                    "confidence": pattern['confidence'],
                    "pattern_data": pattern['data']
                })
        
        # Sort by similarity
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matches
    
    def _calculate_similarity(
        self,
        current: Dict[str, float],
        pattern: Dict
    ) -> float:
        """Calculate similarity between current state and pattern.
        
        Args:
            current: Current metrics
            pattern: Pattern data
            
        Returns:
            Similarity score (0-1)
        """
        # Extract common keys
        common_keys = set(current.keys()) & set(pattern.keys())
        
        if not common_keys:
            return 0.0
        
        # Create vectors
        current_vec = np.array([current[k] for k in common_keys])
        pattern_vec = np.array([pattern[k] for k in common_keys])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(
            current_vec.reshape(1, -1),
            pattern_vec.reshape(1, -1)
        )[0][0]
        
        return float(similarity)
    
    def identify_activity(
        self,
        current_metrics: Dict[str, float]
    ) -> Optional[str]:
        """Identify current activity based on metrics.
        
        Args:
            current_metrics: Current system metrics
            
        Returns:
            Activity name or None
        """
        matches = self.match_current_state(current_metrics)
        
        if not matches:
            return None
        
        # Return best match if confidence is high enough
        best_match = matches[0]
        if best_match['similarity'] > 0.7 and best_match['confidence'] > 0.6:
            return best_match['pattern_type']
        
        return None
    
    def check_baseline_deviation(
        self,
        metric_name: str,
        value: float,
        time_context: str = None
    ) -> Dict:
        """Check if value deviates from baseline.
        
        Args:
            metric_name: Name of the metric
            value: Current value
            time_context: Optional time context
            
        Returns:
            Dictionary with deviation information
        """
        if time_context is None:
            time_context = self.baseline_manager.get_time_context()
        
        baseline = self.baseline_manager.get_baseline(metric_name, time_context)
        
        if not baseline:
            return {
                "has_baseline": False,
                "is_anomaly": False,
                "deviation": 0.0
            }
        
        deviation = abs(value - baseline['baseline'])
        std_devs = deviation / baseline['std_deviation'] if baseline['std_deviation'] > 0 else 0
        is_anomaly = self.baseline_manager.is_anomaly(metric_name, time_context, value)
        
        return {
            "has_baseline": True,
            "baseline_value": baseline['baseline'],
            "current_value": value,
            "deviation": deviation,
            "std_deviations": std_devs,
            "is_anomaly": is_anomaly,
            "confidence": baseline['confidence']
        }
    
    def get_expected_metrics(
        self,
        time_context: str = None
    ) -> Dict[str, tuple]:
        """Get expected metric ranges for time context.
        
        Args:
            time_context: Optional time context
            
        Returns:
            Dictionary of metric names to (min, max) ranges
        """
        if time_context is None:
            time_context = self.baseline_manager.get_time_context()
        
        patterns = self.pattern_store.get_patterns_by_time(time_context)
        
        expected = {}
        for pattern in patterns:
            metric_name = pattern['pattern_type']
            range_val = self.baseline_manager.get_expected_range(
                metric_name,
                time_context
            )
            if range_val:
                expected[metric_name] = range_val
        
        return expected
