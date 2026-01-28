"""Status API endpoints for system and training status."""
from fastapi import APIRouter
from pathlib import Path
import sqlite3
from datetime import datetime
from typing import Dict

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get("/system")
async def get_system_status() -> Dict:
    """Get comprehensive system status including training readiness.
    
    Returns:
        System status with component health and training progress
    """
    # Database paths
    sentinel_db = Path("../sentinel/data/system_stats.db")
    oracle_db = Path("../oracle/data/patterns.db")
    oracle_models_dir = Path("../oracle/saved_models")
    
    # Check if Oracle is trained by looking for model files
    oracle_trained = False
    if oracle_models_dir.exists():
        lstm_model = oracle_models_dir / "lstm_forecaster.joblib"
        anomaly_model = oracle_models_dir / "isolation_forest_detector.joblib"
        clustering_model = oracle_models_dir / "kmeans_clustering.joblib"
        oracle_trained = lstm_model.exists() and anomaly_model.exists() and clustering_model.exists()
    
    if not oracle_trained and oracle_db.exists():
        oracle_trained = True
    
    status = {
        "components": {
            "sentinel": {
                "active": sentinel_db.exists(),
                "database": str(sentinel_db)
            },
            "oracle": {
                "trained": oracle_trained,
                "database": str(oracle_db)
            },
            "sage": {
                "active": True,
                "model": "gemini-2.5-flash"
            },
            "guardian": {
                "active": True,
                "mode": "on-demand"
            },
            "nexus": {
                "active": True,
                "version": "0.1.0"
            }
        },
        "training": {
            "oracle_trained": oracle_trained,
            "ready_for_training": False,
            "data_collection_hours": 0,
            "snapshot_count": 0,
            "min_hours_needed": 1.0,
            "min_samples_needed": 1000,
            "recommended_hours": 24.0,
            "progress_percentage": 0
        }
    }
    
    # Get Sentinel data collection status
    if sentinel_db.exists():
        try:
            conn = sqlite3.connect(sentinel_db)
            cursor = conn.cursor()
            
            # Get snapshot count
            cursor.execute("SELECT COUNT(*) FROM system_snapshots")
            snapshot_count = cursor.fetchone()[0]
            status["training"]["snapshot_count"] = snapshot_count
            
            # Get time range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM system_snapshots")
            min_time, max_time = cursor.fetchone()
            
            if min_time and max_time:
                start = datetime.fromisoformat(min_time)
                end = datetime.fromisoformat(max_time)
                duration_hours = (end - start).total_seconds() / 3600
                status["training"]["data_collection_hours"] = round(duration_hours, 2)
                
                # Calculate progress
                time_progress = min(100, (duration_hours / status["training"]["min_hours_needed"]) * 100)
                samples_progress = min(100, (snapshot_count / status["training"]["min_samples_needed"]) * 100)
                status["training"]["progress_percentage"] = round((time_progress + samples_progress) / 2, 1)
                
                # Check if ready for training
                if (duration_hours >= status["training"]["min_hours_needed"] and 
                    snapshot_count >= status["training"]["min_samples_needed"]):
                    status["training"]["ready_for_training"] = True
                
                # Add collection info
                status["components"]["sentinel"]["collection_start"] = start.isoformat()
                status["components"]["sentinel"]["latest_snapshot"] = end.isoformat()
            
            conn.close()
        except Exception as e:
            status["components"]["sentinel"]["error"] = str(e)
    
    return status


@router.get("/training")
async def get_training_status() -> Dict:
    """Get detailed training status and progress.
    
    Returns:
        Training readiness information
    """
    sentinel_db = Path("../sentinel/data/system_stats.db")
    oracle_db = Path("../oracle/data/patterns.db")
    oracle_models_dir = Path("../oracle/saved_models")
    
    # Check if Oracle is trained by looking for model files
    oracle_trained = False
    if oracle_models_dir.exists():
        lstm_model = oracle_models_dir / "lstm_forecaster.joblib"
        anomaly_model = oracle_models_dir / "isolation_forest_detector.joblib"
        clustering_model = oracle_models_dir / "kmeans_clustering.joblib"
        oracle_trained = lstm_model.exists() and anomaly_model.exists() and clustering_model.exists()
    
    if not oracle_trained and oracle_db.exists():
        oracle_trained = True
    
    training_status = {
        "oracle_trained": oracle_trained,
        "sentinel_active": sentinel_db.exists(),
        "ready_for_training": False,
        "data_collection_hours": 0,
        "snapshot_count": 0,
        "requirements": {
            "min_hours": 1.0,
            "min_samples": 1000,
            "recommended_hours": 24.0
        },
        "progress": {
            "time_percentage": 0,
            "samples_percentage": 0,
            "overall_percentage": 0
        },
        "next_steps": []
    }
    
    if not sentinel_db.exists():
        training_status["next_steps"].append({
            "action": "start_sentinel",
            "description": "Start Sentinel to begin collecting data",
            "command": "cd sentinel && python main.py monitor"
        })
        return training_status
    
    try:
        conn = sqlite3.connect(sentinel_db)
        cursor = conn.cursor()
        
        # Get metrics
        cursor.execute("SELECT COUNT(*) FROM system_snapshots")
        snapshot_count = cursor.fetchone()[0]
        training_status["snapshot_count"] = snapshot_count
        
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM system_snapshots")
        min_time, max_time = cursor.fetchone()
        
        if min_time and max_time:
            start = datetime.fromisoformat(min_time)
            end = datetime.fromisoformat(max_time)
            duration_hours = (end - start).total_seconds() / 3600
            training_status["data_collection_hours"] = round(duration_hours, 2)
            
            # Calculate progress
            time_progress = min(100, (duration_hours / training_status["requirements"]["min_hours"]) * 100)
            samples_progress = min(100, (snapshot_count / training_status["requirements"]["min_samples"]) * 100)
            
            training_status["progress"]["time_percentage"] = round(time_progress, 1)
            training_status["progress"]["samples_percentage"] = round(samples_progress, 1)
            training_status["progress"]["overall_percentage"] = round((time_progress + samples_progress) / 2, 1)
            
            # Determine readiness and next steps
            if oracle_trained:
                training_status["next_steps"].append({
                    "action": "trained",
                    "description": "Oracle is trained and ready! Automatic retraining every 24 hours.",
                    "status": "complete"
                })
            elif duration_hours >= training_status["requirements"]["min_hours"] and snapshot_count >= training_status["requirements"]["min_samples"]:
                training_status["ready_for_training"] = True
                training_status["next_steps"].append({
                    "action": "train_oracle",
                    "description": "Ready to train! Oracle will train automatically when scheduler runs.",
                    "command": "cd oracle && python main.py train",
                    "priority": "high"
                })
            else:
                if duration_hours < training_status["requirements"]["min_hours"]:
                    hours_remaining = training_status["requirements"]["min_hours"] - duration_hours
                    training_status["next_steps"].append({
                        "action": "collect_more_time",
                        "description": f"Collect {hours_remaining:.1f} more hours of data",
                        "status": "in_progress"
                    })
                
                if snapshot_count < training_status["requirements"]["min_samples"]:
                    samples_remaining = training_status["requirements"]["min_samples"] - snapshot_count
                    training_status["next_steps"].append({
                        "action": "collect_more_samples",
                        "description": f"Collect {samples_remaining} more samples",
                        "status": "in_progress"
                    })
        
        conn.close()
    except Exception as e:
        training_status["error"] = str(e)
    
    return training_status
