from app.core.config import get_settings

settings = get_settings()

print("Application :", settings.APP_NAME)
print("Version :", settings.APP_VERSION)
print("Qdrant :", settings.QDRANT_URL)
print("Collection :", settings.QDRANT_COLLECTION)
print("Modèle embeddings :", settings.VOYAGE_EMBEDDING_MODEL)
print("Dimension :", settings.EMBEDDING_DIMENSION)
print("Modèle Claude :", settings.CLAUDE_MODEL)
