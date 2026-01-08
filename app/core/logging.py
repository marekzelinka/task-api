import sys

from loguru import logger

from .config import config

logger.remove(0)
logger.add(sys.stderr, level=config.log_level)
