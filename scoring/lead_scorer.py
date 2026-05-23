from typing import Dict, Any

class LeadScorer:
    """
    Algorithmic scoring system that ranks opportunities based on distance to infrastructure,
    fractionalization risk, and competitive density.
    """

    def __init__(self, target_state: str = "TX"):
        # Weights for the scoring algorithm
        self.weights = {
            "geology_confidence": 0.3,
            "parcel_overlap": 0.2,
            "severance_bonus": 0.2,
            "unleased_bonus": 0.2,
            "out_of_state_bonus": 0.1
        }
        self.target_state = target_state

    def generate_lead_score(self,
                            geology_confidence: float,
                            parcel_overlap_ratio: float,
                            is_severed: bool,
                            is_unleased: bool,
                            owner_state: str) -> Dict[str, Any]:
        """
        Generates the total algorithmic score for a lead based on:
        - geology confidence
        - parcel overlap
        - likely severance
        - likely unleased status
        - ownership signals such as out-of-state owner
        """

        # Base scores
        geo_score = min(max(geology_confidence, 0.0), 1.0)
        overlap_score = min(max(parcel_overlap_ratio, 0.0), 1.0)

        # Bonuses
        sev_score = 1.0 if is_severed else 0.0
        unleased_score = 1.0 if is_unleased else 0.0

        # Out of state bonus
        out_of_state_score = 1.0 if (owner_state and owner_state.upper() != self.target_state.upper()) else 0.0

        total_score = (
            (geo_score * self.weights["geology_confidence"]) +
            (overlap_score * self.weights["parcel_overlap"]) +
            (sev_score * self.weights["severance_bonus"]) +
            (unleased_score * self.weights["unleased_bonus"]) +
            (out_of_state_score * self.weights["out_of_state_bonus"])
        )

        return {
            "total_score": round(total_score, 3),
            "geology_confidence": geo_score,
            "parcel_overlap_ratio": overlap_score,
            "likely_severed": is_severed,
            "likely_unleased": is_unleased,
            "out_of_state_owner": out_of_state_score > 0
        }

if __name__ == "__main__":
    # Example usage:
    # scorer = LeadScorer()
    # result = scorer.generate_lead_score(distance_meters=1500, num_heirs=2, recent_mailers_count=0)
    # print(result)
    pass
