import pytest
from scoring.lead_scorer import LeadScorer

def test_scorer_init():
    scorer = LeadScorer()
    assert scorer.weights["distance"] == 0.4

def test_distance_score():
    scorer = LeadScorer()
    assert scorer.calculate_distance_score(0) == 1.0
    assert scorer.calculate_distance_score(10000) == 0.0
    assert scorer.calculate_distance_score(5000) == 0.5

def test_fractionalization_score():
    scorer = LeadScorer()
    assert scorer.calculate_fractionalization_score(1) == 1.0
    assert scorer.calculate_fractionalization_score(4) == 0.5

def test_competition_score():
    scorer = LeadScorer()
    assert scorer.calculate_competition_score(0) == 1.0
    assert scorer.calculate_competition_score(2) == 0.3

def test_generate_lead_score():
    scorer = LeadScorer()
    # Distance = 5000 -> 0.5 * 0.4 = 0.2
    # Heirs = 2 -> 0.8 * 0.4 = 0.32
    # Comp = 0 -> 1.0 * 0.2 = 0.2
    # Total = 0.72
    result = scorer.generate_lead_score(5000, 2, 0)
    assert result["total_score"] == 0.72
