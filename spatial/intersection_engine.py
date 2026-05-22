import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from typing import List, Dict, Any

class SpatialIntersectionEngine:
    """
    Handles geometric intersections between surface parcels and subsurface mineral zones.
    """

    def __init__(self, crs: str = "EPSG:4326"):
        self.target_crs = crs

    def normalize_gdf(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Normalizes a GeoDataFrame to a unified coordinate reference system.
        """
        if gdf.crs != self.target_crs:
            gdf = gdf.to_crs(self.target_crs)
        return gdf

    def find_intersections(self, parcels_gdf: gpd.GeoDataFrame, zones_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Calculates the geometric intersection between county parcel polygons (surface)
        and USGS-defined probable mineral zones (subsurface).

        Uses a spatial join (sjoin) to find overlapping geometries.
        """
        parcels_gdf = self.normalize_gdf(parcels_gdf)
        zones_gdf = self.normalize_gdf(zones_gdf)

        # Spatial join: keep parcels that intersect with geological zones
        intersected = gpd.sjoin(parcels_gdf, zones_gdf, how="inner", predicate="intersects")
        return intersected

    def evaluate_severance_check(self, intersection_row: Any, deed_history: List[Dict[str, Any]]) -> bool:
        """
        The Severance Check:
        If a parcel overlaps a high-probability mineral zone AND the associated deed history
        indicates a historical mineral severance without a recent corporate lease attachment,
        flag this parcel as a high-value anomaly.

        :param intersection_row: A row from the intersected GeoDataFrame.
        :param deed_history: List of parsed deed dictionaries for the parcel.
        :return: True if it's a high-value anomaly, False otherwise.
        """
        # Assume the intersection indicates it overlaps a high-probability mineral zone
        # Now we check the deed history

        has_severance = False
        has_active_lease = False

        for deed in deed_history:
            if deed.get("is_mineral_severed"):
                has_severance = True
            if deed.get("has_active_lease"):
                has_active_lease = True

        # High value if severed but NOT actively leased by a corporation
        if has_severance and not has_active_lease:
            return True

        return False

if __name__ == "__main__":
    # Example usage / Mock data
    pass
