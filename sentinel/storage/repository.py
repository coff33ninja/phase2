"""
Data repository layer
Provides high-level data access methods
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from storage.database import Database
from models import (
    SystemSnapshot, CPUMetrics, RAMMetrics, GPUMetrics,
    DiskMetrics, NetworkMetrics, ProcessInfo, SystemContext,
    AnomalyDetection
)


class Repository:
    """Data access layer for system metrics"""
    
    def __init__(self, database: Database):
        self.db = database
    
    async def save_snapshot(self, snapshot: SystemSnapshot) -> int:
        """
        Save a complete system snapshot to database
        Returns the snapshot ID
        """
        try:
            # Insert snapshot
            cursor = await self.db.execute(
                "INSERT INTO system_snapshots (timestamp) VALUES (?)",
                (snapshot.timestamp,)
            )
            snapshot_id = cursor.lastrowid
            
            # Save CPU metrics
            await self._save_cpu_metrics(snapshot_id, snapshot.cpu)
            
            # Save RAM metrics
            await self._save_ram_metrics(snapshot_id, snapshot.ram)
            
            # Save GPU metrics
            if snapshot.gpu:
                await self._save_gpu_metrics(snapshot_id, snapshot.gpu)
            
            # Save disk metrics
            await self._save_disk_metrics(snapshot_id, snapshot.disk)
            
            # Save network metrics
            await self._save_network_metrics(snapshot_id, snapshot.network)
            
            # Save process info
            if snapshot.processes:
                await self._save_process_info(snapshot_id, snapshot.processes)
            
            # Save context
            await self._save_context(snapshot_id, snapshot.context)
            
            logger.debug(f"Saved snapshot {snapshot_id} at {snapshot.timestamp}")
            return snapshot_id
            
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            raise
    
    async def _save_cpu_metrics(self, snapshot_id: int, cpu: CPUMetrics):
        """Save CPU metrics"""
        cursor = await self.db.execute(
            """
            INSERT INTO cpu_metrics 
            (snapshot_id, usage_percent, frequency_mhz, temperature_celsius)
            VALUES (?, ?, ?, ?)
            """,
            (snapshot_id, cpu.usage_percent, cpu.frequency_mhz, cpu.temperature_celsius)
        )
        
        cpu_metric_id = cursor.lastrowid
        
        # Save per-core usage
        if cpu.per_core_usage:
            params = [
                (cpu_metric_id, idx, usage)
                for idx, usage in enumerate(cpu.per_core_usage)
            ]
            await self.db.execute_many(
                "INSERT INTO cpu_core_usage (cpu_metric_id, core_index, usage_percent) VALUES (?, ?, ?)",
                params
            )
    
    async def _save_ram_metrics(self, snapshot_id: int, ram: RAMMetrics):
        """Save RAM metrics"""
        await self.db.execute(
            """
            INSERT INTO ram_metrics 
            (snapshot_id, total_gb, used_gb, available_gb, cached_gb, usage_percent)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (snapshot_id, ram.total_gb, ram.used_gb, ram.available_gb, 
             ram.cached_gb, ram.usage_percent)
        )
    
    async def _save_gpu_metrics(self, snapshot_id: int, gpus: List[GPUMetrics]):
        """Save GPU metrics"""
        params = [
            (snapshot_id, gpu.name, gpu.usage_percent, gpu.memory_used_gb,
             gpu.memory_total_gb, gpu.temperature_celsius, gpu.power_draw_watts)
            for gpu in gpus
        ]
        await self.db.execute_many(
            """
            INSERT INTO gpu_metrics 
            (snapshot_id, name, usage_percent, memory_used_gb, memory_total_gb, 
             temperature_celsius, power_draw_watts)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            params
        )
    
    async def _save_disk_metrics(self, snapshot_id: int, disk: DiskMetrics):
        """Save disk metrics"""
        await self.db.execute(
            """
            INSERT INTO disk_metrics 
            (snapshot_id, read_mbps, write_mbps, queue_length, usage_percent)
            VALUES (?, ?, ?, ?, ?)
            """,
            (snapshot_id, disk.read_mbps, disk.write_mbps, 
             disk.queue_length, disk.usage_percent)
        )
    
    async def _save_network_metrics(self, snapshot_id: int, network: NetworkMetrics):
        """Save network metrics"""
        await self.db.execute(
            """
            INSERT INTO network_metrics 
            (snapshot_id, download_mbps, upload_mbps, connections_active)
            VALUES (?, ?, ?, ?)
            """,
            (snapshot_id, network.download_mbps, network.upload_mbps, 
             network.connections_active)
        )
    
    async def _save_process_info(self, snapshot_id: int, processes: List[ProcessInfo]):
        """Save process information"""
        params = [
            (snapshot_id, proc.name, proc.pid, proc.cpu_percent, 
             proc.memory_mb, proc.threads, proc.status)
            for proc in processes
        ]
        await self.db.execute_many(
            """
            INSERT INTO process_info 
            (snapshot_id, name, pid, cpu_percent, memory_mb, threads, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            params
        )
    
    async def _save_context(self, snapshot_id: int, context: SystemContext):
        """Save system context"""
        await self.db.execute(
            """
            INSERT INTO system_context 
            (snapshot_id, user_active, time_of_day, day_of_week, user_action)
            VALUES (?, ?, ?, ?, ?)
            """,
            (snapshot_id, context.user_active, context.time_of_day, 
             context.day_of_week, context.user_action)
        )
    
    async def save_anomaly(self, anomaly: AnomalyDetection):
        """Save anomaly detection result"""
        await self.db.execute(
            """
            INSERT INTO anomalies 
            (timestamp, metric_name, current_value, expected_value, 
             deviation_std, severity, context_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (anomaly.timestamp, anomaly.metric_name, anomaly.current_value,
             anomaly.expected_value, anomaly.deviation_std, anomaly.severity,
             json.dumps(anomaly.context))
        )
    
    async def get_recent_snapshots(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent snapshots with basic metrics"""
        rows = await self.db.fetch_all(
            """
            SELECT 
                s.id, s.timestamp,
                c.usage_percent as cpu_usage,
                r.usage_percent as ram_usage,
                d.read_mbps, d.write_mbps,
                n.download_mbps, n.upload_mbps
            FROM system_snapshots s
            LEFT JOIN cpu_metrics c ON s.id = c.snapshot_id
            LEFT JOIN ram_metrics r ON s.id = r.snapshot_id
            LEFT JOIN disk_metrics d ON s.id = d.snapshot_id
            LEFT JOIN network_metrics n ON s.id = n.snapshot_id
            ORDER BY s.timestamp DESC
            LIMIT ?
            """,
            (limit,)
        )
        
        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'cpu_usage': row[2],
                'ram_usage': row[3],
                'disk_read': row[4],
                'disk_write': row[5],
                'net_download': row[6],
                'net_upload': row[7]
            }
            for row in rows
        ]
    
    async def get_metric_history(
        self, 
        metric_name: str, 
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get historical data for a specific metric"""
        # Map metric names to tables
        metric_queries = {
            'cpu': """
                SELECT s.timestamp, c.usage_percent as value
                FROM system_snapshots s
                JOIN cpu_metrics c ON s.id = c.snapshot_id
                WHERE s.timestamp > datetime('now', ?)
                ORDER BY s.timestamp
            """,
            'ram': """
                SELECT s.timestamp, r.usage_percent as value
                FROM system_snapshots s
                JOIN ram_metrics r ON s.id = r.snapshot_id
                WHERE s.timestamp > datetime('now', ?)
                ORDER BY s.timestamp
            """,
            'disk_read': """
                SELECT s.timestamp, d.read_mbps as value
                FROM system_snapshots s
                JOIN disk_metrics d ON s.id = d.snapshot_id
                WHERE s.timestamp > datetime('now', ?)
                ORDER BY s.timestamp
            """,
            'network_download': """
                SELECT s.timestamp, n.download_mbps as value
                FROM system_snapshots s
                JOIN network_metrics n ON s.id = n.snapshot_id
                WHERE s.timestamp > datetime('now', ?)
                ORDER BY s.timestamp
            """
        }
        
        query = metric_queries.get(metric_name)
        if not query:
            return []
        
        rows = await self.db.fetch_all(query, (f"-{hours} hours",))
        return [{'timestamp': row[0], 'value': row[1]} for row in rows]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        total_snapshots = await self.db.fetch_one(
            "SELECT COUNT(*) FROM system_snapshots"
        )
        
        oldest_snapshot = await self.db.fetch_one(
            "SELECT MIN(timestamp) FROM system_snapshots"
        )
        
        newest_snapshot = await self.db.fetch_one(
            "SELECT MAX(timestamp) FROM system_snapshots"
        )
        
        db_size = await self.db.get_database_size()
        
        return {
            'total_snapshots': total_snapshots[0] if total_snapshots else 0,
            'oldest_snapshot': oldest_snapshot[0] if oldest_snapshot else None,
            'newest_snapshot': newest_snapshot[0] if newest_snapshot else None,
            'database_size_mb': round(db_size / (1024 * 1024), 2)
        }
