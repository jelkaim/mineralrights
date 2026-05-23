import pytest
from spatial.intersection_engine import SpatialIntersectionEngine

def test_spatial_engine_init():
    engine = SpatialIntersectionEngine()
    assert engine.target_crs == "EPSG:4326"

def test_severance_check_positive():
    engine = SpatialIntersectionEngine()
    deed_history = [
        {"is_mineral_severed": True, "has_active_lease": False}
    ]
    # Check returns True for high value anomaly
    assert engine.evaluate_severance_check(None, deed_history) == True

def test_severance_check_negative():
    engine = SpatialIntersectionEngine()
    deed_history = [
        {"is_mineral_severed": True, "is_lease": True}
    ]
    # Check returns False due to active lease
    assert engine.evaluate_severance_check(None, deed_history) == False
