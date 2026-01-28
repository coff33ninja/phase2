"""WebSocket handler for streaming metrics."""
import asyncio
import json
import sqlite3
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from config import config


class MetricsStreamHandler:
    """Handle WebSocket connections for metrics streaming."""
    
    def __init__(self):
        """Initialize handler."""
        self.active_connections: Set[WebSocket] = set()
        self.update_interval = 2  # seconds
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_metrics(self, websocket: WebSocket):
        """Send metrics to a WebSocket client.
        
        Args:
            websocket: WebSocket connection
        """
        try:
            while True:
                # Get current metrics
                metrics = await self._get_current_metrics()
                
                # Send to client
                await websocket.send_json(metrics)
                
                # Wait before next update
                await asyncio.sleep(self.update_interval)
                
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except Exception as e:
            logger.error(f"Error sending metrics: {e}")
            self.disconnect(websocket)
    
    async def _get_current_metrics(self) -> dict:
        """Get current metrics from Sentinel.
        
        Returns:
            Metrics dictionary
        """
        if not config.sentinel_db_path.exists():
            return {"error": "Sentinel database not found"}
        
        try:
            conn = sqlite3.connect(config.sentinel_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM system_metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients.
        
        Args:
            message: Message dictionary to broadcast
        """
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global handler instance
metrics_handler = MetricsStreamHandler()
