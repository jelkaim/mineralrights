import geopandas as gpd
from typing import Optional

class ParcelLoader:
    """
    Ingests assessor parcel GIS data (Shapefiles/GeoJSON) into the system.
    """
    def __init__(self, db_connection_string: Optional[str] = None):
        self.db_connection_string = db_connection_string

    def load_parcels(self, filepath: str) -> gpd.GeoDataFrame:
        """
        Loads parcel data from a local file, standardizing to EPSG:4326.
        """
        print(f"Loading parcel data from {filepath}...")
        gdf = gpd.read_file(filepath)

        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")

        print(f"Loaded {len(gdf)} parcels.")
        return gdf

    # In a full implementation, this would have a method to push to PostGIS
    # e.g., using `gdf.to_postgis('parcels', engine, if_exists='append')`

if __name__ == "__main__":
    pass
