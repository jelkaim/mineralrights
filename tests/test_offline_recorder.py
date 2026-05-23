import pytest
from ingestion.offline_recorder import OfflineRecorderImporter

def test_load_csv_export():
    importer = OfflineRecorderImporter()
    records = importer.load_csv_export("data/sample_deeds.csv")
    assert len(records) == 2
    assert records[0]["APN"] == "123-45-678"
    assert records[1]["DocumentType"] == "OIL AND GAS LEASE"
