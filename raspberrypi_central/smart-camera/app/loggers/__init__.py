import logging
import sys

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)

LOGGER = logging.getLogger('mx')
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.DEBUG)
