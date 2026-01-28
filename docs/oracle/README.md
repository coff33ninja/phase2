# Oracle - Local ML & Pattern Learning
## Phase 2.2: Machine Learning

> **Codename:** Oracle  
> **Mission:** Predict and learn patterns  
> **Status:** 🎯 Planned

---

## 🎯 Purpose

Oracle is the machine learning brain of the system. It learns from the data collected by Sentinel, identifies patterns in user behavior and system performance, predicts future resource usage, and detects anomalies that simple thresholds can't catch.

## 🧠 Machine Learning Models

### Primary Model: LSTM Neural Network
- **Purpose:** Time-series forecasting
- **Predicts:** CPU, RAM, GPU usage for next 1-60 minutes
- **Training:** Continuous online learning
- **Framework:** TensorFlow Lite or PyTorch Mobile

### Secondary Models

#### 1. Clustering (K-means)
- **Purpose:** Group similar usage patterns
- **Identifies:** Work modes, gaming sessions, idle periods
- **Output:** User behavior profiles

#### 2. Classification (Random Forest)
- **Purpose:** Categorize processes and activities
- **Identifies:** Process types, user actions, workload categories
- **Output:** Activity labels

#### 3. Anomaly Detection (Isolation Forest)
- **Purpose:** Detect unusual behavior
- **Identifies:** Performance issues, malware, system problems
- **Output:** Anomaly scores and alerts

## 📊 What Oracle Learns

### 1. User Behavior Patterns
```python
{
    "work_hours": {
        "typical_start": "08:30",
        "typical_end": "17:45",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    },
    "application_usage": {
        "vscode": {
            "avg_duration": "4.5h",
            "peak_hours": [9, 14, 16],
            "typical_ram": "1.2GB",
            "typical_cpu": "8%"
        },
        "chrome": {
            "avg_tabs": 23,
            "memory_pattern": "high_morning",
            "typical_ram": "3.5GB"
        }
    },
    "activity_patterns": {
        "coding": {
            "apps": ["vscode", "chrome", "terminal"],
            "cpu_range": "15-35%",
            "ram_range": "16-22GB"
        },
        "gaming": {
            "apps": ["steam", "discord"],
            "cpu_range": "60-85%",
            "gpu_range": "80-95%"
        }
    }
}
```

### 2. Resource Usage Trends
- Baseline CPU/RAM/GPU usage per hour of day
- Weekly patterns (weekday vs weekend)
- Seasonal trends (if applicable)
- Growth trends (increasing resource needs over time)

### 3. Process Correlations
- Which processes typically run together
- Process startup sequences
- Resource competition patterns
- Dependency chains

### 4. Performance Baselines
- Normal operating ranges for each metric
- Expected performance per application
- Typical response times
- Standard deviation calculations

### 5. Anomaly Signatures
- Unusual process behavior patterns
- Unexpected resource spikes
- Abnormal network activity
- System instability indicators

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SENTINEL DATA                             │
│              (Time-series database)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 DATA PREPROCESSING                           │
│  • Feature engineering                                      │
│  • Normalization                                            │
│  • Window creation                                          │
│  • Train/test split                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│    LSTM     │ │  Clustering │ │Classification│
│  Forecaster │ │   K-means   │ │Random Forest│
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 PATTERN RECOGNITION                          │
│  • Behavior profiles                                        │
│  • Usage predictions                                        │
│  • Anomaly detection                                        │
│  • Optimization opportunities                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  MODEL STORAGE                               │
│  • Trained model weights                                    │
│  • Feature scalers                                          │
│  • Pattern database                                         │
│  • Performance metrics                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 INFERENCE ENGINE                             │
│  • Real-time predictions                                    │
│  • Pattern matching                                         │
│  • Anomaly scoring                                          │
│  • Confidence calculation                                   │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Planned Components

### `/models`
- `lstm_forecaster.py` - Time-series prediction model
- `clustering.py` - K-means for pattern grouping
- `classifier.py` - Random Forest for categorization
- `anomaly_detector.py` - Isolation Forest for anomalies
- `base_model.py` - Abstract base class for all models

### `/training`
- `trainer.py` - Model training orchestration
- `data_loader.py` - Load data from Sentinel
- `feature_engineering.py` - Create features from raw data
- `validation.py` - Model validation and metrics
- `hyperparameter_tuning.py` - Optimize model parameters

