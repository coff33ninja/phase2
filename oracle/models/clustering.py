"""K-means clustering for pattern grouping."""
from pathlib import Path
from typing import Dict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
from loguru import logger

from models.base_model import BaseModel


class KMeansClustering(BaseModel):
    """K-means clustering for identifying usage patterns."""
    
    def __init__(self, model_dir: Path, n_clusters: int = 5):
        """Initialize K-means clustering.
        
        Args:
            model_dir: Directory to save/load models
            n_clusters: Number of clusters
        """
        super().__init__("kmeans_clustering", model_dir)
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )
        self.cluster_labels = {
            0: "idle",
            1: "light_work",
            2: "heavy_work",
            3: "gaming",
            4: "other"
        }
    
    def train(self, X: np.ndarray, y=None, **kwargs):
        """Train K-means clustering.
        
        Args:
            X: Training features (samples, features)
            y: Not used (unsupervised)
            **kwargs: Additional training parameters
        """
        logger.info(f"Training K-means with {len(X)} samples")
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model
        self.model.fit(X_scaled)
        
        self.is_trained = True
        
        # Calculate cluster statistics
        labels = self.model.labels_
        cluster_sizes = np.bincount(labels)
        
        self.update_metadata(
            training_samples=len(X),
            cluster_sizes=cluster_sizes.tolist(),
            inertia=float(self.model.inertia_)
        )
        
        logger.info(f"Clustering complete. Inertia: {self.model.inertia_:.2f}")
    
    def predict(self, X: np.ndarray, **kwargs) -> np.ndarray:
        """Predict cluster labels.
        
        Args:
            X: Input features (samples, features)
            **kwargs: Additional prediction parameters
            
        Returns:
            Cluster labels (samples,)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        labels = self.model.predict(X_scaled)
        return labels
    
    def evaluate(self, X: np.ndarray, y=None, **kwargs) -> Dict[str, float]:
        """Evaluate clustering quality.
        
        Args:
            X: Test features
            y: Not used
            **kwargs: Additional evaluation parameters
            
        Returns:
            Dictionary of evaluation metrics
        """
        X_scaled = self.scaler.transform(X)
        labels = self.model.predict(X_scaled)
        
        metrics = {
            "silhouette_score": float(silhouette_score(X_scaled, labels)),
            "davies_bouldin_score": float(davies_bouldin_score(X_scaled, labels)),
            "inertia": float(self.model.inertia_)
        }
        
        return metrics
    
    def get_cluster_centers(self) -> np.ndarray:
        """Get cluster centers in original feature space.
        
        Returns:
            Cluster centers (n_clusters, n_features)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        centers_scaled = self.model.cluster_centers_
        centers = self.scaler.inverse_transform(centers_scaled)
        return centers
    
    def get_cluster_label(self, cluster_id: int) -> str:
        """Get human-readable label for cluster.
        
        Args:
            cluster_id: Cluster ID
            
        Returns:
            Cluster label
        """
        return self.cluster_labels.get(cluster_id, "unknown")
    
    def update_cluster_labels(self, labels: Dict[int, str]):
        """Update cluster labels based on analysis.
        
        Args:
            labels: Dictionary mapping cluster IDs to labels
        """
        self.cluster_labels.update(labels)
        self.update_metadata(cluster_labels=self.cluster_labels)
