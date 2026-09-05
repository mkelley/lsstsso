import logging

logger = logging.getLogger("lsstsso")
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)
