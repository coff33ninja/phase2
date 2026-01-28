"""Model training orchestration."""
from pathlib import Path
from typing import Dict, Any
import numpy as np
from sklearn.model_selection import train_test_split
from loguru import logger

from models.base_model import BaseModel


class ModelTrainer:
    """Orchestrate model training pipeline."""
    
    def __init__(self, model: BaseModel):
        """Initialize trainer.
        
        Args:
            model: Model to train
        """
        self.model = model
        self.training_history: Dict[str, Any] = {}
    
    def train_test_split(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        random_state: int = 42
    ):
        """Split data into train and test sets.
        
        Args:
            X: Features
            y: Targets
            test_size: Fraction for test set
            random_state: Random seed
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        return train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            shuffle=False
        )
    
    def train_and_evaluate(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        **train_kwargs
    ) -> Dict[str, float]:
        """Train model and evaluate performance.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_test: Test features
            y_test: Test targets
            **train_kwargs: Additional training parameters
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info(f"Training {self.model.model_name}")
        
        self.model.train(X_train, y_train, **train_kwargs)
        
        logger.info("Evaluating model")
        metrics = self.model.evaluate(X_test, y_test)
        
        self.training_history = {
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "metrics": metrics
        }
        
        logger.info(f"Training complete. Metrics: {metrics}")
        
        return metrics
    
    def save_model(self, filename: str = None) -> Path:
        """Save trained model.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved model
        """
        return self.model.save(filename)
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get training summary.
        
        Returns:
            Dictionary with training information
        """
        return {
            "model_name": self.model.model_name,
            "is_trained": self.model.is_trained,
            "metadata": self.model.get_metadata(),
            "history": self.training_history
        }
