import logging, os

def get_logger(name: str) -> logging.Logger:
    level = os.getenv("LOGLEVEL", "INFO").upper()
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        level=getattr(logging, level, logging.INFO),
    )
    return logging.getLogger(name)
