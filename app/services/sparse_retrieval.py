import logging
import re
import unicodedata
from threading import RLock

from rank_bm25 import BM25Okapi

from app.repositories.qdrant_repository import QdrantRepository

logger = logging.getLogger(__name__)


def tokenize(text: str) -> list[str]:
    """Normalise et découpe un texte en tokens."""

    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))

    return re.findall(r"\b\w+\b", text)


class SparseRetriever:
    # Cache partagé entre toutes les instances de SparseRetriever
    _cached_documents = None
    _cached_bm25 = None

    # Évite que plusieurs requêtes construisent simultanément le même index
    _cache_lock = RLock()

    def __init__(self):
        self.documents = []
        self.bm25 = None
        self.repository = None

    def build_index(self):
        """
        Construit l'index BM25 une seule fois par processus.

        Si l'index existe déjà, il est directement réutilisé.
        """

        # Vérification rapide du cache
        if (
            SparseRetriever._cached_bm25 is not None
            and SparseRetriever._cached_documents is not None
        ):
            self.documents = SparseRetriever._cached_documents
            self.bm25 = SparseRetriever._cached_bm25

            logger.info("Index BM25 récupéré depuis le cache.")
            return

        # Protection contre les constructions simultanées
        with SparseRetriever._cache_lock:
            # Une autre requête a peut-être construit l'index
            # pendant que cette requête attendait le verrou.
            if (
                SparseRetriever._cached_bm25 is not None
                and SparseRetriever._cached_documents is not None
            ):
                self.documents = SparseRetriever._cached_documents
                self.bm25 = SparseRetriever._cached_bm25

                logger.info("Index BM25 récupéré depuis le cache.")
                return

            logger.info("Construction initiale de l'index BM25.")

            self.repository = QdrantRepository()

            try:
                documents = []
                offset = None

                # Récupération de tous les passages depuis Qdrant
                while True:
                    points, next_offset = self.repository.client.scroll(
                        collection_name=self.repository.collection_name,
                        limit=100,
                        offset=offset,
                        with_payload=True,
                        with_vectors=False,
                    )

                    for point in points:
                        payload = point.payload or {}

                        documents.append(
                            {
                                "id": point.id,
                                "text": payload.get("text", ""),
                                "metadata": {
                                    "filename": payload.get("filename"),
                                    "page": payload.get("page"),
                                    "chunk_id": payload.get("chunk_id"),
                                },
                            }
                        )

                    if next_offset is None:
                        break

                    offset = next_offset

                if not documents:
                    raise ValueError("Aucun document trouvé dans Qdrant.")

                # Tokenisation du corpus
                tokenized_corpus = [
                    tokenize(document["text"]) for document in documents
                ]

                # Construction de l'index BM25
                bm25_index = BM25Okapi(tokenized_corpus)

                # Mise en cache
                SparseRetriever._cached_documents = documents
                SparseRetriever._cached_bm25 = bm25_index

                # Affectation à l'instance courante
                self.documents = documents
                self.bm25 = bm25_index

                logger.info(
                    "Index BM25 construit et mis en cache : %s documents.",
                    len(documents),
                )

            finally:
                self.repository.close()
                self.repository = None

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        """Recherche les passages les plus pertinents avec BM25."""

        if not question or not question.strip():
            raise ValueError("La question ne peut pas être vide.")

        if top_k <= 0:
            raise ValueError("top_k doit être positif.")

        if self.bm25 is None:
            raise RuntimeError(
                "L'index BM25 n'est pas initialisé. "
                "Appeler build_index() avant search()."
            )

        query_tokens = tokenize(question)

        scores = self.bm25.get_scores(query_tokens)

        ranked_indices = scores.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            document = self.documents[index]

            results.append(
                {
                    "id": document["id"],
                    "score": float(scores[index]),
                    "text": document["text"],
                    "metadata": document["metadata"],
                }
            )

        logger.info("Recherche BM25 terminée : %s résultats.", len(results))

        return results

    def refresh_index(self):
        """
        Invalide le cache partagé et reconstruit l'index BM25.

        À utiliser après une mise à jour des documents dans Qdrant.
        """

        with SparseRetriever._cache_lock:
            SparseRetriever._cached_documents = None
            SparseRetriever._cached_bm25 = None

            logger.info("Cache BM25 invalidé.")

            self.documents = []
            self.bm25 = None

            self.build_index()

    def close(self):
        """Ferme le repository s'il est encore ouvert."""

        if self.repository is not None:
            self.repository.close()
            self.repository = None
