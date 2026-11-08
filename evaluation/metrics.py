def recall_at_k(ranked_ids: list[int], relevant_ids: list[int], k: int = 5) -> float:
    """Proportion des chunks pertinents retrouvés dans les K premiers résultats."""
    if not relevant_ids:
        return 0.0

    retrieved = set(ranked_ids[:k])
    relevant = set(relevant_ids)

    return len(retrieved & relevant) / len(relevant)


def mrr_at_k(ranked_ids: list[int], relevant_ids: list[int], k: int = 5) -> float:
    """Inverse du rang du premier chunk pertinent."""
    relevant = set(relevant_ids)

    for rank, chunk_id in enumerate(ranked_ids[:k], start=1):
        if chunk_id in relevant:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(ranked_ids: list[int], relevant_ids: list[int], k: int = 5) -> float:
    """NDCG avec pertinence binaire : pertinent = 1, non pertinent = 0."""
    import math

    relevant = set(relevant_ids)

    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, chunk_id in enumerate(ranked_ids[:k], start=1)
        if chunk_id in relevant
    )

    ideal_relevant_count = min(len(relevant), k)

    if ideal_relevant_count == 0:
        return 0.0

    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_relevant_count + 1))

    return dcg / idcg


def evaluate_retrieval(
    ranked_ids: list[int], relevant_ids: list[int], k: int = 5
) -> dict:
    """Calcule les trois métriques pour une question."""

    return {
        f"Recall@{k}": recall_at_k(ranked_ids, relevant_ids, k),
        f"MRR@{k}": mrr_at_k(ranked_ids, relevant_ids, k),
        f"nDCG@{k}": ndcg_at_k(ranked_ids, relevant_ids, k),
    }
