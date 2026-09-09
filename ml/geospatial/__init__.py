"""
AI-DisasterGuard Geospatial Subsystem
Modular geospatial intelligence providers for terrain, drainage, and historical flood memory.
"""

from .provider import (
    DataSourceType,
    BaseGeospatialProvider,
    SpatialConfidence,
    GeospatialProvenance
)
from .terrain_provider import TerrainProvider
from .drainage_provider import DrainageProvider
from .historical_flood_provider import HistoricalFloodProvider
from .spatial_features import extract_spatial_features
from .susceptibility import calculate_flood_susceptibility
from .inundation import InundationEstimator

__all__ = [
    "DataSourceType",
    "BaseGeospatialProvider",
    "SpatialConfidence",
    "GeospatialProvenance",
    "TerrainProvider",
    "DrainageProvider",
    "HistoricalFloodProvider",
    "extract_spatial_features",
    "calculate_flood_susceptibility",
    "InundationEstimator",
]
