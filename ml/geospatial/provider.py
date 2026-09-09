"""
Geospatial Provider Base Architecture and Provenance Standards.
Enforces strict scientific honesty regarding data sources, resolution, and limitations.
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class DataSourceType(str, Enum):
    REAL_OBSERVED = "REAL_OBSERVED"
    REAL_REANALYSIS = "REAL_REANALYSIS"
    REAL_GEOSPATIAL = "REAL_GEOSPATIAL"
    HISTORICAL_EVENT = "HISTORICAL_EVENT"
    DERIVED = "DERIVED"
    SIMULATION = "SIMULATION"
    SYNTHETIC = "SYNTHETIC"
    MOCK = "MOCK"

class SpatialConfidence:
    def __init__(self, score: float, description: str, basis: str):
        self.score = round(max(0.0, min(1.0, score)), 2)
        self.description = description
        self.basis = basis

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "description": self.description,
            "basis": self.basis
        }

class GeospatialProvenance:
    def __init__(
        self,
        provider_name: str,
        source_type: DataSourceType,
        dataset_name: str,
        resolution: str,
        confidence: float,
        limitations: str,
        citation: Optional[str] = None
    ):
        self.provider_name = provider_name
        self.source_type = source_type.value if isinstance(source_type, DataSourceType) else str(source_type)
        self.dataset_name = dataset_name
        self.resolution = resolution
        self.confidence = confidence
        self.limitations = limitations
        self.citation = citation
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "source_type": self.source_type,
            "dataset": self.dataset_name,
            "resolution": self.resolution,
            "confidence": self.confidence,
            "limitations": self.limitations,
            "citation": self.citation,
            "timestamp": self.timestamp
        }

class BaseGeospatialProvider:
    """Abstract interface for geospatial feature and intelligence providers."""

    def __init__(self, name: str, default_mode: str = "DERIVED"):
        self.name = name
        self.mode = default_mode

    def get_provenance(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement get_provenance")
