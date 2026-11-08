import logging
from pathlib import Path


def setup_logging() -> None:
    """Configure le système de logging de MediQuery V2."""

    # Racine du projet
    project_root = Path(__file__).resolve().parents[2]

    # Dossier des logs
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "mediquery.log"

    # Format des logs
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Handler fichier
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Configuration générale
    logging.basicConfig(
        level=logging.INFO, handlers=[file_handler, console_handler], force=True
    )
