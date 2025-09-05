"""
Clustering Example with scikit-learn and HDBSCAN

Cluster play sequences or player embeddings for tagging and meta-learning.
"""

from sklearn.cluster import KMeans
import hdbscan

def cluster_data_kmeans(X, num_clusters=5):
    kmeans = KMeans(n_clusters=num_clusters)
    labels = kmeans.fit_predict(X)
    return labels

def cluster_data_hdbscan(X):
    clusterer = hdbscan.HDBSCAN()
    labels = clusterer.fit_predict(X)
    return labels
