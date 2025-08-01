import logging
import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
level = getattr(logging, LOG_LEVEL, logging.INFO)

logging.basicConfig(
    level=level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('echoed')

