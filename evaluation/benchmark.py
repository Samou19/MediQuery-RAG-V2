import json
import logging
from collections import defaultdict
from pathlib import Path

from app.services.fusion import reciprocal_rank_fusion
from app.services.reranking import rerank_results
from app.services.retrieval import dense_search
from app.services.sparse_retrieval import SparseRetriever
from evaluation.metrics import evaluate_retrieval

DATASET_PATH = Path("evaluation/datasets/mediquery_eval.json")

K = 5
CANDIDATE_K = 10


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def get_result_ids(results):
    return [int(result["id"]) for result in results]


def main():

    logging.basicConfig(level=logging.WARNING)

    questions = load_dataset()

    sparse_retriever = SparseRetriever()

    # Stockage des métriques par méthode
    scores = defaultdict(list)

    try:
        print("Construction de l'index BM25...")
        sparse_retriever.build_index()

        for question in questions:
            question_id = question["id"]
            query = question["question"]
            relevant_ids = question["relevant_chunk_ids"]

            if not relevant_ids:
                raise ValueError(f"Aucun chunk pertinent annoté pour {question_id}")

            print(f"\nÉvaluation de {question_id}...")

            # 1. Dense retrieval
            dense_results = dense_search(query, top_k=CANDIDATE_K)

            # 2. Sparse retrieval
            sparse_results = sparse_retriever.search(query, top_k=CANDIDATE_K)

            # 3. Fusion RRF
            fused_results = reciprocal_rank_fusion(
                dense_results=dense_results,
                sparse_results=sparse_results,
                k=60,
                top_k=CANDIDATE_K,
            )

            # 4. Reranking
            reranked_results = rerank_results(
                question=query, candidates=fused_results, top_k=K
            )

            # Résultats à comparer
            methods = {
                "Dense": dense_results[:K],
                "BM25": sparse_results[:K],
                "RRF": fused_results[:K],
                "RRF + Reranking": reranked_results,
            }

            for method_name, results in methods.items():
                ranked_ids = get_result_ids(results)

                metrics = evaluate_retrieval(
                    ranked_ids=ranked_ids, relevant_ids=relevant_ids, k=K
                )

                scores[method_name].append(metrics)

        # Résultats moyens
        print("\n" + "=" * 75)
        print(f"RÉSULTATS DU BENCHMARK — MÉTRIQUES @{K}")
        print("=" * 75)

        print(f"{'Méthode':<22}{'Recall@5':>12}{'MRR@5':>12}{'nDCG@5':>12}")

        print("-" * 75)

        for method_name, question_scores in scores.items():
            averages = {
                metric: sum(item[metric] for item in question_scores)
                / len(question_scores)
                for metric in question_scores[0]
            }

            print(
                f"{method_name:<22}"
                f"{averages['Recall@5']:>12.4f}"
                f"{averages['MRR@5']:>12.4f}"
                f"{averages['nDCG@5']:>12.4f}"
            )

        print("=" * 75)

    finally:
        sparse_retriever.close()


if __name__ == "__main__":
    main()
