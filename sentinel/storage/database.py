"""
SQLite database manager
Handles database connections and schema initialization
"""
import sqlite3
import aiosqlite
from pathlib import Path
from typing import Optional
from loguru import logger


class Database:
    """SQLite database manager with async support"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
        self._schema_path = Path(__file__).parent / "schema.sql"
    
    async def connect(self):
        """Establish database connection"""
        if self._connection is None:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self._connection = await aiosqlite.connect(str(self.db_path))
            
            # Enable foreign keys
            await self._connection.execute("PRAGMA foreign_keys = ON")
            
            # Initialize schema if needed
            await self._initialize_schema()
            
            logger.info(f"Connected to database: {self.db_path}")
    
    async def disconnect(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Disconnected from database")
    
    async def _initialize_schema(self):
        """Initialize database schema from SQL file"""
        try:
            # Read schema file
            schema_sql = self._schema_path.read_text()
            
            # Execute schema
            await self._connection.executescript(schema_sql)
            await self._connection.commit()
            
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise
    
    async def execute(self, query: str, params: tuple = ()):
        """Execute a query"""
        if not self._connection:
            await self.connect()
        
        cursor = await self._connection.execute(query, params)
        await self._connection.commit()
        return cursor
    
    async def execute_many(self, query: str, params_list: list):
        """Execute a query with multiple parameter sets"""
        if not self._connection:
            await self.connect()
        
        await self._connection.executemany(query, params_list)
        await self._connection.commit()
    
    async def fetch_one(self, query: str, params: tuple = ()):
        """Fetch a single row"""
        if not self._connection:
            await self.connect()
        
        cursor = await self._connection.execute(query, params)
        return await cursor.fetchone()
    
    async def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all rows"""
        if not self._connection:
            await self.connect()
        
        cursor = await self._connection.execute(query, params)
        return await cursor.fetchall()
    
    async def cleanup_old_data(self, days: int):
        """Remove data older than specified days"""
        query = """
        DELETE FROM system_snapshots 
        WHERE timestamp < datetime('now', ?)
        """
        await self.execute(query, (f"-{days} days",))
        logger.info(f"Cleaned up data older than {days} days")
    
    async def get_database_size(self) -> int:
        """Get database file size in bytes"""
        if self.db_path.exists():
            return self.db_path.stat().st_size
        return 0
    
    async def vacuum(self):
        """Optimize database (reclaim space)"""
        if not self._connection:
            await self.connect()
        
        await self._connection.execute("VACUUM")
        logger.info("Database vacuumed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
