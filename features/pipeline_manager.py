"""
Frozen feature pipelines using sklearn for reproducibility.
Includes clustering with quality metrics and persistence.
"""
import pickle
import joblib
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import json

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, adjusted_rand_score, calinski_harabasz_score
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd


@dataclass
class ClusteringResult:
    """Results from clustering analysis."""
    algorithm: str
    n_clusters: int
    labels: List[int]
    centroids: Optional[np.ndarray]
    silhouette_score: float
    calinski_harabasz_score: float
    inertia: Optional[float]
    ari_vs_previous: Optional[float]
    feature_importance: Dict[str, float]
    timestamp: float
    pipeline_version: str


@dataclass 
class FeaturePipelineMetadata:
    """Metadata for a frozen feature pipeline."""
    pipeline_id: str
    version: str
    description: str
    input_features: List[str]
    output_features: List[str]
    creation_date: float
    sklearn_version: str
    parameter_hash: str


class NFLFeatureExtractor(BaseEstimator, TransformerMixin):
    """Custom feature extractor for NFL play data."""
    
    def __init__(self, include_situational: bool = True, include_historical: bool = True):
        self.include_situational = include_situational
        self.include_historical = include_historical
        self.fitted_columns = None
    
    def fit(self, X, y=None):
        """Fit the feature extractor."""
        if isinstance(X, pd.DataFrame):
            self.fitted_columns = X.columns.tolist()
        return self
    
    def transform(self, X):
        """Transform play data into feature vectors."""
        if isinstance(X, dict):
            X = pd.DataFrame([X])
        elif not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        
        features = []
        
        if self.include_situational:
            # Situational features
            features.extend([
                X.get('down', 1),
                X.get('distance', 10),
                X.get('field_position', 50),
                X.get('quarter', 1),
                X.get('time_remaining', 3600),
                X.get('score_differential', 0),
                int(X.get('is_redzone', False)),
                int(X.get('is_two_minute_warning', False)),
                X.get('timeouts_remaining', 3)
            ])
        
        if self.include_historical:
            # Historical/tendency features
            features.extend([
                X.get('team_rushing_avg', 0),
                X.get('team_passing_avg', 0),
                X.get('opponent_defense_rating', 0.5),
                X.get('weather_impact', 0),
                X.get('home_field_advantage', 0)
            ])
        
        return np.array(features).reshape(1, -1) if len(features) > 0 else np.array([]).reshape(1, -1)


