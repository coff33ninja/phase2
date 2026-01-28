"""Training status API endpoints."""
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Dict, Optional
import sqlite3
from datetime import datetime

router = APIRouter(prefix="/api/training", tags=["training"])


def get_training_status() -> Dict:
    """Get comprehensive training status.
    
    Returns:
        Training status dictionary
    """
    # Check Sentinel data
    sentinel_db = Path("../sentinel/data/system_stats.db")
    sentinel_active = sentinel_db.exists()
    snapshot_count = 0
    data_collection_hours = 0.0
    oldest_snapshot = None
    newest_snapshot = None
    
    if sentinel_active:
        try:
            conn = sqlite3.connect(sentinel_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM system_snapshots")
            snapshot_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM system_snapshots")
            min_time, max_time = cursor.fetchone()
            
            if min_time and max_time:
                oldest_snapshot = min_time
                newest_snapshot = max_time
                start = datetime.fromisoformat(min_time)
                end = datetime.fromisoformat(max_time)
                duration_hours = (end - start).total_seconds() / 3600
                data_collection_hours = round(duration_hours, 1)
            
            conn.close()
        except Exception as e:
            pass
    
    # Check Oracle models
    oracle_models_dir = Path("../oracle/saved_models")
    models_exist = False
    model_files = {}
    
    if oracle_models_dir.exists():
        lstm_model = oracle_models_dir / "lstm_forecaster.joblib"
        anomaly_model = oracle_models_dir / "isolation_forest_detector.joblib"
        clustering_model = oracle_models_dir / "kmeans_clustering.joblib"
        
        models_exist = lstm_model.exists() and anomaly_model.exists() and clustering_model.exists()
        
        if lstm_model.exists():
            model_files["lstm"] = {
                "exists": True,
                "size_mb": round(lstm_model.stat().st_size / 1024 / 1024, 2),
                "modified": datetime.fromtimestamp(lstm_model.stat().st_mtime).isoformat()
            }
        
        if anomaly_model.exists():
            model_files["anomaly"] = {
                "exists": True,
                "size_mb": round(anomaly_model.stat().st_size / 1024 / 1024, 2),
                "modified": datetime.fromtimestamp(anomaly_model.stat().st_mtime).isoformat()
            }
        
        if clustering_model.exists():
            model_files["clustering"] = {
                "exists": True,
                "size_kb": round(clustering_model.stat().st_size / 1024, 2),
                "modified": datetime.fromtimestamp(clustering_model.stat().st_mtime).isoformat()
            }
    
    # Calculate readiness
    min_samples = 1000
    min_hours = 1.0
    ready_for_training = (
        sentinel_active and 
        snapshot_count >= min_samples and 
        data_collection_hours >= min_hours
    )
    
    # Calculate progress
    samples_progress = min(100, (snapshot_count / min_samples) * 100)
    hours_progress = min(100, (data_collection_hours / min_hours) * 100)
    
    return {
        "oracle_trained": models_exist,
        "sentinel_active": sentinel_active,
        "ready_for_training": ready_for_training,
        "snapshot_count": snapshot_count,
        "data_collection_hours": data_collection_hours,
        "oldest_snapshot": oldest_snapshot,
        "newest_snapshot": newest_snapshot,
        "min_samples_needed": min_samples,
        "min_hours_needed": min_hours,
        "recommended_hours": 24.0,
        "samples_progress": round(samples_progress, 1),
        "hours_progress": round(hours_progress, 1),
        "models": model_files,
        "status_message": _get_status_message(
            models_exist, 
            ready_for_training, 
            snapshot_count, 
            min_samples,
            data_collection_hours
        )
    }


def _get_status_message(
    models_exist: bool,
    ready: bool,
    samples: int,
    min_samples: int,
    hours: float
) -> str:
    """Generate human-readable status message."""
    if models_exist:
        return f"✅ Oracle trained and active with {samples:,} samples ({hours:.1f} hours of data)"
    elif ready:
        return f"⚡ Ready to train! {samples:,} samples collected. Training will start automatically."
    else:
        remaining = min_samples - samples
        return f"📊 Collecting data... {samples:,}/{min_samples:,} samples ({remaining:,} more needed)"


@router.get("/status")
async def training_status():
    """Get current training status.
    
    Returns:
        Training status information
    """
    try:
        status = get_training_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress")
async def training_progress():
    """Get training progress for progress bars.
    
    Returns:
        Progress information
    """
    try:
        status = get_training_status()
        return {
            "samples": {
                "current": status["snapshot_count"],
                "required": status["min_samples_needed"],
                "progress": status["samples_progress"]
            },
            "time": {
                "current": status["data_collection_hours"],
                "required": status["min_hours_needed"],
                "progress": status["hours_progress"]
            },
            "ready": status["ready_for_training"],
            "trained": status["oracle_trained"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
