from typing import Dict, Any, List
from app.gis.geojson import create_feature_collection, create_inundation_polygon_feature

class InundationService:
    @staticmethod
    def get_inundation_geojson() -> Dict[str, Any]:
        """Generate GeoJSON FeatureCollection for Leaflet inundation map layers."""
        features = [
            create_inundation_polygon_feature(
                id_val="zone-alpha-1",
                name="Downtown Riverside Basin (Severe Spill)",
                coordinates_polygon=[
                    [80.265, 13.078],
                    [80.282, 13.078],
                    [80.282, 13.092],
                    [80.265, 13.092],
                    [80.265, 13.078]
                ],
                risk_level="CRITICAL",
                risk_score=92,
                water_depth=1.45,
                affected_population=14200
            ),
            create_inundation_polygon_feature(
                id_val="zone-beta-2",
                name="Northern Highway Slopes",
                coordinates_polygon=[
                    [80.280, 13.088],
                    [80.295, 13.088],
                    [80.295, 13.102],
                    [80.280, 13.102],
                    [80.280, 13.088]
                ],
                risk_level="HIGH",
                risk_score=76,
                water_depth=0.85,
                affected_population=3800
            )
        ]
        return create_feature_collection(features)

inundation_service = InundationService()
