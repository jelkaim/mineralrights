import pytest
from ingestion.parcel_loader import ParcelLoader

def test_parcel_loader_init():
    loader = ParcelLoader(db_connection_string="test_db")
    assert loader.db_connection_string == "test_db"

def test_load_local_parcels():
    loader = ParcelLoader()
    gdf = loader.load_parcels("data/sample_parcels.geojson")
    assert len(gdf) == 2
    assert "APN" in gdf.columns
