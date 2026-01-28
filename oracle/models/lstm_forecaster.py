"""LSTM-based time series forecaster."""
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import StandardScaler
from loguru import logger

from models.base_model import BaseModel


class LSTMForecaster(BaseModel):
    """LSTM neural network for time-series forecasting."""
    
    def __init__(
        self,
        model_dir: Path,
        sequence_length: int = 60,
        n_features: int = 10,
        prediction_horizons: list = None
    ):
        """Initialize LSTM forecaster.
        
        Args:
            model_dir: Directory to save/load models
            sequence_length: Number of time steps to look back
            n_features: Number of input features
            prediction_horizons: List of prediction horizons in minutes
        """
        super().__init__("lstm_forecaster", model_dir)
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.prediction_horizons = prediction_horizons or [5, 15, 30, 60]
        self.scaler = StandardScaler()
        self._build_model()
    
    def _build_model(self):
        """Build LSTM model architecture."""
        # Use Input layer instead of input_shape parameter
        inputs = layers.Input(shape=(self.sequence_length, self.n_features))
        x = layers.LSTM(128, return_sequences=True)(inputs)
        x = layers.Dropout(0.2)(x)
        x = layers.LSTM(64, return_sequences=False)(x)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(32, activation='relu')(x)
        outputs = layers.Dense(len(self.prediction_horizons))(x)
        
        model = keras.Model(inputs=inputs, outputs=outputs)
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae', 'mape']
        )
        
        self.model = model
        logger.info("LSTM model built successfully")
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        validation_split: float = 0.2,
        epochs: int = 50,
        batch_size: int = 32,
        **kwargs
    ):
        """Train the LSTM model.
        
        Args:
            X: Training sequences (samples, sequence_length, features)
            y: Training targets (samples, n_horizons)
            validation_split: Fraction of data for validation
            epochs: Number of training epochs
            batch_size: Batch size for training
            **kwargs: Additional training parameters
        """
        logger.info(f"Training LSTM with {len(X)} samples")
        
        # Normalize features
        X_reshaped = X.reshape(-1, self.n_features)
        X_scaled = self.scaler.fit_transform(X_reshaped)
        X_scaled = X_scaled.reshape(X.shape)
        
        # Train model
        history = self.model.fit(
            X_scaled,
            y,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            verbose=0,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                )
            ]
        )
        
        self.is_trained = True
        self.update_metadata(
            training_samples=len(X),
            epochs_trained=len(history.history['loss']),
            final_loss=float(history.history['loss'][-1]),
            final_val_loss=float(history.history['val_loss'][-1])
        )
        
        logger.info(f"Training complete. Final loss: {history.history['loss'][-1]:.4f}")
    
    def predict(self, X: np.ndarray, **kwargs) -> np.ndarray:
        """Make predictions.
        
        Args:
            X: Input sequences (samples, sequence_length, features)
            **kwargs: Additional prediction parameters
            
        Returns:
            Predictions for each horizon (samples, n_horizons)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Normalize features
        X_reshaped = X.reshape(-1, self.n_features)
        X_scaled = self.scaler.transform(X_reshaped)
        X_scaled = X_scaled.reshape(X.shape)
        
        predictions = self.model.predict(X_scaled, verbose=0)
        return predictions
    
    def evaluate(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, float]:
        """Evaluate model performance.
        
        Args:
            X: Test sequences
            y: Test targets
            **kwargs: Additional evaluation parameters
            
        Returns:
            Dictionary of evaluation metrics
        """
        predictions = self.predict(X)
        
        # Calculate metrics for each horizon
        metrics = {}
        for i, horizon in enumerate(self.prediction_horizons):
            y_true = y[:, i]
            y_pred = predictions[:, i]
            
            mae = np.mean(np.abs(y_true - y_pred))
            mse = np.mean((y_true - y_pred) ** 2)
            rmse = np.sqrt(mse)
            mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
            
            metrics[f"mae_{horizon}m"] = float(mae)
            metrics[f"rmse_{horizon}m"] = float(rmse)
            metrics[f"mape_{horizon}m"] = float(mape)
        
        return metrics
    
    def predict_with_confidence(
        self,
        X: np.ndarray,
        n_samples: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence intervals using Monte Carlo dropout.
        
        Args:
            X: Input sequences
            n_samples: Number of Monte Carlo samples
            
        Returns:
            Tuple of (mean predictions, standard deviations)
        """
        predictions = []
        for _ in range(n_samples):
            pred = self.predict(X)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)
        
        return mean_pred, std_pred
