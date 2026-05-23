import pytest
from pipeline import ArbitragePipeline

def test_mvp_pipeline():
    pipeline = ArbitragePipeline()
    leads = pipeline.run_mvp_pipeline(
        "data/sample_geology.geojson",
        "data/sample_parcels.geojson",
        "data/sample_deeds.csv"
    )

    # We expect 1 lead (123-45-678) because the other parcel does not intersect
    assert len(leads) == 1

    lead = leads[0]
    assert lead["APN"] == "123-45-678"
    assert lead["Is_Severed"] == True
    assert lead["Is_Unleased"] == True
    assert lead["Owner_State"] == "CA"
    assert lead["Score"] > 0.0 # Should have geology, overlap, severance, unleased, and out-of-state bonuses
