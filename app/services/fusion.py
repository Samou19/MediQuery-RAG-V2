import logging

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    dense_results: list[dict], sparse_results: list[dict], k: int = 60, top_k: int = 5
) -> list[dict]:
    """
    Fusionne les résultats Dense et Sparse avec Reciprocal Rank Fusion.

    Args:
        dense_results: résultats du moteur Dense.
        sparse_results: résultats du moteur Sparse (BM25).
        k: constante RRF.
        top_k: nombre de résultats finaux.

    Returns:
        Liste des documents fusionnés et classés par score RRF.
    """

    if k <= 0:
        raise ValueError("k doit être strictement positif.")

    if top_k <= 0:
        raise ValueError("top_k doit être strictement positif.")

    fused_results = {}

    retrieval_lists = {"dense": dense_results, "sparse": sparse_results}

    for source, results in retrieval_lists.items():
        for rank, result in enumerate(results, start=1):
            document_id = result["id"]

            if document_id not in fused_results:
                fused_results[document_id] = {
                    "id": document_id,
                    "text": result["text"],
                    "metadata": result["metadata"],
                    "rrf_score": 0.0,
                    "ranks": {},
                    "sources": [],
                }

            fused_results[document_id]["rrf_score"] += 1 / (k + rank)

            fused_results[document_id]["ranks"][source] = rank
            fused_results[document_id]["sources"].append(source)

    ranked_results = sorted(
        fused_results.values(), key=lambda item: item["rrf_score"], reverse=True
    )

    logger.info("Fusion RRF terminée : %s documents fusionnés.", len(ranked_results))

    return ranked_results[:top_k]
