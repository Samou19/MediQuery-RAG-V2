import logging

from langchain_anthropic import ChatAnthropic

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def generate_answer(messages: list[dict]) -> dict:
    """
    Génère une réponse avec Claude API à partir
    des messages construits par le Prompt Builder.

    Args:
        messages: Liste des messages system et human.

    Returns:
        Dictionnaire contenant la réponse et les
        informations d'utilisation du modèle.
    """

    if not messages:
        raise ValueError("La liste des messages ne peut pas être vide.")

    settings = get_settings()

    # 1. Initialisation du modèle Claude
    llm = ChatAnthropic(
        model=settings.CLAUDE_MODEL,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=settings.CLAUDE_MAX_TOKENS,
    )

    try:
        # 2. Appel à Claude API
        response = llm.invoke(messages)

        # 3. Extraction du contenu textuel
        if isinstance(response.content, str):
            answer = response.content
        else:
            answer = "\n".join(
                block["text"]
                for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )

        # 4. Récupération des métadonnées d'utilisation
        usage = response.usage_metadata or {}

        logger.info(
            "Réponse générée avec Claude : %s tokens en entrée, %s tokens en sortie.",
            usage.get("input_tokens", 0),
            usage.get("output_tokens", 0),
        )

        return {"answer": answer, "model": settings.CLAUDE_MODEL, "usage": usage}

    except Exception:
        logger.exception("Erreur pendant la génération avec Claude API.")
        raise
