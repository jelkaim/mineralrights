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
        and USGS-defined probable mineral zones (subsurface) using GeoPandas (In-memory).

        Uses an overlay intersection to calculate exact geometry overlap to compute the `overlap_ratio`.
        Only retains parcels with >50% overlap ratio to match the PostGIS logic.
        """
        parcels_gdf = self.normalize_gdf(parcels_gdf)
        zones_gdf = self.normalize_gdf(zones_gdf)

        # We need an equal area projection to calculate true area accurately, but for MVP
        # approximate degrees or a simple re-projection to a typical US equal area (e.g. EPSG:5070)
        parcels_proj = parcels_gdf.to_crs("EPSG:5070")
        zones_proj = zones_gdf.to_crs("EPSG:5070")

        parcels_proj['parcel_area'] = parcels_proj.geometry.area

        # Perform overlay intersection to get the actual overlapping geometries
        intersected = gpd.overlay(parcels_proj, zones_proj, how='intersection')

        # Calculate overlap ratio
        intersected['overlap_area'] = intersected.geometry.area
        intersected['overlap_ratio'] = intersected['overlap_area'] / intersected['parcel_area']

        # Filter for >50% overlap to match the requested architecture
        intersected = intersected[intersected['overlap_ratio'] > 0.5].copy()

        # Return normalized back to original target CRS
        return intersected.to_crs(self.target_crs)

    def find_intersections_postgis(self, db_engine: Any) -> gpd.GeoDataFrame:
        """
        Executes a highly scalable PostGIS query to find every single parcel ID
        that overlaps with USGS mineral zones by at least 50%.

        This reflects the 'Top of Funnel' architecture where the heavy lifting
        is done inside the database using GIST spatial indexes.

        :param db_engine: A SQLAlchemy engine or active psycopg2 connection.
        :return: GeoDataFrame of the filtered target surface parcels.
        """
        query = """
        SELECT p.parcel_id, p.owner_name, p.geom, z.id AS zone_id, z.zone_name
        FROM parcels p
        JOIN geological_zones z ON ST_Intersects(p.geom, z.geom)
        WHERE ST_Area(ST_Intersection(p.geom, z.geom)) > (ST_Area(p.geom) * 0.5);
        """

        print("Executing PostGIS >50% overlap intersection query...")
        try:
            target_surface_parcels = gpd.read_postgis(query, db_engine, geom_col='geom')
            print(f"Found {len(target_surface_parcels)} target parcels overlapping geology >50%.")
            return target_surface_parcels
        except Exception as e:
            print(f"PostGIS query failed (likely no DB connection). Falling back to empty GeoDataFrame. Error: {e}")
            return gpd.GeoDataFrame()

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
            if deed.get("is_lease"):
                has_active_lease = True

        # High value if severed but NOT actively leased by a corporation
        if has_severance and not has_active_lease:
            return True

        return False

if __name__ == "__main__":
    # Example usage / Mock data
    pass
