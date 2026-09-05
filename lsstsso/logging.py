import logging

logger = logging.getLogger("lsstsso")
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
