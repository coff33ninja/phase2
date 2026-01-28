# Oracle Usage Guide

## Quick Start

### 1. Setup
```powershell
# Run setup script
.\setup.ps1

# Or manual setup
pip install -r requirements.txt
pip install -e .
```

### 2. Check Status
```powershell
python main.py status
```

### 3. Train Models
```powershell
# Train with 30 days of data
python main.py train --days 30

# Train with custom parameters
python main.py train --days 60
```

### 4. Make Predictions
```powershell
python main.py predict
```

## CLI Commands

### `status`
Show current model status and training information.

```powershell
python main.py status
```

**Output:**
- Model names and training status
- Number of training samples
- Last training date
- Model performance metrics

### `train`
Train all ML models on historical data from Sentinel.

```powershell
python main.py train [OPTIONS]
```

**Options:**
- `--days INTEGER`: Number of days of data to use (default: 30)

**Requirements:**
- Sentinel must be running
- Minimum 1000 samples recommended
- Database path configured in .env

**Example:**
```powershell
# Train with 30 days
python main.py train --days 30

# Train with 60 days
python main.py train --days 60
```

### `predict`
Make predictions on current system state.

```powershell
python main.py predict
```

**Output:**
- CPU usage predictions (5m, 15m, 30m, 60m)
- RAM usage predictions
- Anomaly detection results
- Confidence scores

## Configuration

Edit `.env` file to customize Oracle behavior:

```env
# Sentinel Database
SENTINEL_DB_PATH=../sentinel/data/system_stats.db

# Model Storage
MODEL_DIR=saved_models
PATTERN_DB_PATH=data/patterns.db

# Training
TRAINING_WINDOW_DAYS=30
MIN_TRAINING_SAMPLES=1000
BATCH_SIZE=32
EPOCHS=50

# Prediction
PREDICTION_HORIZONS=5,15,30,60
CONFIDENCE_THRESHOLD=0.7

# Anomaly Detection
ANOMALY_CONTAMINATION=0.1
ANOMALY_THRESHOLD=0.8
```

## Python API

### Training Models

```python
from pathlib import Path
from training.data_loader import SentinelDataLoader
from training.feature_engineering import FeatureEngineer
from training.trainer import ModelTrainer
from models.lstm_forecaster import LSTMForecaster

# Load data
loader = SentinelDataLoader(Path("../sentinel/data/system_stats.db"))
df = loader.load_time_series(days=30)

# Engineer features
df = FeatureEngineer.create_all_features(df)

# Prepare sequences
X, y = loader.create_sequences(df[['cpu_percent']].values)

# Train model
model = LSTMForecaster(Path("saved_models"))
trainer = ModelTrainer(model)

X_train, X_test, y_train, y_test = trainer.train_test_split(X, y)
metrics = trainer.train_and_evaluate(X_train, y_train, X_test, y_test)

# Save model
trainer.save_model()
```

### Making Predictions

```python
from inference.predictor import Predictor
import numpy as np

# Load predictor
predictor = Predictor(Path("saved_models"))
predictor.load_models()

# Prepare current sequence (last 60 samples)
current_sequence = np.random.rand(60, 10)  # Replace with real data

# Predict future
predictions = predictor.predict_future(current_sequence)
print(f"CPU in 5 minutes: {predictions['cpu_5m']:.1f}%")

# Detect anomalies
current_features = np.random.rand(10)  # Replace with real features
anomaly_info = predictor.detect_anomaly(current_features)
print(f"Is anomaly: {anomaly_info['is_anomaly']}")
```

## Model Details

### LSTM Forecaster
- **Purpose:** Predict future CPU/RAM/GPU usage
- **Architecture:** 2-layer LSTM with dropout
- **Input:** 60-step sequences
- **Output:** Predictions for 5m, 15m, 30m, 60m horizons
- **Training:** Early stopping with validation split

### Anomaly Detector
- **Purpose:** Detect unusual system behavior
- **Algorithm:** Isolation Forest
- **Features:** Current metrics + rolling statistics
- **Output:** Anomaly score and binary classification

### Clustering
- **Purpose:** Group similar usage patterns
- **Algorithm:** K-means (5 clusters)
- **Output:** Pattern labels (idle, work, gaming, etc.)

### Classifier
- **Purpose:** Categorize activities
- **Algorithm:** Random Forest
- **Features:** Process info + resource usage
- **Output:** Activity category with confidence

## Troubleshooting

### "Sentinel database not found"
- Ensure Sentinel is installed and has run at least once
- Check `SENTINEL_DB_PATH` in .env
- Verify path is relative to Oracle directory

### "Not enough data for training"
- Sentinel needs to collect more data
- Run Sentinel for at least a few days
- Minimum 1000 samples recommended

### "Model not loaded"
- Train models first with `python main.py train`
- Check that saved_models directory exists
- Verify models were saved successfully

### TensorFlow errors
- Ensure TensorFlow is installed: `pip install tensorflow`
- Check Python version (3.12 required)
- Try CPU-only version if GPU issues occur

## Performance Tips

1. **Training Data:** More data = better predictions (30+ days recommended)
2. **Update Frequency:** Retrain models weekly for best accuracy
3. **Feature Selection:** Customize features in `feature_engineering.py`
4. **Model Tuning:** Adjust hyperparameters in config.py

## Integration with Sentinel

Oracle automatically reads from Sentinel's database:

```
Sentinel (Phase 2.1)
    ↓ Collects data
    ↓ Stores in SQLite
    ↓
Oracle (Phase 2.2)
    ↓ Loads historical data
    ↓ Trains models
    ↓ Makes predictions
```

Ensure Sentinel is running and collecting data before training Oracle models.
