"""Real-time prediction engine."""
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from loguru import logger

from models.lstm_forecaster import LSTMForecaster
from models.anomaly_detector import IsolationForestDetector


class Predictor:
    """Real-time prediction and inference engine."""
    
    def __init__(self, model_dir: Path):
        """Initialize predictor.
        
        Args:
            model_dir: Directory containing saved models
        """
        self.model_dir = Path(model_dir)
        self.forecaster: Optional[LSTMForecaster] = None
        self.anomaly_detector: Optional[IsolationForestDetector] = None
    
    def load_models(self):
        """Load all trained models."""
        logger.info("Loading models")
        
        self.forecaster = LSTMForecaster(self.model_dir)
        if not self.forecaster.load():
            logger.warning("LSTM forecaster not loaded")
        
        self.anomaly_detector = IsolationForestDetector(self.model_dir)
        if not self.anomaly_detector.load():
            logger.warning("Anomaly detector not loaded")
    
    def predict_future(
        self,
        current_sequence: np.ndarray
    ) -> Dict[str, float]:
        """Predict future resource usage.
        
        Args:
            current_sequence: Recent time series data
            
        Returns:
            Dictionary of predictions
        """
        if self.forecaster is None or not self.forecaster.is_trained:
            raise ValueError("Forecaster not loaded")
        
        predictions = self.forecaster.predict(current_sequence[np.newaxis, :])[0]
        
        result = {}
        for i, horizon in enumerate(self.forecaster.prediction_horizons):
            result[f"cpu_{horizon}m"] = float(predictions[i])
        
        return result
    
    def detect_anomaly(
        self,
        current_features: np.ndarray
    ) -> Dict[str, any]:
        """Detect if current state is anomalous.
        
        Args:
            current_features: Current system features
            
        Returns:
            Dictionary with anomaly information
        """
        if self.anomaly_detector is None or not self.anomaly_detector.is_trained:
            raise ValueError("Anomaly detector not loaded")
        
        score = self.anomaly_detector.score_samples(current_features[np.newaxis, :])[0]
        is_anomaly = self.anomaly_detector.predict(current_features[np.newaxis, :])[0] == -1
        
        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": float(score),
            "severity": "high" if score < -0.5 else "medium" if score < 0 else "low"
        }
