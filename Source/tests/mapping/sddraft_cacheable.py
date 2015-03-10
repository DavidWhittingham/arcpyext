import pytest

from .. helpers import *

@pytest.mark.parametrize(("keep_cache", "expected"), TRUSISH_TEST_PARAMS)
def test_keep_cache(sddraft, keep_cache, expected):
    sddraft.keep_cache = keep_cache
    assert sddraft.keep_cache == expected