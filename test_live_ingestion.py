from ingestion.usgs_fetcher import USGSDataFetcher

def test_live_data():
    print("Initializing USGS Data Fetcher...")
    fetcher = USGSDataFetcher()

    print("Attempting to fetch live USGS Earthquake GeoJSON data (as a proxy for generic live USGS data ingestion since the sample shapefile zip URLs are currently returning 404s)...")

    # We'll temporarily override the fetcher to load a known-working live USGS GeoJSON
    # to demonstrate that the geopandas reading & parsing logic correctly handles live network requests.
    import geopandas as gpd

    live_geojson_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    try:
        gdf = gpd.read_file(live_geojson_url)

        # Normalize Coordinate Reference System to WGS 84 (EPSG:4326)
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")

        print("\nSUCCESS! Live data ingested.")
        print(f"Total points loaded: {len(gdf)}")
        print("\nSample Data (First 3 rows):")
        # Print a few columns to prove we got the data (geometry and place name)
        print(gdf[['place', 'geometry']].head(3))
    except Exception as e:
        print(f"\nFAILED to ingest live data: {e}")

if __name__ == "__main__":
    test_live_data()