class FeaturePipelineManager:
    """Manages frozen feature pipelines for reproducibility."""
    
    def __init__(self, storage_path: str = "features/pipelines"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.pipelines: Dict[str, Pipeline] = {}
        self.metadata: Dict[str, FeaturePipelineMetadata] = {}
        self.logger = logging.getLogger(__name__)
        
        # Load existing pipelines
        self._load_pipelines()
    
    def create_pipeline(self, pipeline_id: str, description: str, 
                       steps: List[Tuple[str, Any]], version: str = "1.0") -> Pipeline:
        """Create and freeze a new feature pipeline."""
        pipeline = Pipeline(steps)
        
        # Generate parameter hash for reproducibility
        import hashlib
        param_str = str(pipeline.get_params())
        parameter_hash = hashlib.md5(param_str.encode()).hexdigest()[:16]
        
        # Create metadata
        metadata = FeaturePipelineMetadata(
            pipeline_id=pipeline_id,
            version=version,
            description=description,
            input_features=[],  # Will be populated when fitted
            output_features=[],  # Will be populated when fitted
            creation_date=time.time(),
            sklearn_version=self._get_sklearn_version(),
            parameter_hash=parameter_hash
        )
        
        self.pipelines[pipeline_id] = pipeline
        self.metadata[pipeline_id] = metadata
        
        # Save to disk
        self._save_pipeline(pipeline_id)
        
        self.logger.info(f"Created feature pipeline '{pipeline_id}' version {version}")
        return pipeline
    
    def create_default_nfl_pipeline(self) -> Pipeline:
        """Create default NFL feature processing pipeline."""
        steps = [
            ('feature_extractor', NFLFeatureExtractor()),
            ('scaler', StandardScaler()),
            ('pca', PCA(n_components=0.95))  # Keep 95% of variance
        ]
        
        return self.create_pipeline(
            pipeline_id="nfl_default",
            description="Standard NFL play feature extraction with scaling and PCA",
            steps=steps,
            version="1.0"
        )
    
    def fit_pipeline(self, pipeline_id: str, X, y=None) -> bool:
        """Fit a pipeline and update metadata."""
        if pipeline_id not in self.pipelines:
            return False
        
        try:
            pipeline = self.pipelines[pipeline_id]
            pipeline.fit(X, y)
            
            # Update metadata with feature information
            if hasattr(X, 'columns'):
                self.metadata[pipeline_id].input_features = X.columns.tolist()
            
            # Try to determine output feature names
            if hasattr(pipeline, 'get_feature_names_out'):
                try:
                    output_features = pipeline.get_feature_names_out()
                    self.metadata[pipeline_id].output_features = output_features.tolist()
                except:
                    pass
            
            # Save updated pipeline
            self._save_pipeline(pipeline_id)
            
            self.logger.info(f"Fitted pipeline '{pipeline_id}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fit pipeline '{pipeline_id}': {e}")
            return False
    
    def transform(self, pipeline_id: str, X) -> Optional[np.ndarray]:
        """Transform data using a fitted pipeline."""
        if pipeline_id not in self.pipelines:
            self.logger.error(f"Pipeline '{pipeline_id}' not found")
            return None
        
        try:
            return self.pipelines[pipeline_id].transform(X)
        except Exception as e:
            self.logger.error(f"Transform failed for pipeline '{pipeline_id}': {e}")
            return None
    
    def get_pipeline_info(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a pipeline."""
        if pipeline_id not in self.metadata:
            return None
        
        metadata = self.metadata[pipeline_id]
        pipeline = self.pipelines[pipeline_id]
        
        return {
            "metadata": asdict(metadata),
            "is_fitted": self._is_pipeline_fitted(pipeline),
            "steps": [step[0] for step in pipeline.steps]
        }
    
    def _save_pipeline(self, pipeline_id: str):
        """Save pipeline and metadata to disk."""
        try:
            # Save pipeline
            pipeline_path = self.storage_path / f"{pipeline_id}_pipeline.pkl"
            joblib.dump(self.pipelines[pipeline_id], pipeline_path)
            
            # Save metadata
            metadata_path = self.storage_path / f"{pipeline_id}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(asdict(self.metadata[pipeline_id]), f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save pipeline '{pipeline_id}': {e}")
    
    def _load_pipelines(self):
        """Load existing pipelines from disk."""
        for pipeline_file in self.storage_path.glob("*_pipeline.pkl"):
            try:
                pipeline_id = pipeline_file.stem.replace("_pipeline", "")
                
                # Load pipeline
                pipeline = joblib.load(pipeline_file)
                self.pipelines[pipeline_id] = pipeline
                
                # Load metadata
                metadata_file = self.storage_path / f"{pipeline_id}_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata_dict = json.load(f)
                    self.metadata[pipeline_id] = FeaturePipelineMetadata(**metadata_dict)
                
                self.logger.info(f"Loaded pipeline '{pipeline_id}'")
                
            except Exception as e:
                self.logger.error(f"Failed to load pipeline from {pipeline_file}: {e}")
    
    def _is_pipeline_fitted(self, pipeline: Pipeline) -> bool:
        """Check if a pipeline has been fitted."""
        try:
            # Try to access fitted attributes
            for step_name, step in pipeline.steps:
                if hasattr(step, 'n_features_in_'):
                    return True
            return False
        except:
            return False
    
    def _get_sklearn_version(self) -> str:
        """Get sklearn version."""
        import sklearn
        return sklearn.__version__


class ClusteringManager:
    """Manages clustering with quality metrics and persistence."""
    
    def __init__(self, storage_path: str = "features/clusters"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.clustering_history: List[ClusteringResult] = []
        self.logger = logging.getLogger(__name__)
        
        # Load historical results
        self._load_clustering_history()
    
    def perform_clustering(self, features: np.ndarray, algorithm: str = "kmeans", 
                         n_clusters: Optional[int] = None, **kwargs) -> ClusteringResult:
        """Perform clustering with comprehensive quality metrics."""
        
        if algorithm.lower() == "kmeans":
            clusterer = self._setup_kmeans(features, n_clusters, **kwargs)
        elif algorithm.lower() == "dbscan":
            clusterer = self._setup_dbscan(features, **kwargs)
        else:
            raise ValueError(f"Unsupported clustering algorithm: {algorithm}")
        
        # Fit the clusterer
        labels = clusterer.fit_predict(features)
        
        # Compute quality metrics
        metrics = self._compute_clustering_metrics(features, labels, clusterer)
        
        # Compute ARI vs previous clustering if available
        ari_vs_previous = None
        if self.clustering_history:
            previous_labels = self.clustering_history[-1].labels
            if len(previous_labels) == len(labels):
                ari_vs_previous = adjusted_rand_score(previous_labels, labels)
        
        # Feature importance analysis
        feature_importance = self._compute_feature_importance(features, labels)
        
        # Create result
        result = ClusteringResult(
            algorithm=algorithm.lower(),
            n_clusters=len(np.unique(labels[labels >= 0])),  # Exclude noise points (-1) for DBSCAN
            labels=labels.tolist(),
            centroids=clusterer.cluster_centers_ if hasattr(clusterer, 'cluster_centers_') else None,
            silhouette_score=metrics['silhouette'],
            calinski_harabasz_score=metrics['calinski_harabasz'],
            inertia=metrics.get('inertia'),
            ari_vs_previous=ari_vs_previous,
            feature_importance=feature_importance,
            timestamp=time.time(),
            pipeline_version="1.0"  # Should be linked to actual pipeline version
        )
        
        # Store result
        self.clustering_history.append(result)
        self._save_clustering_result(result)
        
        self.logger.info(f"Clustering completed: {algorithm} with {result.n_clusters} clusters "
                        f"(silhouette: {result.silhouette_score:.3f})")
        
        return result
    
    def _setup_kmeans(self, features: np.ndarray, n_clusters: Optional[int], **kwargs) -> KMeans:
        """Setup KMeans clustering."""
        if n_clusters is None:
            # Auto-determine optimal k using elbow method
            n_clusters = self._find_optimal_k(features)
        
        return KMeans(
            n_clusters=n_clusters,
            random_state=42,  # For reproducibility
            n_init=10,
            **kwargs
        )
    
    def _setup_dbscan(self, features: np.ndarray, **kwargs) -> DBSCAN:
        """Setup DBSCAN clustering."""
        # Default parameters if not provided
        eps = kwargs.get('eps', 0.5)
        min_samples = kwargs.get('min_samples', 5)
        
        return DBSCAN(eps=eps, min_samples=min_samples)
    
    def _find_optimal_k(self, features: np.ndarray, max_k: int = 20) -> int:
        """Find optimal number of clusters using elbow method."""
        if len(features) < 10:
            return 2
        
        max_k = min(max_k, len(features) // 2)
        inertias = []
        
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(features)
            inertias.append(kmeans.inertia_)
        
        # Simple elbow detection (could be improved)
        if len(inertias) < 3:
            return 2
        
        # Find the point with maximum curvature
        diffs = np.diff(inertias)
        second_diffs = np.diff(diffs)
        
        if len(second_diffs) > 0:
            elbow_point = np.argmax(second_diffs) + 2  # +2 because we started from k=2
            return min(elbow_point, max_k)
        
        return len(inertias) // 2 + 2
    
    def _compute_clustering_metrics(self, features: np.ndarray, labels: np.ndarray, 
                                  clusterer) -> Dict[str, float]:
        """Compute comprehensive clustering quality metrics."""
        metrics = {}
        
        # Remove noise points for metric calculation
        valid_mask = labels >= 0
        valid_features = features[valid_mask]
        valid_labels = labels[valid_mask]
        
        if len(np.unique(valid_labels)) > 1 and len(valid_labels) > 1:
            # Silhouette score
            metrics['silhouette'] = silhouette_score(valid_features, valid_labels)
            
            # Calinski-Harabasz score
            metrics['calinski_harabasz'] = calinski_harabasz_score(valid_features, valid_labels)
        else:
            metrics['silhouette'] = -1.0
            metrics['calinski_harabasz'] = 0.0
        
        # Inertia for KMeans
        if hasattr(clusterer, 'inertia_'):
            metrics['inertia'] = clusterer.inertia_
        
        return metrics
    
    def _compute_feature_importance(self, features: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """Compute feature importance for clustering."""
        if len(np.unique(labels[labels >= 0])) < 2:
            return {}
        
        # Use variance ratio as a simple feature importance measure
        feature_importance = {}
        
        for i in range(features.shape[1]):
            feature_values = features[:, i]
            
            # Between-cluster variance vs within-cluster variance
            between_var = 0.0
            within_var = 0.0
            total_mean = np.mean(feature_values)
            
            unique_labels = np.unique(labels[labels >= 0])
            
            for label in unique_labels:
                cluster_mask = labels == label
                cluster_values = feature_values[cluster_mask]
                
                if len(cluster_values) > 0:
                    cluster_mean = np.mean(cluster_values)
                    cluster_size = len(cluster_values)
                    
                    between_var += cluster_size * (cluster_mean - total_mean) ** 2
                    within_var += np.sum((cluster_values - cluster_mean) ** 2)
            
            # Feature importance as ratio of between to within variance
            if within_var > 0:
                importance = between_var / within_var
            else:
                importance = 0.0
            
            feature_importance[f"feature_{i}"] = importance
        
        return feature_importance
    
    def get_cluster_analysis(self) -> Dict[str, Any]:
        """Get comprehensive cluster analysis."""
        if not self.clustering_history:
            return {}
        
        recent_results = self.clustering_history[-5:]  # Last 5 clusterings
        
        analysis = {
            "total_clusterings": len(self.clustering_history),
            "recent_results": [asdict(result) for result in recent_results],
            "best_silhouette": max(result.silhouette_score for result in self.clustering_history),
            "average_clusters": np.mean([result.n_clusters for result in self.clustering_history]),
            "algorithm_usage": {}
        }
        
        # Algorithm usage statistics
        for result in self.clustering_history:
            alg = result.algorithm
            if alg not in analysis["algorithm_usage"]:
                analysis["algorithm_usage"][alg] = 0
            analysis["algorithm_usage"][alg] += 1
        
        return analysis
    
    def _save_clustering_result(self, result: ClusteringResult):
        """Save clustering result to disk."""
        try:
            timestamp_str = str(int(result.timestamp))
            file_path = self.storage_path / f"clustering_{result.algorithm}_{timestamp_str}.json"
            
            # Convert numpy arrays to lists for JSON serialization
            result_dict = asdict(result)
            if result_dict['centroids'] is not None:
                result_dict['centroids'] = result.centroids.tolist()
            
            with open(file_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save clustering result: {e}")
    
    def _load_clustering_history(self):
        """Load clustering history from disk."""
        for result_file in sorted(self.storage_path.glob("clustering_*.json")):
            try:
                with open(result_file, 'r') as f:
                    result_dict = json.load(f)
                
                # Convert centroids back to numpy array
                if result_dict['centroids'] is not None:
                    result_dict['centroids'] = np.array(result_dict['centroids'])
                
                result = ClusteringResult(**result_dict)
                self.clustering_history.append(result)
                
            except Exception as e:
                self.logger.error(f"Failed to load clustering result from {result_file}: {e}")