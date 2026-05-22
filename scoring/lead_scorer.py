from typing import Dict, Any

class LeadScorer:
    """
    Algorithmic scoring system that ranks opportunities based on distance to infrastructure,
    fractionalization risk, and competitive density.
    """

    def __init__(self):
        # Weights for the scoring algorithm
        self.weights = {
            "distance": 0.4,
            "fractionalization": 0.4,
            "competition": 0.2
        }

    def calculate_distance_score(self, distance_meters: float) -> float:
        """
        Calculates score based on proximity to active drilling/mining.
        Closer = Higher Score.
        Returns a score between 0.0 and 1.0.
        """
        # Assume max relevant distance is 10,000 meters (10km)
        max_dist = 10000.0
        if distance_meters <= 0:
            return 1.0
        elif distance_meters >= max_dist:
            return 0.0

        return 1.0 - (distance_meters / max_dist)

    def calculate_fractionalization_score(self, num_heirs: int) -> float:
        """
        Calculates score based on the number of living heirs.
        Fewer heirs = Higher Score (easier to negotiate/purchase).
        Returns a score between 0.0 and 1.0.
        """
        if num_heirs <= 1:
            return 1.0
        elif num_heirs <= 3:
            return 0.8
        elif num_heirs <= 5:
            return 0.5
        elif num_heirs <= 10:
            return 0.2
        else:
            return 0.0

    def calculate_competition_score(self, recent_mailers_count: int) -> float:
        """
        Calculates score based on competitive density.
        Fewer recent corporate mailers/leases = Higher Score (less competition).
        Returns a score between 0.0 and 1.0.
        """
        if recent_mailers_count == 0:
            return 1.0
        elif recent_mailers_count == 1:
            return 0.7
        elif recent_mailers_count <= 3:
            return 0.3
        else:
            return 0.0

    def generate_lead_score(self, distance_meters: float, num_heirs: int, recent_mailers_count: int) -> Dict[str, float]:
        """
        Generates the total algorithmic score for a lead.
        """
        dist_score = self.calculate_distance_score(distance_meters)
        frac_score = self.calculate_fractionalization_score(num_heirs)
        comp_score = self.calculate_competition_score(recent_mailers_count)

        total_score = (
            (dist_score * self.weights["distance"]) +
            (frac_score * self.weights["fractionalization"]) +
            (comp_score * self.weights["competition"])
        )

        return {
            "total_score": round(total_score, 3),
            "distance_score": round(dist_score, 3),
            "fractionalization_score": round(frac_score, 3),
            "competition_score": round(comp_score, 3)
        }

if __name__ == "__main__":
    # Example usage:
    # scorer = LeadScorer()
    # result = scorer.generate_lead_score(distance_meters=1500, num_heirs=2, recent_mailers_count=0)
    # print(result)
    pass
