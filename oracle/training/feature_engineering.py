"""Feature engineering for ML models."""
import numpy as np
import pandas as pd
from typing import List


class FeatureEngineer:
    """Create features from raw time series data."""
    
    @staticmethod
    def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features.
        
        Args:
            df: DataFrame with timestamp column
            
        Returns:
            DataFrame with added features
        """
        df = df.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_work_hours'] = df['hour'].between(9, 17).astype(int)
        
        return df
    
    @staticmethod
    def add_rolling_features(
        df: pd.DataFrame,
        columns: List[str],
        windows: List[int] = None
    ) -> pd.DataFrame:
        """Add rolling window features.
        
        Args:
            df: Input DataFrame
            columns: Columns to compute rolling features for
            windows: Window sizes in samples
            
        Returns:
            DataFrame with added features
        """
        if windows is None:
            windows = [5, 15, 60]
        
        df = df.copy()
        
        for col in columns:
            for window in windows:
                df[f"{col}_mean_{window}"] = df[col].rolling(window).mean()
                df[f"{col}_std_{window}"] = df[col].rolling(window).std()
                df[f"{col}_min_{window}"] = df[col].rolling(window).min()
                df[f"{col}_max_{window}"] = df[col].rolling(window).max()
        
        return df
    
    @staticmethod
    def add_lag_features(
        df: pd.DataFrame,
        columns: List[str],
        lags: List[int] = None
    ) -> pd.DataFrame:
        """Add lagged features.
        
        Args:
            df: Input DataFrame
            columns: Columns to create lags for
            lags: Lag values
            
        Returns:
            DataFrame with added features
        """
        if lags is None:
            lags = [1, 5, 15, 60]
        
        df = df.copy()
        
        for col in columns:
            for lag in lags:
                df[f"{col}_lag_{lag}"] = df[col].shift(lag)
        
        return df
    
    @staticmethod
    def add_diff_features(
        df: pd.DataFrame,
        columns: List[str]
    ) -> pd.DataFrame:
        """Add difference features (trends).
        
        Args:
            df: Input DataFrame
            columns: Columns to compute differences for
            
        Returns:
            DataFrame with added features
        """
        df = df.copy()
        
        for col in columns:
            df[f"{col}_diff"] = df[col].diff()
            df[f"{col}_pct_change"] = df[col].pct_change()
        
        return df
    
    @staticmethod
    def create_all_features(df: pd.DataFrame) -> pd.DataFrame:
        """Create all features at once.
        
        Args:
            df: Input DataFrame with timestamp and metrics
            
        Returns:
            DataFrame with all features
        """
        metric_cols = ['cpu_percent', 'ram_percent']
        
        df = FeatureEngineer.add_time_features(df)
        df = FeatureEngineer.add_rolling_features(df, metric_cols)
        df = FeatureEngineer.add_lag_features(df, metric_cols)
        df = FeatureEngineer.add_diff_features(df, metric_cols)
        
        df = df.dropna()
        
        return df
