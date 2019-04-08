# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

TRUEISH_TEST_PARAMS = [
    (True, True),
    ("TRUE", True),
    ("T", True),
    ("tRUe", True),
    ("t", True),
    (False, False),
    ("FALSE", False),
    ("F", False),
    ("faLSe", False),
    ("f", False),
    (1, True),
    (0, False),
    (2, False),
    (-1, False)
]