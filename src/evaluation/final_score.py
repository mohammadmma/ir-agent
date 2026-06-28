class FinalMeanScorer:
    def score(self, wikirank_score: float, diversity_score: float) -> float:
        return (wikirank_score + 100 * diversity_score) / 2