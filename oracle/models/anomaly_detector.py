"""Isolation Forest for anomaly detection."""
from pathlib import Path
from typing import Dict
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support
from loguru import logger

from models.base_model import BaseModel


class IsolationForestDetector(BaseModel):
    """Isolation Forest for detecting anomalous system behavior."""
    
    def __init__(
        self,
        model_dir: Path,
        contamination: float = 0.1,
        n_estimators: int = 100
    ):
        """Initialize Isolation Forest detector.
        
        Args:
            model_dir: Directory to save/load models
            contamination: Expected proportion of anomalies
            n_estimators: Number of trees
        """
        super().__init__("isolation_forest_detector", model_dir)
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42,
            n_jobs=-1
        )
    
    def train(self, X: np.ndarray, y=None, **kwargs):
        """Train Isolation Forest.
        
        Args:
            X: Training features (samples, features)
            y: Not used (unsupervised)
            **kwargs: Additional training parameters
        """
        logger.info(f"Training Isolation Forest with {len(X)} samples")
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model
        self.model.fit(X_scaled)
        
        self.is_trained = True
        
        # Calculate anomaly scores
        scores = self.model.score_samples(X_scaled)
        n_anomalies = np.sum(self.model.predict(X_scaled) == -1)
        
        self.update_metadata(
            training_samples=len(X),
            detected_anomalies=int(n_anomalies),
            anomaly_rate=float(n_anomalies / len(X)),
            score_mean=float(np.mean(scores)),
            score_std=float(np.std(scores))
        )
        
        logger.info(f"Training complete. Detected {n_anomalies} anomalies")
    
    def predict(self, X: np.ndarray, **kwargs) -> np.ndarray:
        """Predict anomaly labels.
        
        Args:
            X: Input features (samples, features)
            **kwargs: Additional prediction parameters
            
        Returns:
            Anomaly labels (1 for normal, -1 for anomaly)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        return predictions
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Calculate anomaly scores.
        
        Args:
            X: Input features (samples, features)
            
        Returns:
            Anomaly scores (lower = more anomalous)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before scoring")
        
        X_scaled = self.scaler.transform(X)
        scores = self.model.score_samples(X_scaled)
        return scores
    
    def evaluate(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, float]:
        """Evaluate anomaly detection performance.
        
        Args:
            X: Test features
            y: True labels (1 for normal, -1 for anomaly)
            **kwargs: Additional evaluation parameters
            
        Returns:
            Dictionary of evaluation metrics
        """
        predictions = self.predict(X)
        scores = self.score_samples(X)
        
        # Convert labels to binary (0 for normal, 1 for anomaly)
        y_binary = (y == -1).astype(int)
        pred_binary = (predictions == -1).astype(int)
        
        # Calculate metrics
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_binary, pred_binary, average='binary'
        )
        
        # Calculate AUC if possible
        try:
            auc = roc_auc_score(y_binary, -scores)  # Negative scores for AUC
        except ValueError:
            auc = 0.0
        
        metrics = {
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "auc": float(auc),
            "detected_anomalies": int(np.sum(pred_binary))
        }
        
        return metrics
    
    def get_anomaly_threshold(self, percentile: float = 95) -> float:
        """Get anomaly score threshold.
        
        Args:
            percentile: Percentile for threshold
            
        Returns:
            Anomaly score threshold
        """
        if "score_mean" not in self.metadata:
            raise ValueError("Model must be trained first")
        
        # Estimate threshold from training statistics
        mean = self.metadata["score_mean"]
        std = self.metadata["score_std"]
        
        # Use z-score approximation
        z_score = (percentile - 50) / 50 * 3  # Rough approximation
        threshold = mean - z_score * std
        
        return threshold
    
    def is_anomaly(self, X: np.ndarray, threshold: float = None) -> np.ndarray:
        """Check if samples are anomalies.
        
        Args:
            X: Input features
            threshold: Custom threshold (if None, use model default)
            
        Returns:
            Boolean array (True for anomaly)
        """
        if threshold is None:
            predictions = self.predict(X)
            return predictions == -1
        else:
            scores = self.score_samples(X)
            return scores < threshold
