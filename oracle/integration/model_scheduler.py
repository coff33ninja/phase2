"""Scheduler for automatic model updates."""
import schedule
import time
from pathlib import Path
from datetime import datetime
from loguru import logger

from training.data_loader import SentinelDataLoader
from training.feature_engineering import FeatureEngineer
from training.trainer import ModelTrainer
from models.lstm_forecaster import LSTMForecaster
from models.anomaly_detector import IsolationForestDetector
from config import config


class ModelScheduler:
    """Schedule automatic model training and updates."""
    
    def __init__(
        self,
        sentinel_db_path: Path,
        model_dir: Path,
        update_interval_hours: int = 24
    ):
        """Initialize model scheduler.
        
        Args:
            sentinel_db_path: Path to Sentinel database
            model_dir: Directory for models
            update_interval_hours: Hours between updates
        """
        self.sentinel_db_path = Path(sentinel_db_path)
        self.model_dir = Path(model_dir)
        self.update_interval_hours = update_interval_hours
        self.is_running = False
        self.last_update = None
    
    def schedule_updates(self):
        """Schedule automatic model updates."""
        schedule.every(self.update_interval_hours).hours.do(self._update_models)
        logger.info(f"Scheduled model updates every {self.update_interval_hours} hours")
    
    def _update_models(self):
        """Update all models with latest data."""
        logger.info("Starting scheduled model update")
        
        try:
            # Load data
            loader = SentinelDataLoader(self.sentinel_db_path)
            stats = loader.get_statistics()
            
            if stats['total_samples'] < config.min_training_samples:
                logger.warning(f"Not enough data for training: {stats['total_samples']}")
                return
            
            df = loader.load_time_series(days=config.training_window_days)
            df = FeatureEngineer.create_all_features(df)
            
            logger.info(f"Loaded {len(df)} samples for training")
            
            # Update LSTM
            self._update_lstm(loader, df)
            
            # Update Anomaly Detector
            self._update_anomaly_detector(df)
            
            self.last_update = datetime.now()
            logger.info("Model update complete")
            
        except Exception as e:
            logger.error(f"Model update failed: {e}")
    
    def _update_lstm(self, loader, df):
        """Update LSTM model."""
        try:
            X, y = loader.create_sequences(
                df[['cpu_percent', 'ram_percent']].values,
                sequence_length=60
            )
            
            model = LSTMForecaster(
                self.model_dir,
                sequence_length=60,
                n_features=2
            )
            
            trainer = ModelTrainer(model)
            X_train, X_test, y_train, y_test = trainer.train_test_split(X, y)
            
            metrics = trainer.train_and_evaluate(
                X_train, y_train, X_test, y_test,
                epochs=config.epochs,
                batch_size=config.batch_size
            )
            
            trainer.save_model()
            logger.info(f"LSTM updated. MAE: {metrics.get('mae_5m', 0):.2f}")
            
        except Exception as e:
            logger.error(f"LSTM update failed: {e}")
    
    def _update_anomaly_detector(self, df):
        """Update anomaly detector."""
        try:
            features = df[['cpu_percent', 'ram_percent']].values
            
            model = IsolationForestDetector(
                self.model_dir,
                contamination=config.anomaly_contamination
            )
            
            model.train(features)
            model.save()
            
            logger.info("Anomaly detector updated")
            
        except Exception as e:
            logger.error(f"Anomaly detector update failed: {e}")
    
    def run(self):
        """Run the scheduler."""
        self.is_running = True
        logger.info("Model scheduler started")
        
        # Check if models exist, if not and we have enough data, train immediately
        models_exist = self._check_models_exist()
        if not models_exist:
            logger.info("No trained models found, checking if we can train...")
            loader = SentinelDataLoader(self.sentinel_db_path)
            stats = loader.get_statistics()
            
            if stats['total_samples'] >= config.min_training_samples:
                logger.info(f"Found {stats['total_samples']} samples, starting initial training...")
                self._update_models()
            else:
                logger.info(f"Need {config.min_training_samples - stats['total_samples']} more samples before training")
        else:
            logger.info("Models already trained, running scheduled updates")
            # Run update to refresh with latest data
            self._update_models()
        
        # Start scheduled updates
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _check_models_exist(self) -> bool:
        """Check if trained models exist.
        
        Returns:
            True if models exist, False otherwise
        """
        lstm_model = self.model_dir / "lstm_forecaster.joblib"
        anomaly_model = self.model_dir / "isolation_forest_detector.joblib"
        clustering_model = self.model_dir / "kmeans_clustering.joblib"
        
        return lstm_model.exists() and anomaly_model.exists() and clustering_model.exists()
    
    def stop(self):
        """Stop the scheduler."""
        self.is_running = False
        logger.info("Model scheduler stopped")
    
    def force_update(self):
        """Force an immediate model update."""
        logger.info("Forcing model update")
        self._update_models()
    
    def get_status(self) -> dict:
        """Get scheduler status.
        
        Returns:
            Status dictionary
        """
        return {
            "is_running": self.is_running,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "update_interval_hours": self.update_interval_hours,
            "next_update": schedule.next_run().isoformat() if schedule.jobs else None
        }
