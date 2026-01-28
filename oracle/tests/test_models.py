"""Tests for ML models."""
import pytest
import numpy as np
from pathlib import Path

from models.lstm_forecaster import LSTMForecaster
from models.clustering import KMeansClustering
from models.classifier import RandomForestClassifier
from models.anomaly_detector import IsolationForestDetector


class TestLSTMForecaster:
    """Test LSTM forecaster."""
    
    def test_initialization(self, temp_dir):
        """Test model initialization."""
        model = LSTMForecaster(temp_dir, sequence_length=60, n_features=10)
        assert model.sequence_length == 60
        assert model.n_features == 10
        assert not model.is_trained
    
    def test_training(self, temp_dir, sample_sequences):
        """Test model training."""
        X, y = sample_sequences
        model = LSTMForecaster(temp_dir, sequence_length=60, n_features=10)
        
        model.train(X, y, epochs=2, batch_size=16)
        
        assert model.is_trained
        assert 'training_samples' in model.metadata
    
    def test_prediction(self, temp_dir, sample_sequences):
        """Test making predictions."""
        X, y = sample_sequences
        model = LSTMForecaster(temp_dir, sequence_length=60, n_features=10)
        
        model.train(X, y, epochs=2, batch_size=16)
        predictions = model.predict(X[:5])
        
        assert predictions.shape == (5, 4)
    
    def test_save_load(self, temp_dir, sample_sequences):
        """Test model persistence."""
        X, y = sample_sequences
        model = LSTMForecaster(temp_dir, sequence_length=60, n_features=10)
        
        model.train(X, y, epochs=2, batch_size=16)
        model.save()
        
        new_model = LSTMForecaster(temp_dir, sequence_length=60, n_features=10)
        assert new_model.load()
        assert new_model.is_trained


class TestKMeansClustering:
    """Test K-means clustering."""
    
    def test_initialization(self, temp_dir):
        """Test model initialization."""
        model = KMeansClustering(temp_dir, n_clusters=5)
        assert model.n_clusters == 5
        assert not model.is_trained
    
    def test_training(self, temp_dir, sample_features):
        """Test model training."""
        model = KMeansClustering(temp_dir, n_clusters=5)
        model.train(sample_features)
        
        assert model.is_trained
        assert 'training_samples' in model.metadata
    
    def test_prediction(self, temp_dir, sample_features):
        """Test cluster prediction."""
        model = KMeansClustering(temp_dir, n_clusters=5)
        model.train(sample_features)
        
        labels = model.predict(sample_features[:10])
        
        assert len(labels) == 10
        assert all(0 <= label < 5 for label in labels)
    
    def test_cluster_centers(self, temp_dir, sample_features):
        """Test getting cluster centers."""
        model = KMeansClustering(temp_dir, n_clusters=5)
        model.train(sample_features)
        
        centers = model.get_cluster_centers()
        
        assert centers.shape == (5, sample_features.shape[1])


class TestRandomForestClassifier:
    """Test Random Forest classifier."""
    
    def test_initialization(self, temp_dir):
        """Test model initialization."""
        model = RandomForestClassifier(temp_dir, n_estimators=10)
        assert not model.is_trained
    
    def test_training(self, temp_dir, sample_features, sample_labels):
        """Test model training."""
        model = RandomForestClassifier(temp_dir, n_estimators=10)
        model.train(sample_features, sample_labels)
        
        assert model.is_trained
        assert 'training_samples' in model.metadata
    
    def test_prediction(self, temp_dir, sample_features, sample_labels):
        """Test classification."""
        model = RandomForestClassifier(temp_dir, n_estimators=10)
        model.train(sample_features, sample_labels)
        
        predictions = model.predict(sample_features[:10])
        
        assert len(predictions) == 10
    
    def test_predict_proba(self, temp_dir, sample_features, sample_labels):
        """Test probability prediction."""
        model = RandomForestClassifier(temp_dir, n_estimators=10)
        model.train(sample_features, sample_labels)
        
        probas = model.predict_proba(sample_features[:10])
        
        assert probas.shape[0] == 10
        assert np.allclose(probas.sum(axis=1), 1.0)


class TestIsolationForestDetector:
    """Test Isolation Forest anomaly detector."""
    
    def test_initialization(self, temp_dir):
        """Test model initialization."""
        model = IsolationForestDetector(temp_dir, contamination=0.1)
        assert model.contamination == 0.1
        assert not model.is_trained
    
    def test_training(self, temp_dir, sample_features):
        """Test model training."""
        model = IsolationForestDetector(temp_dir, contamination=0.1)
        model.train(sample_features)
        
        assert model.is_trained
        assert 'training_samples' in model.metadata
    
    def test_prediction(self, temp_dir, sample_features):
        """Test anomaly detection."""
        model = IsolationForestDetector(temp_dir, contamination=0.1)
        model.train(sample_features)
        
        predictions = model.predict(sample_features[:10])
        
        assert len(predictions) == 10
        assert all(pred in [-1, 1] for pred in predictions)
    
    def test_score_samples(self, temp_dir, sample_features):
        """Test anomaly scoring."""
        model = IsolationForestDetector(temp_dir, contamination=0.1)
        model.train(sample_features)
        
        scores = model.score_samples(sample_features[:10])
        
        assert len(scores) == 10
        assert all(isinstance(score, (int, float)) for score in scores)
