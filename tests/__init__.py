import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(fmt=logging.Formatter(fmt="%(asctime)s [%(levelname)s]: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

tests_dir_path = Path(__file__).parent
