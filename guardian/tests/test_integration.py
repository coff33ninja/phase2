"""Integration tests for Guardian connectors."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sqlite3

from integration.sentinel_connector import SentinelConnector
from integration.oracle_connector import OracleConnector
from integration.sage_connector import SageConnector


class TestSentinelConnector:
    """Test Sentinel connector."""
    
    def test_create_connector(self, temp_dir):
        """Test connector creation."""
        db_path = temp_dir / "sentinel.db"
        connector = SentinelConnector(db_path=db_path)
        
        assert connector.db_path == db_path
    
    def test_get_current_metrics_no_db(self, temp_dir):
        """Test getting metrics when DB doesn't exist."""
        db_path = temp_dir / "nonexistent.db"
        connector = SentinelConnector(db_path=db_path)
        
        metrics = connector.get_current_metrics()
        
        assert metrics == {}
    
    def test_get_current_metrics_with_data(self, temp_dir, mock_system_metrics):
        """Test getting metrics with data."""
        db_path = temp_dir / "sentinel.db"
        
        # Create mock database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE system_metrics (
                timestamp TEXT,
                cpu_usage REAL,
                ram_usage REAL,
                gpu_usage REAL,
                disk_usage REAL,
                network_usage REAL
            )
        """)
        cursor.execute("""
            INSERT INTO system_metrics VALUES (?, ?, ?, ?, ?, ?)
        """, (
            mock_system_metrics['timestamp'],
            mock_system_metrics['cpu_usage'],
            mock_system_metrics['ram_usage'],
            mock_system_metrics['gpu_usage'],
            mock_system_metrics['disk_usage'],
            mock_system_metrics['network_usage']
        ))
        conn.commit()
        conn.close()
        
        connector = SentinelConnector(db_path=db_path)
        metrics = connector.get_current_metrics()
        
        assert metrics is not None
        assert 'cpu_usage' in metrics
    
    def test_check_thresholds(self, temp_dir):
        """Test threshold checking."""
        db_path = temp_dir / "sentinel.db"
        
        # Create mock database with high CPU
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE system_metrics (
                timestamp TEXT,
                cpu_usage REAL,
                ram_usage REAL,
                gpu_usage REAL,
                disk_usage REAL
            )
        """)
        cursor.execute("""
            INSERT INTO system_metrics VALUES (?, 95.0, 50.0, 30.0, 70.0)
        """, ("2026-01-28T00:00:00",))
        conn.commit()
        conn.close()
        
        connector = SentinelConnector(db_path=db_path)
        violations = connector.check_thresholds()
        
        # Should detect high CPU
        assert len(violations) > 0
        assert any(v['metric'] == 'cpu_usage' for v in violations)


class TestOracleConnector:
    """Test Oracle connector."""
    
    def test_create_connector(self, temp_dir):
        """Test connector creation."""
        db_path = temp_dir / "oracle.db"
        connector = OracleConnector(db_path=db_path)
        
        assert connector.db_path == db_path
    
    def test_get_patterns_no_db(self, temp_dir):
        """Test getting patterns when DB doesn't exist."""
        db_path = temp_dir / "nonexistent.db"
        connector = OracleConnector(db_path=db_path)
        
        patterns = connector.get_current_patterns()
        
        assert patterns == []
    
    def test_get_predictions(self, temp_dir):
        """Test getting predictions."""
        db_path = temp_dir / "oracle.db"
        connector = OracleConnector(db_path=db_path)
        
        prediction = connector.get_predictions("cpu_usage", horizon_minutes=30)
        
        # Should return None when no data
        assert prediction is None


class TestSageConnector:
    """Test Sage connector."""
    
    def test_create_connector(self, temp_dir):
        """Test connector creation."""
        db_path = temp_dir / "sage.db"
        connector = SageConnector(db_path=db_path)
        
        assert connector.db_path == db_path
    
    def test_get_recommendations_no_db(self, temp_dir):
        """Test getting recommendations when DB doesn't exist."""
        db_path = temp_dir / "nonexistent.db"
        connector = SageConnector(db_path=db_path)
        
        recommendations = connector.get_recommendations({})
        
        assert recommendations == []
    
    def test_query_sage(self, temp_dir):
        """Test querying Sage."""
        db_path = temp_dir / "sage.db"
        connector = SageConnector(db_path=db_path)
        
        response = connector.query_sage("What should I optimize?")
        
        # Currently returns None (not implemented)
        assert response is None
