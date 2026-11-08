import logging

from app.core.logging import setup_logging

setup_logging()

logger = logging.getLogger("mediquery.test")

logger.debug("Message de debug")
logger.info("MediQuery V2 démarré")
logger.warning("Exemple de warning")
logger.error("Exemple d'erreur")
