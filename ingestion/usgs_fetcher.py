import os
import requests
import tempfile
import zipfile
import geopandas as gpd
from typing import Optional, Dict, Any

class USGSDataFetcher:
    """
    Interfaces with USGS and state geological APIs to fetch Shapefiles/GeoJSON
    for known mineral deposits, shale plays, and oil fields.
    """

    def __init__(self, db_connection_string: Optional[str] = None):
        """
        Initialize the fetcher.
        :param db_connection_string: PostGIS connection string to save data to the DB.
        """
        self.db_connection_string = db_connection_string or os.environ.get("DATABASE_URL")

    def download_shapefile_zip(self, url: str, extract_dir: str) -> str:
        """
        Downloads a zipped shapefile from a URL and extracts it.
        :param url: URL to the zip file.
        :param extract_dir: Directory to extract contents.
        :return: Path to the main .shp file.
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()

        zip_path = os.path.join(extract_dir, "temp_shapefile.zip")
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Find the .shp file
        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(".shp"):
                    return os.path.join(root, file)

        raise FileNotFoundError("No .shp file found in the downloaded zip archive.")

    def process_and_save_geodata(self, filepath: str, formation_type: str = "Unknown", zone_name_col: str = None) -> gpd.GeoDataFrame:
        """
        Reads spatial data using GeoPandas, normalizes coordinates to EPSG:4326,
        and (optionally) saves it to the database.
        """
        print(f"Reading spatial data from {filepath}...")
        gdf = gpd.read_file(filepath)

        # Normalize Coordinate Reference System to WGS 84 (EPSG:4326)
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")

        print(f"Loaded {len(gdf)} geological zones.")

        # Ensure MultiPolygons for database compatibility
        # In a full implementation, we'd map fields and push to the PostGIS 'geological_zones' table using SQLAlchemy/GeoAlchemy2.
        # e.g. gdf.to_postgis('geological_zones', engine, if_exists='append', ...)

        return gdf

    def load_local_geology(self, filepath: str) -> gpd.GeoDataFrame:
        """
        Loads geology data from a local file. Used for MVP/offline mode.
        """
        return self.process_and_save_geodata(filepath)

    def fetch_shale_plays(self):
        """
        Example method to fetch EIA/USGS US Shale Plays.
        """
        shale_url = "https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_lower48_TXLA_update.zip"

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                shp_path = self.download_shapefile_zip(shale_url, tmpdir)
                gdf = self.process_and_save_geodata(shp_path, formation_type="Shale Play", zone_name_col="Play_Name")
                return gdf
            except Exception as e:
                print(f"Failed to fetch shale plays: {e}")
                return None

    def fetch_usgs_mineral_resources_program_data(self):
        """
        Fetches datasets from the USGS Mineral Resources Program Data Portal.
        This represents the primary data repository containing geospatial downloads,
        maps, and geochemical/geophysical datasets necessary to establish resource baseline shapes.
        """
        # Note: In a production environment, this would target specific dataset URLs
        # within the MRP Data Portal depending on the targeted mineral.
        mrp_sample_url = "https://mrdata.usgs.gov/services/ds-1130?request=GetCapabilities&service=WFS&version=1.0.0" # Example WFS endpoint
        print(f"Targeting USGS MRP portal: {mrp_sample_url}")

        # Implementation would parse WFS or download shapefiles similar to fetch_shale_plays
        return None

    def fetch_usgs_usmin_spatial_catalog(self):
        """
        Fetches spatial data boundaries for known mineral districts and deposits
        from the USGS Mineral Resources Online Spatial Data Catalog (including USMIN).
        """
        # Note: Targets the USMIN mine feature tracking and interactive maps.
        usmin_shapefile_url = "https://mrdata.usgs.gov/usmin/data/usmin-shape.zip" # Example shapefile URL

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                shp_path = self.download_shapefile_zip(usmin_shapefile_url, tmpdir)
                gdf = self.process_and_save_geodata(shp_path, formation_type="Mineral Deposit", zone_name_col="site_name")
                return gdf
            except Exception as e:
                print(f"Failed to fetch USMIN spatial catalog data: {e}")
                return None

if __name__ == "__main__":
    fetcher = USGSDataFetcher()
    # fetcher.fetch_shale_plays()
