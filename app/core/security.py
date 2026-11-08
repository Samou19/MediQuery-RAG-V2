from app.core.config import get_settings


def validate_api_keys() -> None:
    """Vérifie la présence des clés API nécessaires."""

    settings = get_settings()

    required_keys = {
        "VOYAGE_API_KEY": settings.VOYAGE_API_KEY,
        "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY,
    }

    missing_keys = [
        name for name, value in required_keys.items() if not value or not value.strip()
    ]

    if missing_keys:
        raise ValueError(f"Clés API manquantes : {', '.join(missing_keys)}")