### `/inference`
- `predictor.py` - Real-time prediction engine
- `pattern_matcher.py` - Match current state to learned patterns
- `confidence_calculator.py` - Calculate prediction confidence
- `explainer.py` - Explain model decisions

### `/patterns`
- `behavior_profiles.py` - User behavior pattern storage
- `usage_patterns.py` - Resource usage pattern storage
- `correlation_matrix.py` - Process correlation tracking
- `baseline_manager.py` - Dynamic baseline calculation

## 🚀 Implementation Plan

### Week 3: Foundation
- [ ] Set up ML framework (TensorFlow Lite or PyTorch)
- [ ] Create data preprocessing pipeline
- [ ] Implement feature engineering
- [ ] Build training data loader from Sentinel

### Week 4: Model Development
- [ ] Implement LSTM forecaster
- [ ] Add K-means clustering
- [ ] Create Random Forest classifier
- [ ] Build Isolation Forest anomaly detector

### Week 5: Training Pipeline
- [ ] Implement continuous learning
- [ ] Add model validation
- [ ] Create performance metrics
- [ ] Build model versioning

### Week 6: Inference & Integration
- [ ] Real-time prediction engine
- [ ] Pattern matching system
- [ ] Integration with Sentinel
- [ ] Prepare for Sage integration

## 📊 Training Data Structure

```python
{
    "features": {
        # Time features
        "hour_of_day": 14,
        "day_of_week": 2,
        "is_weekend": False,
        
        # Current metrics
        "cpu_usage": 45.2,
        "ram_usage": 18.5,
        "gpu_usage": 12.0,
        
        # Historical features (rolling windows)
        "cpu_mean_1h": 42.1,
        "cpu_std_1h": 5.3,
        "cpu_trend_1h": 0.05,  # increasing
        
        # Process features
        "active_processes": 156,
        "top_process_cpu": 15.2,
        "chrome_running": True,
        "vscode_running": True,
        
        # Context features
        "user_active": True,
        "detected_activity": "coding"
    },
    "targets": {
        # What we're predicting
        "cpu_next_5m": 48.5,
        "cpu_next_15m": 52.1,
        "cpu_next_60m": 45.0,
        "ram_next_5m": 19.2,
        "anomaly_score": 0.12
    }
}
```

## 🎯 Success Metrics

### Prediction Accuracy
- **CPU Usage:** >85% accuracy within ±5%
- **RAM Usage:** >85% accuracy within ±10%
- **GPU Usage:** >80% accuracy within ±10%

### Anomaly Detection
- **False Positive Rate:** <5%
- **True Positive Rate:** >90%
- **Detection Latency:** <30 seconds

### Performance
- **Inference Time:** <100ms
- **Training Time:** <5 minutes for daily update
- **Model Size:** <50MB
- **CPU Overhead:** <1%

## 🔗 Integration Points

### Input from Sentinel
- Historical time-series data
- Real-time metric stream
- Process information
- Context data

### Output to Sage
- Learned patterns summary
- Predictions with confidence
- Detected anomalies
- Optimization opportunities

### Output to Guardian
- Resource usage predictions
- Recommended actions
- Anomaly alerts
- Pattern-based rules

## 📚 Technologies

- **ML Framework:** TensorFlow Lite or PyTorch Mobile
- **Data Processing:** NumPy, Pandas
- **Feature Engineering:** scikit-learn
- **Model Storage:** ONNX format
- **Visualization:** Matplotlib, Seaborn

## 🎓 Learning Examples

### Example 1: Gaming Pattern
```
Week 1: Oracle observes user games 19:00-23:00 weekdays
Week 2: Predicts gaming session at 18:55
Week 3: Learns user closes Chrome before gaming
Week 4: Recommends closing Chrome at 18:55
```

### Example 2: Work Pattern
```
Week 1: Observes VS Code + Chrome usage 9:00-17:00
Week 2: Learns typical RAM usage is 18-22GB
Week 3: Detects anomaly when RAM hits 28GB
Week 4: Identifies Chrome tab explosion as cause
```

---

**Last Updated:** January 27, 2026  
**Status:** 🎯 Planned  
**Prerequisites:** Sentinel (Phase 2.1) ✅  
**Next Phase:** Sage (Phase 2.3) - Gemini Integration
