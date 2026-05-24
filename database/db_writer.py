import os
import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
from typing import List, Dict, Any

class DatabaseWriter:
    """
    Persists pipeline output (leads, intersected parcels) into PostgreSQL/PostGIS.
    """
    def __init__(self, db_url: str = None):
        # Default to environment variable if not provided
        self.db_url = db_url or os.environ.get("DATABASE_URL")
        self.engine = None
        if self.db_url:
            try:
                self.engine = create_engine(self.db_url)
            except Exception as e:
                print(f"Warning: Failed to initialize DB engine: {e}")

    def persist_leads(self, leads: List[Dict[str, Any]]):
        """
        Writes the final ranked leads to the 'leads' table.
        For the MVP, we assume the table matches the schema in schema.sql.
        """
        if not self.engine:
            print("Skipping DB write for leads: No DATABASE_URL configured.")
            return

        if not leads:
            print("No leads to persist.")
            return

        print(f"Persisting {len(leads)} leads to the database...")
        df = pd.DataFrame(leads)

        # Map our pipeline dictionary keys to the actual DB schema column names
        # e.g., 'APN' -> 'parcel_id'
        df_db = pd.DataFrame({
            'parcel_id': df['APN'],
            'total_score': df['Score'],
            'likely_severed': df['Is_Severed'],
            'likely_unleased': df['Is_Unleased'],
            'out_of_state_owner': df['Owner_State'] != 'TX', # Basic approximation
            'is_high_value_anomaly': (df['Is_Severed'] & df['Is_Unleased'])
        })

        try:
            # We use if_exists='append' for cumulative running
            df_db.to_sql('leads', self.engine, if_exists='append', index=False)
            print("Successfully written leads to DB.")
        except Exception as e:
            print(f"Failed to persist leads to DB: {e}")

    def persist_intersected_parcels(self, parcels_gdf: gpd.GeoDataFrame):
        """
        Writes the geometry and metadata of the target parcels into the 'parcels' PostGIS table.
        """
        if not self.engine:
            print("Skipping DB write for parcels: No DATABASE_URL configured.")
            return

        if parcels_gdf is None or parcels_gdf.empty:
            return

        print(f"Persisting {len(parcels_gdf)} parcels to the database with PostGIS geometries...")

        # Keep only required columns
        cols_to_keep = ['APN', 'OWNER_NAME', 'OWNER_STATE', 'geometry']
        available_cols = [c for c in cols_to_keep if c in parcels_gdf.columns]
        gdf_db = parcels_gdf[available_cols].copy()

        # Map to schema
        gdf_db = gdf_db.rename(columns={'APN': 'parcel_id', 'OWNER_NAME': 'owner_name', 'OWNER_STATE': 'owner_address_state'})
        gdf_db['county_fips'] = '00000' # Placeholder MVP

        try:
            # Requires geoalchemy2
            gdf_db.to_postgis('parcels', self.engine, if_exists='append', index=False)
            print("Successfully written parcels to PostGIS.")
        except Exception as e:
            print(f"Failed to persist parcels to PostGIS: {e}")

if __name__ == "__main__":
    pass
