import logging
import sys


def init_logging(level=logging.INFO, file=None):
    handlers = [logging.StreamHandler(sys.stdout)]
    if file:
        handlers.append(logging.FileHandler(file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
        force=True,
    )
