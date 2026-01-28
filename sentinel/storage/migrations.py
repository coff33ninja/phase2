"""
Database migrations
Handle schema version upgrades
"""
from pathlib import Path
from loguru import logger
import aiosqlite


class MigrationManager:
    """Manage database schema migrations"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.migrations_dir = Path(__file__).parent / "migrations"
    
    async def get_current_version(self, conn: aiosqlite.Connection) -> str:
        """Get current schema version"""
        try:
            cursor = await conn.execute(
                "SELECT value FROM schema_metadata WHERE key = 'version'"
            )
            row = await cursor.fetchone()
            return row[0] if row else "0.0.0"
        except Exception:
            return "0.0.0"
    
    async def set_version(self, conn: aiosqlite.Connection, version: str):
        """Set schema version"""
        await conn.execute(
            "UPDATE schema_metadata SET value = ?, updated_at = datetime('now') WHERE key = 'version'",
            (version,)
        )
        await conn.commit()
    
    async def run_migrations(self, conn: aiosqlite.Connection):
        """Run all pending migrations"""
        current_version = await self.get_current_version(conn)
        logger.info(f"Current schema version: {current_version}")
        
        # Define migrations
        migrations = [
            ("1.0.0", self._migrate_to_1_0_0),
            # Add future migrations here
        ]
        
        for version, migration_func in migrations:
            if self._version_less_than(current_version, version):
                logger.info(f"Running migration to {version}")
                await migration_func(conn)
                await self.set_version(conn, version)
                logger.info(f"Migration to {version} complete")
    
    def _version_less_than(self, v1: str, v2: str) -> bool:
        """Compare version strings"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        return v1_parts < v2_parts
    
    async def _migrate_to_1_0_0(self, conn: aiosqlite.Connection):
        """Initial schema - already created by schema.sql"""
        pass
