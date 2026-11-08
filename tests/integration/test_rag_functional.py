import os

import pytest

from app.pipelines.rag_pipeline import rag_query

# ============================================================
# Configuration
# ============================================================

# Les tests réels sont exécutés uniquement si cette variable vaut 1.
RUN_LIVE_TESTS = os.getenv("RUN_LIVE_RAG_TESTS", "0") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_LIVE_TESTS,
    reason=(
        "Définir RUN_LIVE_RAG_TESTS=1 pour exécuter les tests avec les API réelles."
    ),
)


# ============================================================
# Fonctions utilitaires
# ============================================================


def check_result(result: dict):
    """Vérifie la structure minimale du résultat RAG."""

    assert isinstance(result, dict)
    assert result["question"]

    assert isinstance(result["answer"], str)
    assert result["answer"].strip()

    assert isinstance(result["sources"], list)
    assert len(result["sources"]) > 0

    assert result["chunks_used"] > 0
    assert result["model"]

    for source in result["sources"]:
        assert source["filename"]
        assert source["page"] is not None


def check_refusal(answer: str, refusal_terms: list[str]):
    """
    Vérifie que MediQuery reconnaît une question
    à laquelle le contexte documentaire ne permet pas de répondre.
    """

    answer = answer.lower()

    assert any(term in answer for term in refusal_terms), (
        f"MediQuery aurait dû refuser de répondre.\n\nRéponse générée :\n{answer}"
    )


# ============================================================
# Tests fonctionnels
# ============================================================


def test_question_simple():
    """Une question dont la réponse est clairement présente dans le guide."""

    question = (
        "Quelles sont les principales étapes du parcours de soins "
        "du patient adulte vivant avec un diabète de type 2 ?"
    )

    result = rag_query(question)

    check_result(result)

    answer = result["answer"].lower()

    expected_terms = ["dépistage", "diagnostic", "suivi", "complications"]

    for term in expected_terms:
        assert term in answer, f"Terme attendu absent : {term}"


def test_question_multi_informations():
    """Une question qui nécessite plusieurs informations du guide."""

    question = (
        "Quelles mesures non médicamenteuses sont recommandées "
        "dans la prise en charge du diabète de type 2 ?"
    )

    result = rag_query(question)

    check_result(result)

    answer = result["answer"].lower()

    expected_terms = ["activité physique", "équilibre alimentaire"]

    for term in expected_terms:
        assert term in answer, f"Information attendue absente : {term}"


def test_question_precise():
    """Une question précise sur le dépistage."""

    question = (
        "Quels tests sont utilisés pour dépister le diabète de type 2 "
        "et à quelle fréquence ?"
    )

    result = rag_query(question)

    check_result(result)

    answer = result["answer"].lower()

    assert any(term in answer for term in ["glycémie", "glycémie veineuse", "test"]), (
        "La réponse ne mentionne pas les tests de dépistage."
    )


def test_question_hors_perimetre_document():
    """Une question médicale sur une pathologie différente."""

    question = (
        "Quelles sont les recommandations de prise en charge "
        "du diabète de type 1 chez l'enfant ?"
    )

    result = rag_query(question)

    check_result(result)

    check_refusal(
        result["answer"],
        [
            "ne permettent pas de répondre",
            "ne permet pas de répondre",
            "n'est pas abordée",
            "n'est pas abordé",
            "informations insuffisantes",
        ],
    )


def test_question_sans_rapport():
    """Une question sans rapport avec le contenu du guide."""

    question = "Quelle est la capitale du Japon ?"

    result = rag_query(question)

    check_result(result)

    check_refusal(
        result["answer"],
        [
            "je ne peux pas répondre",
            "ne contient aucune information",
            "ne contiennent aucune information",
            "hors du périmètre",
            "ne permettent pas de répondre",
        ],
    )
