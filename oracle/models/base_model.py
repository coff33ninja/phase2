"""Base class for all ML models."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
import joblib
from loguru import logger


class BaseModel(ABC):
    """Abstract base class for all machine learning models."""
    
    def __init__(self, model_name: str, model_dir: Path):
        """Initialize base model.
        
        Args:
            model_name: Name of the model
            model_dir: Directory to save/load models
        """
        self.model_name = model_name
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model: Optional[Any] = None
        self.is_trained = False
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def train(self, X, y, **kwargs):
        """Train the model.
        
        Args:
            X: Training features
            y: Training targets
            **kwargs: Additional training parameters
        """
        pass
    
    @abstractmethod
    def predict(self, X, **kwargs):
        """Make predictions.
        
        Args:
            X: Input features
            **kwargs: Additional prediction parameters
            
        Returns:
            Predictions
        """
        pass
    
    @abstractmethod
    def evaluate(self, X, y, **kwargs) -> Dict[str, float]:
        """Evaluate model performance.
        
        Args:
            X: Test features
            y: Test targets
            **kwargs: Additional evaluation parameters
            
        Returns:
            Dictionary of evaluation metrics
        """
        pass
    
    def save(self, filename: Optional[str] = None) -> Path:
        """Save model to disk.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved model
        """
        if filename is None:
            filename = f"{self.model_name}.joblib"
        
        filepath = self.model_dir / filename
        
        save_data = {
            "model": self.model,
            "metadata": self.metadata,
            "is_trained": self.is_trained
        }
        
        joblib.dump(save_data, filepath)
        logger.info(f"Model saved to {filepath}")
        return filepath
    
    def load(self, filename: Optional[str] = None) -> bool:
        """Load model from disk.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            True if successful, False otherwise
        """
        if filename is None:
            filename = f"{self.model_name}.joblib"
        
        filepath = self.model_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Model file not found: {filepath}")
            return False
        
        try:
            save_data = joblib.load(filepath)
            self.model = save_data["model"]
            self.metadata = save_data["metadata"]
            self.is_trained = save_data["is_trained"]
            logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata.
        
        Returns:
            Dictionary of metadata
        """
        return self.metadata.copy()
    
    def update_metadata(self, **kwargs):
        """Update model metadata.
        
        Args:
            **kwargs: Metadata key-value pairs
        """
        self.metadata.update(kwargs)
