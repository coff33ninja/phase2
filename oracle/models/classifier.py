"""Random Forest classifier for activity categorization."""
from pathlib import Path
from typing import Dict, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier as SKRandomForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from loguru import logger

from models.base_model import BaseModel


class RandomForestClassifier(BaseModel):
    """Random Forest for categorizing processes and activities."""
    
    def __init__(
        self,
        model_dir: Path,
        n_estimators: int = 100,
        max_depth: int = 20
    ):
        """Initialize Random Forest classifier.
        
        Args:
            model_dir: Directory to save/load models
            n_estimators: Number of trees
            max_depth: Maximum tree depth
        """
        super().__init__("random_forest_classifier", model_dir)
        self.scaler = StandardScaler()
        self.model = SKRandomForest(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )
        self.class_names: List[str] = []
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        class_names: List[str] = None,
        **kwargs
    ):
        """Train Random Forest classifier.
        
        Args:
            X: Training features (samples, features)
            y: Training labels (samples,)
            class_names: List of class names
            **kwargs: Additional training parameters
        """
        logger.info(f"Training Random Forest with {len(X)} samples")
        
        if class_names:
            self.class_names = class_names
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        self.is_trained = True
        
        # Calculate training accuracy
        train_pred = self.model.predict(X_scaled)
        train_acc = accuracy_score(y, train_pred)
        
        self.update_metadata(
            training_samples=len(X),
            n_classes=len(np.unique(y)),
            class_names=self.class_names,
            train_accuracy=float(train_acc),
            feature_importances=self.model.feature_importances_.tolist()
        )
        
        logger.info(f"Training complete. Accuracy: {train_acc:.4f}")
    
    def predict(self, X: np.ndarray, **kwargs) -> np.ndarray:
        """Predict class labels.
        
        Args:
            X: Input features (samples, features)
            **kwargs: Additional prediction parameters
            
        Returns:
            Predicted labels (samples,)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        return predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities.
        
        Args:
            X: Input features (samples, features)
            
        Returns:
            Class probabilities (samples, n_classes)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        probabilities = self.model.predict_proba(X_scaled)
        return probabilities
    
    def evaluate(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, float]:
        """Evaluate classifier performance.
        
        Args:
            X: Test features
            y: Test labels
            **kwargs: Additional evaluation parameters
            
        Returns:
            Dictionary of evaluation metrics
        """
        predictions = self.predict(X)
        
        accuracy = accuracy_score(y, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y, predictions, average='weighted'
        )
        
        metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1)
        }
        
        return metrics
    
    def get_feature_importance(self) -> np.ndarray:
        """Get feature importances.
        
        Returns:
            Feature importances (n_features,)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        return self.model.feature_importances_
    
    def get_class_name(self, class_id: int) -> str:
        """Get class name from ID.
        
        Args:
            class_id: Class ID
            
        Returns:
            Class name
        """
        if class_id < len(self.class_names):
            return self.class_names[class_id]
        return f"class_{class_id}"
