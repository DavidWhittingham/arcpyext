import datetime

import pytest

from .. helpers import *

SCALES = [
    (1.1, 1.1),
    ("1.1", 1.1)
]

@pytest.mark.parametrize(("access_information"), [
    ("This is a test description"),
    ("This is a much longer test description, it should still work\nIt includes line breaks, we'll see how they go."),
    ("")
])
def test_access_information(sddraft, access_information):
    sddraft.access_information = access_information
    assert sddraft.access_information == access_information

@pytest.mark.parametrize(("cluster_name", "expected"), [
    ("Default", "Default"),
    ("NonDefaultCluster", "NonDefaultCluster")
])
def test_cluster(sddraft, cluster_name, expected):
    sddraft.cluster = cluster_name
    assert sddraft.cluster == expected

@pytest.mark.parametrize(("description"), [
    ("This is a test description"),
    ("This is a much longer test description, it should still work\nIt includes line breaks, we'll see how they go."),
    ("")
])
def test_description(sddraft, description):
    sddraft.description = description
    assert sddraft.description == description

@pytest.mark.parametrize(("folder", "expected", "ex"), [
    ("TestName", "TestName", None),
    ("", None, None),
    (None, None, None)
])
def test_folder(sddraft, folder, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.folder = folder
    else:
        sddraft.folder = folder
        assert sddraft.folder == expected

@pytest.mark.parametrize(("high_isolation"), [
    (True), (False), (1), (0)
])
def test_high_isolation(sddraft, high_isolation):
    sddraft.high_isolation = high_isolation
    assert sddraft.high_isolation == bool(high_isolation)

@pytest.mark.parametrize(("timeout", "ex"), [
    (0, None),
    (100, None),
    (99999, None),
    (-10, ValueError)
])
def test_idle_timeout(sddraft, timeout, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.idle_timeout = timeout
    else:
        sddraft.idle_timeout = timeout
        assert sddraft.idle_timeout == timeout

@pytest.mark.parametrize(("scale", "exp_scale"), SCALES)
def text_max_scale(sddraft, scale, exp_scale):
    sddraft.max_scale = scale
    assert sddraft.max_scale == exp_scale

@pytest.mark.parametrize(("scale", "exp_scale"), SCALES)
def text_min_scale(sddraft, scale, exp_scale):
    sddraft.min_scale = scale
    assert sddraft.min_scale == exp_scale

@pytest.mark.parametrize(("instances"), [
    (1), (2), (8)
])
def test_instances_per_container(sddraft, instances):
    sddraft.instances_per_container = instances
    assert sddraft.instances_per_container == instances

@pytest.mark.parametrize(("min_number", "max_number", "exp_min", "exp_max", "ex"), [
    (0, -1, None, None, ValueError),
    (0, 0, None, None, ValueError),
    (0, 2, 0, 2, None),
    (1, 8, 1, 8, None),
    (5, 2, 2, 2, None)
])
def test_instances_counts(sddraft, min_number, max_number, exp_min, exp_max, ex):
    assert isinstance(type(sddraft).min_instances, property) == True
    assert isinstance(type(sddraft).max_instances, property) == True

    if (ex != None):
        with pytest.raises(ex):
            sddraft.min_instances = min_number
            sddraft.max_instances = max_number
    else:
        sddraft.min_instances = min_number
        sddraft.max_instances = max_number
        assert sddraft.min_instances == exp_min
        assert sddraft.max_instances == exp_max

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

@pytest.mark.parametrize(("name", "ex"), [
    ("TestName", None), ("", ValueError)
])
def test_name(sddraft, name, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.name = name
    else:
        sddraft.name = name
        assert sddraft.name == name

@pytest.mark.parametrize(("interval", "ex"), [
    (0, None),
    (12, None),
    (-10, ValueError)
])
def test_recycle_interval(sddraft, interval, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.recycle_interval = interval
    else:
        sddraft.recycle_interval = interval
        assert sddraft.recycle_interval == interval

@pytest.mark.parametrize(("input", "expected", "ex"), [
    ("12:01", datetime.time(12, 01), None),
    (datetime.time(14, 35), datetime.time(14, 35), None),
    ("nonsense", None, ValueError)
])
def test_recycle_start_time(sddraft, input, expected, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.recycle_start_time = input
    else:
        sddraft.recycle_start_time = input
        assert sddraft.recycle_start_time == expected

@pytest.mark.parametrize(("replace", "expected"), TRUEISH_TEST_PARAMS)
def test_replace_existing(sddraft, replace, expected):
    sddraft.replace_existing = replace
    assert sddraft.replace_existing == expected

@pytest.mark.parametrize(("summary"), [
    ("A test summary"), ("A test summary.\nIt also has line breaks."), ("")
])
def test_summary(sddraft, summary):
    sddraft.summary = summary
    assert sddraft.summary == summary

@pytest.mark.parametrize(("title"), [
    ("This is a title"),
    ("This is a much longer title, it should still work\nIt includes line breaks, we'll see how they go."),
    ("")
])
def test_title(sddraft, title):
    sddraft.title = title
    assert sddraft.title == title

@pytest.mark.parametrize(("timeout", "ex"), [
    (0, None),
    (100, None),
    (99999, None),
    (-10, ValueError)
])
def test_usage_timeout(sddraft, timeout, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.usage_timeout = timeout
    else:
        sddraft.usage_timeout = timeout
        assert sddraft.usage_timeout == timeout

@pytest.mark.parametrize(("timeout", "ex"), [
    (0, None),
    (100, None),
    (99999, None),
    (-10, ValueError)
])
def test_wait_timeout(sddraft, timeout, ex):
    if ex != None:
        with pytest.raises(ex):
            sddraft.wait_timeout = timeout
    else:
        sddraft.wait_timeout = timeout
        assert sddraft.wait_timeout == timeout
