import pytest

from .. helpers import *

@pytest.mark.parametrize(("cache_dir", "expected"), [
    (r"D:\Test\File\Path", r"D:\Test\File\Path"),
    (r"\\Test\Unc\Path", r"\\Test\Unc\Path"),
    (None, None)
])
def test_cache_dir(sddraft, cache_dir, expected):
    sddraft.cache_dir = cache_dir
    assert sddraft.cache_dir == expected

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

@pytest.mark.parametrize(("use_local_cache_dir", "expected"), TRUEISH_TEST_PARAMS)
def test_use_local_cache_dir(sddraft, use_local_cache_dir, expected):
    sddraft.use_local_cache_dir = use_local_cache_dir
    assert sddraft.use_local_cache_dir == expected