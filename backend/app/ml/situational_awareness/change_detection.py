"""
AI-DisasterGuard — Real-Time Change Detection Subsystem
Phase 6: Configurable Thresholds, Cooldown Management, and Delta Evaluation
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("disasterguard.ml.situational_awareness.change_detection")


class ChangeDetector:
    """
    Evaluates real-time state deltas against historical/cached snapshots.
    Enforces cooldown windows and significance thresholds to prevent noise.
    """

    def __init__(
        self,
        risk_score_delta_threshold: float = 5.0,
        cooldown_seconds_default: int = 120,
        cooldown_seconds_critical: int = 30,
    ):
        self.risk_score_delta_threshold = risk_score_delta_threshold
        self.cooldown_seconds_default = cooldown_seconds_default
        self.cooldown_seconds_critical = cooldown_seconds_critical
        self._last_event_timestamps: Dict[str, datetime] = {}

    def _is_cooling_down(self, event_key: str, is_critical: bool = False) -> bool:
        """Check if an event key is within its debouncing/cooldown window."""
        now = datetime.now(timezone.utc)
        last_time = self._last_event_timestamps.get(event_key)
        if not last_time:
            return False

        cooldown = self.cooldown_seconds_critical if is_critical else self.cooldown_seconds_default
        if (now - last_time).total_seconds() < cooldown:
            return True
        return False

    def _record_event(self, event_key: str) -> None:
        """Record the timestamp of an emitted change event."""
        self._last_event_timestamps[event_key] = datetime.now(timezone.utc)

    def evaluate_changes(
        self,
        current_state: Dict[str, Any],
        previous_state: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Compare current system state with previous state to detect significant operational changes.
        Returns a list of structured change event dictionaries.
        """
        changes: List[Dict[str, Any]] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        if not previous_state:
            # First snapshot after boot
            changes.append({
                "timestamp": now_iso,
                "source": "SYSTEM",
                "severity": "INFO",
                "title": "Situational Baseline Established",
                "description": f"Initial operational snapshot captured with risk score {current_state.get('risk_score', 0):.1f} ({current_state.get('overall_status', 'NORMAL')}).",
                "confidence": 0.95,
                "freshness": "LIVE",
                "data_provenance": current_state.get("data_provenance", "REAL"),
                "event_type": "SITUATION_UPDATED",
            })
            return changes

        # 1. Risk Score Delta Evaluation
        curr_risk = float(current_state.get("risk_score", 0.0))
        prev_risk = float(previous_state.get("risk_score", 0.0))
        risk_diff = curr_risk - prev_risk

        if abs(risk_diff) >= self.risk_score_delta_threshold:
            event_key = f"risk_score_delta_{round(curr_risk / 10)}"
            is_critical = curr_risk >= 75.0 or risk_diff >= 15.0
            if not self._is_cooling_down(event_key, is_critical):
                direction = "surged" if risk_diff > 0 else "decreased"
                severity = "CRITICAL" if curr_risk >= 75 else ("HIGH" if curr_risk >= 50 else "MODERATE")
                changes.append({
                    "timestamp": now_iso,
                    "source": "ML_PREDICTION",
                    "severity": severity,
                    "title": f"Regional Risk Score {direction.capitalize()}",
                    "description": f"Risk score shifted from {prev_risk:.1f} → {curr_risk:.1f} (delta: {risk_diff:+.1f}). Direction: {current_state.get('risk_direction', 'STABLE')}.",
                    "confidence": 0.91,
                    "freshness": "LIVE",
                    "data_provenance": "DERIVED",
                    "event_type": "RISK_CHANGE_DETECTED",
                })
                self._record_event(event_key)

        # 2. Critical Incidents Changes
        curr_crit = int(current_state.get("critical_incidents", 0))
        prev_crit = int(previous_state.get("critical_incidents", 0))
        if curr_crit != prev_crit:
            event_key = f"critical_incidents_{curr_crit}"
            is_critical = curr_crit > prev_crit
            if not self._is_cooling_down(event_key, is_critical):
                action = "escalated" if curr_crit > prev_crit else "resolved/reduced"
                changes.append({
                    "timestamp": now_iso,
                    "source": "OPERATIONS",
                    "severity": "CRITICAL" if curr_crit > 0 else "INFO",
                    "title": f"Critical Incident Load {action.capitalize()}",
                    "description": f"Active critical emergencies changed from {prev_crit} → {curr_crit}.",
                    "confidence": 0.95,
                    "freshness": "LIVE",
                    "data_provenance": "REAL",
                    "event_type": "INCIDENT_PRIORITY_UPDATED",
                })
                self._record_event(event_key)

        # 3. Resource Contention Appearing or Disappearing
        curr_contentions = int(current_state.get("resource_contentions", 0))
        prev_contentions = int(previous_state.get("resource_contentions", 0))
        if curr_contentions != prev_contentions:
            event_key = f"contentions_{curr_contentions}"
            if not self._is_cooling_down(event_key, is_critical=True):
                if curr_contentions > prev_contentions:
                    changes.append({
                        "timestamp": now_iso,
                        "source": "RESOURCE_OPTIMIZER",
                        "severity": "HIGH",
                        "title": "New Resource Contention Detected",
                        "description": f"{curr_contentions} operational resource conflict(s) currently detected between active emergency requests.",
                        "confidence": 0.93,
                        "freshness": "LIVE",
                        "data_provenance": "DERIVED",
                        "event_type": "RESOURCE_CONTENTION_DETECTED",
                    })
                else:
                    changes.append({
                        "timestamp": now_iso,
                        "source": "RESOURCE_OPTIMIZER",
                        "severity": "INFO",
                        "title": "Resource Contention Resolved",
                        "description": f"Resource contention load reduced to {curr_contentions} active conflict(s).",
                        "confidence": 0.93,
                        "freshness": "LIVE",
                        "data_provenance": "DERIVED",
                        "event_type": "RESOURCE_CONTENTION_UPDATED",
                    })
                self._record_event(event_key)

        # 4. Operational Bottlenecks
        curr_bottlenecks = int(current_state.get("operational_bottlenecks", 0))
        prev_bottlenecks = int(previous_state.get("operational_bottlenecks", 0))
        if curr_bottlenecks != prev_bottlenecks:
            event_key = f"bottlenecks_{curr_bottlenecks}"
            if not self._is_cooling_down(event_key, is_critical=True):
                severity = "HIGH" if curr_bottlenecks > 0 else "INFO"
                changes.append({
                    "timestamp": now_iso,
                    "source": "OPERATIONS",
                    "severity": severity,
                    "title": "System Operational Bottleneck Shift",
                    "description": f"Active capacity bottlenecks updated: {curr_bottlenecks} detected across rescue, shelter, or trauma facilities.",
                    "confidence": 0.90,
                    "freshness": "LIVE",
                    "data_provenance": "DERIVED",
                    "event_type": "OPERATIONAL_BOTTLENECK_DETECTED",
                })
                self._record_event(event_key)

        # 5. Active Public Warnings / Alerts
        curr_alerts = int(current_state.get("active_alerts", 0))
        prev_alerts = int(previous_state.get("active_alerts", 0))
        if curr_alerts != prev_alerts:
            event_key = f"alerts_{curr_alerts}"
            if not self._is_cooling_down(event_key, is_critical=False):
                changes.append({
                    "timestamp": now_iso,
                    "source": "ADAPTIVE_ALERTS",
                    "severity": "HIGH" if curr_alerts > prev_alerts else "INFO",
                    "title": "Public Warning Posture Updated",
                    "description": f"Active emergency alerts count changed from {prev_alerts} → {curr_alerts}.",
                    "confidence": 0.96,
                    "freshness": "LIVE",
                    "data_provenance": "REAL",
                    "event_type": "ALERT_UPDATED",
                })
                self._record_event(event_key)

        return changes

    @staticmethod
    def calculate_freshness(timestamp: Optional[datetime]) -> str:
        """Categorize data freshness based on age."""
        if not timestamp:
            return "STALE"
        now = datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age_seconds = (now - timestamp).total_seconds()
        if age_seconds < 60:
            return "LIVE"
        elif age_seconds < 300:
            return "< 5 MIN"
        elif age_seconds < 900:
            return "15 MIN OLD"
        else:
            return "STALE"
