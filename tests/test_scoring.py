import pytest
from scoring.lead_scorer import LeadScorer

def test_scorer_init():
    scorer = LeadScorer()
    assert scorer.weights["geology_confidence"] == 0.3

def test_generate_lead_score():
    scorer = LeadScorer(target_state="TX")
    # Geology: 0.9 * 0.3 = 0.27
    # Overlap: 1.0 * 0.2 = 0.20
    # Severed: 1.0 * 0.2 = 0.20
    # Unleased: 1.0 * 0.2 = 0.20
    # Out of state (CA vs TX): 1.0 * 0.1 = 0.10
    # Total = 0.97
    result = scorer.generate_lead_score(
        geology_confidence=0.9,
        parcel_overlap_ratio=1.0,
        is_severed=True,
        is_unleased=True,
        owner_state="CA"
    )
    assert result["total_score"] == 0.97
    assert result["out_of_state_owner"] == True

    # Same test but in state
    result_in_state = scorer.generate_lead_score(
        geology_confidence=0.9,
        parcel_overlap_ratio=1.0,
        is_severed=True,
        is_unleased=True,
        owner_state="TX"
    )
    assert result_in_state["total_score"] == 0.87
    assert result_in_state["out_of_state_owner"] == False
