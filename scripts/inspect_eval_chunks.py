import json
from pathlib import Path

from app.services.fusion import reciprocal_rank_fusion
from app.services.retrieval import dense_search
from app.services.sparse_retrieval import SparseRetriever

# Chemin du dataset
DATASET_PATH = Path("evaluation/datasets/mediquery_eval.json")


def load_questions():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def inspect_question(question, sparse_retriever, top_k=10):

    print("\n" + "=" * 80)
    print(f"{question['id']} : {question['question']}")
    print("=" * 80)

    # Dense retrieval
    dense_results = dense_search(question["question"], top_k=10)

    # Sparse retrieval
    sparse_results = sparse_retriever.search(question["question"], top_k=10)

    # Fusion RRF
    fused_results = reciprocal_rank_fusion(
        dense_results=dense_results, sparse_results=sparse_results, k=60, top_k=top_k
    )

    # Affichage des candidats
    for rank, result in enumerate(fused_results, start=1):
        print(f"\nCandidat {rank}")
        print(f"ID : {result['id']}")
        print(f"Page : {result['metadata']['page']}")
        print(f"Score RRF : {result['rrf_score']:.6f}")
        print(f"Classement : {result['ranks']}")
        print(f"Texte :\n{result['text']}")
        print("-" * 80)


def main():

    questions = load_questions()

    question_id = (
        input("Identifiant de la question à examiner (ex: Q02) : ").strip().upper()
    )

    selected = [question for question in questions if question["id"] == question_id]

    if not selected:
        print("Question introuvable.")
        return

    sparse_retriever = SparseRetriever()

    try:
        print("Construction de l'index BM25...")
        sparse_retriever.build_index()

        inspect_question(selected[0], sparse_retriever, top_k=10)

    finally:
        sparse_retriever.close()


if __name__ == "__main__":
    main()
