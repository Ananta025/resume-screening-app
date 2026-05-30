from collections.abc import Iterable

from app.services.scoring_service import CandidateScore



class RankingService:
    def rank(self, results: Iterable[CandidateScore]) -> list[CandidateScore]:
        ranked_results = sorted(results, key=lambda result: result.final_score, reverse=True)

        for rank, result in enumerate(ranked_results, start=1):
            result.rank = rank

        return ranked_results


ranking_service = RankingService()