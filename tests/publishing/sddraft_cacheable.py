import pytest

from .. helpers import *

@pytest.mark.parametrize(("keep_cache", "expected"), TRUEISH_TEST_PARAMS)
def test_keep_cache(sddraft, keep_cache, expected):
    sddraft.keep_cache = keep_cache
    assert sddraft.keep_cache == expected
    
@pytest.mark.parametrize(("export_tiles_allowed", "expected"), TRUEISH_TEST_PARAMS)
def test_export_tiles_allowed(sddraft, export_tiles_allowed, expected):
    sddraft.export_tiles_allowed = export_tiles_allowed
    assert sddraft.export_tiles_allowed == expected

@pytest.mark.parametrize(("max_export_tiles_count", "ex"), [
    (0, None),
    (100, None),
    (99999, None),
    (-10, ValueError)
])
def test_max_export_tiles_count(sddraft, max_export_tiles_count, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.max_export_tiles_count = max_export_tiles_count
    else:
        sddraft.max_export_tiles_count = max_export_tiles_count
        assert sddraft.max_export_tiles_count == max_export_tiles_count