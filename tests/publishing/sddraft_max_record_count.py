from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round,
                      super, filter, map, zip)

import pytest

@pytest.mark.parametrize(("number", "ex"), [
    (-1, ValueError),
    (0, None),
    (200, None),
    (8000, None)
])
def test_max_record_count(sddraft, number, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_record_count = number
    else:
        sddraft.max_record_count = number
        assert sddraft.max_record_count == number