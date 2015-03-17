import datetime
import os.path
import shutil

import arcpyext
import pytest

from arcpyext.publishing import ImageSDDraft
from .. helpers import *

SDDRAFT_FILE_PATH = os.path.abspath("{0}/../samples/imageservice.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_FILE_PATH_COPY = os.path.abspath("{0}/../samples/imageservice.copy.sddraft".format(os.path.dirname(__file__)))
SDDRAFT_SAVE_TEST_FILE_PATH = os.path.abspath("{0}/../samples/imageservice.savetest.sddraft".format(os.path.dirname(__file__)))

@pytest.fixture
def sddraft():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return ImageSDDraft(SDDRAFT_FILE_PATH_COPY)

from sddraftbase import *
from sddraft_cacheable import *

@pytest.mark.parametrize(("methods", "expected", "ex"), [
    ([ImageSDDraft.CompressionMethod.none], [ImageSDDraft.CompressionMethod.none], None),
    (
        [ImageSDDraft.CompressionMethod.jpeg, ImageSDDraft.CompressionMethod.lz77],
        [ImageSDDraft.CompressionMethod.jpeg, ImageSDDraft.CompressionMethod.lz77],
        None
    ),
    (["LERC"], [ImageSDDraft.CompressionMethod.lerc], None),
    (["Fail"], None, ValueError),
    ([123], None, TypeError)
])
def test_allowed_compressions(sddraft, methods, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.allowed_compressions = methods
    else:
        sddraft.allowed_compressions = methods
        assert set(sddraft.allowed_compressions) == set(expected)

@pytest.mark.parametrize(("methods", "expected", "ex"), [
    ([ImageSDDraft.MosaicMethod.north_west], [ImageSDDraft.MosaicMethod.north_west], None),
    (
        [ImageSDDraft.MosaicMethod.lock_raster, ImageSDDraft.MosaicMethod.center],
        [ImageSDDraft.MosaicMethod.lock_raster, ImageSDDraft.MosaicMethod.center],
        None
    ),
    (["Nadir", "Viewpoint"], [ImageSDDraft.MosaicMethod.nadir, ImageSDDraft.MosaicMethod.viewpoint], None),
    (["Blah"], None, ValueError)
])
def test_allowed_mosaic_methods(sddraft, methods, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.allowed_mosaic_methods = methods
    else:
        sddraft.allowed_mosaic_methods = methods
        assert set(sddraft.allowed_mosaic_methods) == set(expected)

@pytest.mark.parametrize(("fields"), [
    (["A", "B", "C"]),
    (("D", "E", "F"))
])
def test_available_fields(sddraft, fields):
    sddraft.available_fields = fields
    assert set(sddraft.available_fields) == set(fields)

@pytest.mark.parametrize(("method", "ex"), [
    (ImageSDDraft.ResamplingMethod.nearest_neighbor, None),
    (ImageSDDraft.ResamplingMethod.bilinear, None),
    (ImageSDDraft.ResamplingMethod.cubic, None),
    (ImageSDDraft.ResamplingMethod.majority, None),
    (99, ValueError)
])
def test_default_resampling_method(sddraft, method, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.default_resampling_method = method
    else:
        sddraft.default_resampling_method = method
        assert sddraft.default_resampling_method == method

@pytest.mark.parametrize(("count", "ex"), [
    (50, None),
    (None, None),
    (0, None),
    (-1, ValueError)
])
def test_max_download_image_count(sddraft, count, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_download_image_count = count
    else:
        sddraft.max_download_image_count = count
        assert sddraft.max_download_image_count == count

@pytest.mark.parametrize(("limit", "ex"), [
    (50, None),
    (None, None),
    (0, None),
    (-1, ValueError)
])
def test_max_download_size_limit(sddraft, limit, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_download_size_limit = limit
    else:
        sddraft.max_download_size_limit = limit
        assert sddraft.max_download_size_limit == limit

@pytest.mark.parametrize(("height", "ex"), [
    (1000, None),
    (None, None),
    (0, None),
    (-1, ValueError)
])
def test_max_image_height(sddraft, height, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_image_height = height
    else:
        sddraft.max_image_height = height
        assert sddraft.max_image_height == height

@pytest.mark.parametrize(("width", "ex"), [
    (1000, None),
    (None, None),
    (-1, ValueError)
])
def test_max_image_width(sddraft, width, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_image_width = width
    else:
        sddraft.max_image_width = width
        assert sddraft.max_image_width == width

@pytest.mark.parametrize(("count", "ex"), [
    (30, None),
    (None, None),
    (-1, ValueError)
])
def test_max_mosaic_image_count(sddraft, count, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_mosaic_image_count = count
    else:
        sddraft.max_mosaic_image_count = count
        assert sddraft.max_mosaic_image_count == count

@pytest.mark.parametrize(("enabled", "expected"), TRUEISH_TEST_PARAMS)
def test_return_jpgpng_as_jpg(sddraft, enabled, expected):
    sddraft.return_jpgpng_as_jpg = enabled
    assert sddraft.return_jpgpng_as_jpg == expected