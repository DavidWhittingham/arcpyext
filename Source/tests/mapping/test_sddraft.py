import datetime
import os.path
import shutil

import arcpyext
import pytest

from arcpyext.mapping import SDDraft

SDDRAFT_FILE_PATH = "{0}/samples/example.sddraft".format(os.path.dirname(__file__))
SDDRAFT_FILE_PATH_COPY = "{0}/samples/example.copy.sddraft".format(os.path.dirname(__file__))
SDDRAFT_SAVE_TEST_FILE_PATH = "{0}/samples/example.savetest.sddraft".format(os.path.dirname(__file__))
TRUSISH_TEST_PARAMS = [
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

@pytest.fixture
def sddraft():
    shutil.copyfile(SDDRAFT_FILE_PATH, SDDRAFT_FILE_PATH_COPY)
    return SDDraft(SDDRAFT_FILE_PATH_COPY)

@pytest.mark.parametrize(("mode"), [
    (SDDraft.ANTI_ALIASING_MODES.NONE),
    (SDDraft.ANTI_ALIASING_MODES.FASTEST),
    (SDDraft.ANTI_ALIASING_MODES.FAST),
    (SDDraft.ANTI_ALIASING_MODES.NORMAL),
    (SDDraft.ANTI_ALIASING_MODES.BEST)
])
def test_aa_mode(sddraft, mode):
    sddraft.anti_aliasing_mode = mode
    assert sddraft.anti_aliasing_mode == mode

@pytest.mark.parametrize(("cluster_name", "expected"), [
    ("Default", ["Default"]),
    ("NonDefaultCluster", ["NonDefaultCluster"]),
    (["foo", "bar"], ["foo", "bar"]),
    ("foo,bar", ["foo", "bar"]),
    ("foo, bar, test", ["foo", "bar", "test"])
])
def test_cluster(sddraft, cluster_name, expected):
    sddraft.cluster = cluster_name
    assert set(sddraft.cluster) == set(expected)

@pytest.mark.parametrize(("description"), [
    ("This is a test description"),
    ("This is a much longer test description, it should still work\nIt includes line breaks, we'll see how they go."),
    ("")
])
def test_description(sddraft, description):
    sddraft.description = description
    assert sddraft.description == description
    
@pytest.mark.parametrize(("disabled", "expected"), TRUSISH_TEST_PARAMS)
def test_disable_indentify_relates(sddraft, disabled, expected):
    sddraft.disable_identify_relates = disabled
    assert sddraft.disable_identify_relates == expected

@pytest.mark.parametrize(("enabled", "expected"), TRUSISH_TEST_PARAMS)
def test_enable_dynamic_layers(sddraft, enabled, expected):
    sddraft.enable_dynamic_layers = enabled
    assert sddraft.enable_dynamic_layers == expected

@pytest.mark.parametrize(("enabled_extensions"), [
    ([SDDraft.EXTENSIONS.KMLSERVER]),
    ([SDDraft.EXTENSIONS.KMLSERVER, SDDraft.EXTENSIONS.MOBILESERVER]),
    ([])
])
def test_enabled_extensions(sddraft, enabled_extensions):
    sddraft.enabled_extensions = enabled_extensions
    assert set(sddraft.enabled_extensions) == set(enabled_extensions)
    
@pytest.mark.parametrize(("enabled_ops", "expected", "ex"), [
    (["Query"], ["Query"], None),
    (["quErY"], ["Query"], None),
    ([SDDraft.FEATURE_ACCESS_OPERATIONS.CREATE, SDDraft.FEATURE_ACCESS_OPERATIONS.UPDATE], ["Create", "Update"], None),
    (["Foo", "Bar"], None, ValueError)
])
def test_feature_access_enabled_operations(sddraft, enabled_ops, expected, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.feature_access_enabled_operations = enabled_ops
    else:
        sddraft.feature_access_enabled_operations = enabled_ops
        assert set(sddraft.feature_access_enabled_operations) == set(expected)

@pytest.mark.parametrize(("file_path", "equal"), [
    (SDDRAFT_FILE_PATH_COPY, True),
    ("./FooBar", False),
])
def test_file_path(sddraft, file_path, equal):
    assert (os.path.normpath(sddraft.file_path) == os.path.normpath(file_path)) == equal

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
    
@pytest.mark.parametrize(("instances"), [
    (1), (2), (8)
])
def test_instances_per_container(sddraft, instances):
    sddraft.instances_per_container = instances
    assert sddraft.instances_per_container == instances
    
@pytest.mark.parametrize(("keep_cache", "expected"), TRUSISH_TEST_PARAMS)
def test_keep_cache(sddraft, keep_cache, expected):
    sddraft.keep_cache = keep_cache
    assert sddraft.keep_cache == expected
    
@pytest.mark.parametrize(("min_number", "max_number", "ex"), [
    (0, -1, ValueError),
    (0, 0, ValueError),
    (0, 2, None),
    (1, 8, None), 
    (5, 2, ValueError)
])
def test_max_instances(sddraft, min_number, max_number, ex):
    sddraft.min_instances = min_number

    if (ex != None):
        with pytest.raises(ex):
            sddraft.max_instances = max_number
    else:
        sddraft.max_instances = max_number
        assert sddraft.max_instances == max_number
        
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

@pytest.mark.parametrize(("number", "ex"), [
    (-1, ValueError),
    (0, None),
    (2, None),
    (8, None)
])
def test_min_instances(sddraft, number, ex):
    if (ex != None):
        with pytest.raises(ex):
            sddraft.min_instances = number
    else:
        sddraft.min_instances = number
        assert sddraft.min_instances == number

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

@pytest.mark.parametrize(("replace", "expected"), TRUSISH_TEST_PARAMS)
def test_replace_existing(sddraft, replace, expected):
    sddraft.replace_existing = replace
    assert sddraft.replace_existing == expected
    
def test_save(sddraft):
    sddraft.save()
    assert True

@pytest.mark.parametrize(("output"), [
    (SDDRAFT_SAVE_TEST_FILE_PATH)
])
def test_save_a_copy(sddraft, output):
    sddraft.save_a_copy(output)
    assert os.path.isfile(output) == True
    
@pytest.mark.parametrize(("enabled", "expected"), TRUSISH_TEST_PARAMS)
def test_schema_locking_enabled(sddraft, enabled, expected):
    sddraft.schema_locking_enabled = enabled
    assert sddraft.schema_locking_enabled == expected
    
@pytest.mark.parametrize(("summary"), [
    ("A test summary"), ("A test summary.\nIt also has line breaks."), ("")
])
def test_summary(sddraft, summary):
    sddraft.summary = summary
    assert sddraft.summary == summary

@pytest.mark.parametrize(("mode"), [
    (SDDraft.TEXT_ANTI_ALIASING_MODES.NONE),
    (SDDraft.TEXT_ANTI_ALIASING_MODES.FORCE),
    (SDDraft.TEXT_ANTI_ALIASING_MODES.NORMAL)
])
def test_text_aa_mode(sddraft, mode):
    sddraft.text_anti_aliasing_mode = mode
    assert sddraft.text_anti_aliasing_mode == mode

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
