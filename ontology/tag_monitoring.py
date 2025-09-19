"""
Tag confidence calibration and drift monitoring system.
Tracks tag confidence accuracy and distributional changes over time.
"""
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
import json
from pathlib import Path

from ontology.version_manager import TagInstance, OntologyManager


@dataclass
class ConfidenceCalibration:
    """Calibration analysis for tag confidence."""
    tag_name: str
    confidence_bins: List[Tuple[float, float]]  # (predicted_conf, actual_accuracy)
    bin_counts: List[int]
    overall_accuracy: float
    brier_score: float
    calibration_error: float
    reliability_score: float
    timestamp: float


@dataclass
class TagDriftMetrics:
    """Metrics for tracking tag drift over time."""
    tag_name: str
    time_window_start: float
    time_window_end: float
    confidence_distribution_current: Dict[str, float]  # binned confidence distribution
    confidence_distribution_baseline: Dict[str, float]
    js_divergence: float  # Jensen-Shannon divergence
    kl_divergence: float  # Kullback-Leibler divergence
    confidence_mean_shift: float
    confidence_std_shift: float
    usage_frequency_change: float
    drift_severity: str  # "low", "medium", "high"


class TagConfidenceManager:
    """Manages tag confidence calibration and drift detection."""
    
    def __init__(self, storage_path: str = "logs/tag_analysis", 
                 ontology_manager: Optional[OntologyManager] = None):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.ontology_manager = ontology_manager or OntologyManager()
        self.logger = logging.getLogger(__name__)
        
        # Tag instance storage
        self.tag_instances: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.calibration_history: Dict[str, List[ConfidenceCalibration]] = defaultdict(list)
        self.drift_history: Dict[str, List[TagDriftMetrics]] = defaultdict(list)
        
        # Configuration
        self.confidence_bins = [(i/10, (i+1)/10) for i in range(10)]  # 0.0-0.1, 0.1-0.2, etc.
        self.drift_window_size = 1000  # Number of instances for drift analysis
        self.calibration_update_frequency = 100  # Update calibration every N instances
        
        # Load existing data
        self._load_historical_data()
    
    def record_tag_instance(self, tag_instance: TagInstance, ground_truth: Optional[bool] = None):
        """Record a new tag instance with optional ground truth for calibration."""
        # Validate tag exists in current ontology
        current_tags = self.ontology_manager.get_current_tags()
        if tag_instance.tag_name not in current_tags:
            self.logger.warning(f"Tag {tag_instance.tag_name} not found in current ontology")
            return
        
        # Validate confidence range
        if not self.ontology_manager.validate_tag_confidence(tag_instance.tag_name, tag_instance.confidence):
            self.logger.warning(f"Confidence {tag_instance.confidence} outside expected range for {tag_instance.tag_name}")
        
        # Store instance
        enhanced_instance = asdict(tag_instance)
        enhanced_instance['ground_truth'] = ground_truth
        
        self.tag_instances[tag_instance.tag_name].append(enhanced_instance)
        
        # Trigger calibration update if enough instances
        if len(self.tag_instances[tag_instance.tag_name]) % self.calibration_update_frequency == 0:
            self._update_calibration(tag_instance.tag_name)
        
        # Trigger drift analysis if enough instances
        if len(self.tag_instances[tag_instance.tag_name]) >= self.drift_window_size:
            self._update_drift_analysis(tag_instance.tag_name)
    
    def _update_calibration(self, tag_name: str):
        """Update calibration analysis for a specific tag."""
        instances = list(self.tag_instances[tag_name])
        
        # Filter instances with ground truth
        labeled_instances = [inst for inst in instances if inst.get('ground_truth') is not None]
        
        if len(labeled_instances) < 20:  # Need minimum instances for calibration
            return
        
        # Compute calibration metrics
        calibration = self._compute_calibration_metrics(tag_name, labeled_instances)
        self.calibration_history[tag_name].append(calibration)
        
        # Log significant calibration issues
        if calibration.calibration_error > 0.2:
            self.logger.warning(f"High calibration error for {tag_name}: {calibration.calibration_error:.3f}")
        
        # Persist calibration data
        self._save_calibration(calibration)
    
    def _compute_calibration_metrics(self, tag_name: str, instances: List[Dict]) -> ConfidenceCalibration:
        """Compute detailed calibration metrics for a tag."""
        confidences = np.array([inst['confidence'] for inst in instances])
        ground_truths = np.array([float(inst['ground_truth']) for inst in instances])
        
        # Bin-based calibration
        bin_data = []
        bin_counts = []
        
        for bin_start, bin_end in self.confidence_bins:
            bin_mask = (confidences >= bin_start) & (confidences < bin_end)
            bin_instances = confidences[bin_mask]
            bin_truths = ground_truths[bin_mask]
            
            if len(bin_instances) > 0:
                avg_confidence = np.mean(bin_instances)
                avg_accuracy = np.mean(bin_truths)
                bin_data.append((avg_confidence, avg_accuracy))
                bin_counts.append(len(bin_instances))
            else:
                bin_data.append((0.0, 0.0))
                bin_counts.append(0)
        
        # Overall accuracy
        overall_accuracy = np.mean(ground_truths)
        
        # Brier score (lower is better)
        brier_score = np.mean((confidences - ground_truths) ** 2)
        
        # Calibration error (Expected Calibration Error)
        calibration_error = 0.0
        total_instances = len(instances)
        
        for (avg_conf, avg_acc), count in zip(bin_data, bin_counts):
            if count > 0:
                calibration_error += (count / total_instances) * abs(avg_conf - avg_acc)
        
        # Reliability score (how much predictions and outcomes align)
        reliability_score = np.corrcoef(confidences, ground_truths)[0, 1] if len(instances) > 1 else 0.0
        
        return ConfidenceCalibration(
            tag_name=tag_name,
            confidence_bins=bin_data,
            bin_counts=bin_counts,
            overall_accuracy=overall_accuracy,
            brier_score=brier_score,
            calibration_error=calibration_error,
            reliability_score=reliability_score,
            timestamp=time.time()
        )
    
    def _update_drift_analysis(self, tag_name: str):
        """Update drift analysis for a specific tag."""
        instances = list(self.tag_instances[tag_name])
        
        if len(instances) < self.drift_window_size:
            return
        
        # Split into baseline (older) and current (newer) windows
        split_point = len(instances) - self.drift_window_size // 2
        baseline_instances = instances[:split_point]
        current_instances = instances[split_point:]
        
        if len(baseline_instances) < 100 or len(current_instances) < 100:
            return
        
        drift_metrics = self._compute_drift_metrics(tag_name, baseline_instances, current_instances)
        self.drift_history[tag_name].append(drift_metrics)
        
        # Log significant drift
        if drift_metrics.drift_severity in ["medium", "high"]:
            self.logger.warning(f"Tag drift detected for {tag_name}: {drift_metrics.drift_severity} "
                              f"(JS divergence: {drift_metrics.js_divergence:.3f})")
        
        # Persist drift data
        self._save_drift_metrics(drift_metrics)
    
    def _compute_drift_metrics(self, tag_name: str, baseline_instances: List[Dict], 
                             current_instances: List[Dict]) -> TagDriftMetrics:
        """Compute drift metrics between baseline and current distributions."""
        baseline_confs = np.array([inst['confidence'] for inst in baseline_instances])
        current_confs = np.array([inst['confidence'] for inst in current_instances])
        
        # Compute confidence distributions
        baseline_dist = self._compute_confidence_distribution(baseline_confs)
        current_dist = self._compute_confidence_distribution(current_confs)
        
        # Jensen-Shannon divergence
        js_divergence = self._jensen_shannon_divergence(baseline_dist, current_dist)
        
        # KL divergence (with smoothing to avoid infinities)
        kl_divergence = self._kl_divergence(baseline_dist, current_dist)
        
        # Mean and std shifts
        confidence_mean_shift = np.mean(current_confs) - np.mean(baseline_confs)
        confidence_std_shift = np.std(current_confs) - np.std(baseline_confs)
        
        # Usage frequency change (instances per unit time)
        baseline_time_span = baseline_instances[-1]['timestamp'] - baseline_instances[0]['timestamp']
        current_time_span = current_instances[-1]['timestamp'] - current_instances[0]['timestamp']
        
        baseline_freq = len(baseline_instances) / max(baseline_time_span, 1)
        current_freq = len(current_instances) / max(current_time_span, 1)
        usage_frequency_change = (current_freq - baseline_freq) / max(baseline_freq, 0.001)
        
        # Determine drift severity
        drift_severity = self._assess_drift_severity(js_divergence, abs(confidence_mean_shift), 
                                                   abs(usage_frequency_change))
        
        return TagDriftMetrics(
            tag_name=tag_name,
            time_window_start=baseline_instances[0]['timestamp'],
            time_window_end=current_instances[-1]['timestamp'],
            confidence_distribution_current=current_dist,
            confidence_distribution_baseline=baseline_dist,
            js_divergence=js_divergence,
            kl_divergence=kl_divergence,
            confidence_mean_shift=confidence_mean_shift,
            confidence_std_shift=confidence_std_shift,
            usage_frequency_change=usage_frequency_change,
            drift_severity=drift_severity
        )
    
    def _compute_confidence_distribution(self, confidences: np.ndarray) -> Dict[str, float]:
        """Compute binned confidence distribution."""
        hist, bin_edges = np.histogram(confidences, bins=10, range=(0, 1))
        hist = hist.astype(float)
        hist = hist / np.sum(hist)  # Normalize
        
        distribution = {}
        for i, (start, end) in enumerate(zip(bin_edges[:-1], bin_edges[1:])):
            distribution[f"{start:.1f}-{end:.1f}"] = hist[i]
        
        return distribution
    
    def _jensen_shannon_divergence(self, dist1: Dict[str, float], dist2: Dict[str, float]) -> float:
        """Compute Jensen-Shannon divergence between two distributions."""
        # Align distributions
        all_keys = set(dist1.keys()) | set(dist2.keys())
        p = np.array([dist1.get(k, 0) for k in sorted(all_keys)])
        q = np.array([dist2.get(k, 0) for k in sorted(all_keys)])
        
        # Add small epsilon to avoid log(0)
        epsilon = 1e-8
        p = p + epsilon
        q = q + epsilon
        
        # Normalize
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        # Compute JS divergence
        m = 0.5 * (p + q)
        js_div = 0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m))
        
        return js_div
    
    def _kl_divergence(self, dist1: Dict[str, float], dist2: Dict[str, float]) -> float:
        """Compute KL divergence D(dist1 || dist2)."""
        all_keys = set(dist1.keys()) | set(dist2.keys())
        p = np.array([dist1.get(k, 0) for k in sorted(all_keys)])
        q = np.array([dist2.get(k, 0) for k in sorted(all_keys)])
        
        # Add smoothing
        epsilon = 1e-8
        p = p + epsilon
        q = q + epsilon
        
        # Normalize
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        return np.sum(p * np.log(p / q))
    
    def _assess_drift_severity(self, js_divergence: float, mean_shift: float, 
                             freq_change: float) -> str:
        """Assess drift severity based on multiple metrics."""
        # Thresholds (tunable based on domain knowledge)
        high_js_threshold = 0.3
        medium_js_threshold = 0.1
        high_mean_threshold = 0.2
        medium_mean_threshold = 0.1
        high_freq_threshold = 0.5
        medium_freq_threshold = 0.2
        
        high_indicators = (
            js_divergence > high_js_threshold or
            mean_shift > high_mean_threshold or
            freq_change > high_freq_threshold
        )
        
        medium_indicators = (
            js_divergence > medium_js_threshold or
            mean_shift > medium_mean_threshold or
            freq_change > medium_freq_threshold
        )
        
        if high_indicators:
            return "high"
        elif medium_indicators:
            return "medium"
        else:
            return "low"
    
    def generate_calibration_plot_data(self, tag_name: str) -> Optional[Dict[str, Any]]:
        """Generate data for calibration plots."""
        if tag_name not in self.calibration_history or not self.calibration_history[tag_name]:
            return None
        
        latest_calibration = self.calibration_history[tag_name][-1]
        
        # Extract data for plotting
        predicted_probs = [bin_data[0] for bin_data in latest_calibration.confidence_bins]
        actual_freqs = [bin_data[1] for bin_data in latest_calibration.confidence_bins]
        bin_counts = latest_calibration.bin_counts
        
        return {
            "tag_name": tag_name,
            "predicted_probabilities": predicted_probs,
            "actual_frequencies": actual_freqs,
            "bin_counts": bin_counts,
            "overall_accuracy": latest_calibration.overall_accuracy,
            "brier_score": latest_calibration.brier_score,
            "calibration_error": latest_calibration.calibration_error,
            "reliability_score": latest_calibration.reliability_score,
            "timestamp": latest_calibration.timestamp
        }
    
    def get_drift_summary(self, tag_name: str, days_back: int = 30) -> Dict[str, Any]:
        """Get drift summary for a tag over specified time period."""
        if tag_name not in self.drift_history:
            return {}
        
        cutoff_time = time.time() - (days_back * 24 * 3600)
        recent_drift = [d for d in self.drift_history[tag_name] if d.time_window_end > cutoff_time]
        
        if not recent_drift:
            return {}
        
        return {
            "tag_name": tag_name,
            "drift_events": len(recent_drift),
            "high_severity_events": len([d for d in recent_drift if d.drift_severity == "high"]),
            "medium_severity_events": len([d for d in recent_drift if d.drift_severity == "medium"]),
            "avg_js_divergence": np.mean([d.js_divergence for d in recent_drift]),
            "avg_confidence_shift": np.mean([d.confidence_mean_shift for d in recent_drift]),
            "avg_frequency_change": np.mean([d.usage_frequency_change for d in recent_drift]),
            "latest_drift": asdict(recent_drift[-1]) if recent_drift else None
        }
    
    def get_all_tag_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health summary for all tags."""
        health_summary = {}
        
        for tag_name in self.tag_instances.keys():
            calibration_data = self.generate_calibration_plot_data(tag_name)
            drift_summary = self.get_drift_summary(tag_name)
            
            health_summary[tag_name] = {
                "total_instances": len(self.tag_instances[tag_name]),
                "calibration": calibration_data,
                "drift": drift_summary,
                "last_updated": max([inst['timestamp'] for inst in self.tag_instances[tag_name]]) 
                               if self.tag_instances[tag_name] else 0
            }
        
        return health_summary
    
    def _save_calibration(self, calibration: ConfidenceCalibration):
        """Save calibration data to disk."""
        try:
            file_path = self.storage_path / f"calibration_{calibration.tag_name}_{int(calibration.timestamp)}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(calibration), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save calibration for {calibration.tag_name}: {e}")
    
    def _save_drift_metrics(self, drift: TagDriftMetrics):
        """Save drift metrics to disk."""
        try:
            file_path = self.storage_path / f"drift_{drift.tag_name}_{int(drift.time_window_end)}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(drift), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save drift metrics for {drift.tag_name}: {e}")
    
    def _load_historical_data(self):
        """Load historical calibration and drift data."""
        # Implementation would load from disk
        # For now, we'll start fresh each time
        pass