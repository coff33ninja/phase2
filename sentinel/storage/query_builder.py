"""
Query builder utilities
Helper functions for building SQL queries
"""
from typing import List, Dict, Any, Optional
from datetime import datetime


class QueryBuilder:
    """Build SQL queries dynamically"""
    
    @staticmethod
    def build_time_range_filter(
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        time_column: str = "timestamp"
    ) -> tuple[str, List[Any]]:
        """
        Build time range filter clause
        Returns (where_clause, params)
        """
        clauses = []
        params = []
        
        if start_time:
            clauses.append(f"{time_column} >= ?")
            params.append(start_time)
        
        if end_time:
            clauses.append(f"{time_column} <= ?")
            params.append(end_time)
        
        if clauses:
            return " AND ".join(clauses), params
        else:
            return "1=1", []
    
    @staticmethod
    def build_metric_query(
        metric_table: str,
        metric_column: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> tuple[str, List[Any]]:
        """
        Build query for metric history
        Returns (query, params)
        """
        time_filter, params = QueryBuilder.build_time_range_filter(
            start_time, end_time, "s.timestamp"
        )
        
        query = f"""
            SELECT s.timestamp, m.{metric_column} as value
            FROM system_snapshots s
            JOIN {metric_table} m ON s.id = m.snapshot_id
            WHERE {time_filter}
            ORDER BY s.timestamp DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        return query, params
    
    @staticmethod
    def build_aggregation_query(
        metric_table: str,
        metric_column: str,
        aggregation: str = "AVG",
        group_by_minutes: int = 5,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> tuple[str, List[Any]]:
        """
        Build aggregation query
        aggregation: AVG, MIN, MAX, SUM
        """
        time_filter, params = QueryBuilder.build_time_range_filter(
            start_time, end_time, "s.timestamp"
        )
        
        query = f"""
            SELECT 
                datetime(s.timestamp, 'unixepoch', 
                    (strftime('%s', s.timestamp) / ({group_by_minutes} * 60)) * ({group_by_minutes} * 60), 
                    'unixepoch') as time_bucket,
                {aggregation}(m.{metric_column}) as value
            FROM system_snapshots s
            JOIN {metric_table} m ON s.id = m.snapshot_id
            WHERE {time_filter}
            GROUP BY time_bucket
            ORDER BY time_bucket DESC
        """
        
        return query, params
    
    @staticmethod
    def build_insert_query(table: str, data: Dict[str, Any]) -> tuple[str, List[Any]]:
        """
        Build INSERT query from dictionary
        Returns (query, params)
        """
        columns = list(data.keys())
        placeholders = ["?" for _ in columns]
        values = [data[col] for col in columns]
        
        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
        
        return query, values
    
    @staticmethod
    def build_update_query(
        table: str,
        data: Dict[str, Any],
        where_clause: str
    ) -> tuple[str, List[Any]]:
        """
        Build UPDATE query from dictionary
        Returns (query, params)
        """
        set_clauses = [f"{col} = ?" for col in data.keys()]
        values = list(data.values())
        
        query = f"""
            UPDATE {table}
            SET {', '.join(set_clauses)}
            WHERE {where_clause}
        """
        
        return query, values
