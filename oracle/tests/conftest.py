"""Pytest configuration and fixtures."""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_time_series():
    """Generate sample time series data."""
    np.random.seed(42)
    n_samples = 1000
    
    timestamps = pd.date_range(start='2024-01-01', periods=n_samples, freq='1min')
    
    data = {
        'timestamp': timestamps,
        'cpu_percent': np.random.uniform(10, 80, n_samples),
        'ram_percent': np.random.uniform(40, 90, n_samples),
        'disk_read_mb': np.random.uniform(0, 10, n_samples),
        'disk_write_mb': np.random.uniform(0, 5, n_samples),
        'network_sent_mb': np.random.uniform(0, 2, n_samples),
        'network_recv_mb': np.random.uniform(0, 3, n_samples)
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_features():
    """Generate sample feature matrix."""
    np.random.seed(42)
    return np.random.rand(100, 10)


@pytest.fixture
def sample_sequences():
    """Generate sample sequences for LSTM."""
    np.random.seed(42)
    X = np.random.rand(50, 60, 10)  # 50 samples, 60 timesteps, 10 features
    y = np.random.rand(50, 4)  # 50 samples, 4 horizons
    return X, y


@pytest.fixture
def sample_labels():
    """Generate sample labels for classification."""
    np.random.seed(42)
    return np.random.randint(0, 5, 100)
