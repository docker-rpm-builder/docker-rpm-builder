# I don't really like this but I don't seem to have a good option to setup testing log
# otherwise. We rely on the "singleton import" feature.

import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format="%(asctime)s %(level)s [%(name)s] %(message)s")
