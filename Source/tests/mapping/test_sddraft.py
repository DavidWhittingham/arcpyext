import pytest
import os.path

import arcpyext

SDDRAFT_FILE_PATH = "{0}/samples/example.sddraft".format(os.path.dirname(__file__))

def pytest_funcarg__sddraft():
    return arcpyext.mapping.SDDraft(SDDRAFT_FILE_PATH)

@pytest.mark.parametrize(("mode"), [
    (arcpyext.mapping.SDDraft.ANTI_ALIASING_MODES.NONE),
    (arcpyext.mapping.SDDraft.ANTI_ALIASING_MODES.FASTEST),
    (arcpyext.mapping.SDDraft.ANTI_ALIASING_MODES.FAST),
    (arcpyext.mapping.SDDraft.ANTI_ALIASING_MODES.NORMAL),
    (arcpyext.mapping.SDDraft.ANTI_ALIASING_MODES.BEST)
])
def test_aa_mode(sddraft, mode):
    sddraft.anti_aliasing_mode = mode
    assert sddraft.anti_aliasing_mode == mode

@pytest.mark.parametrize(("cluster_name"), [
    ("Default"),
    ("NonDefaultCluster")
])
def test_cluster(sddraft, cluster_name):
    sddraft.cluster = cluster_name
    assert sddraft.cluster == cluster_name

@pytest.mark.parametrize(("description"), [
    ("This is a test description"),
    ("This is a much longer test description, it should still work\nIt includes line breaks, we'll see how they go."),
    ("")
])
def test_description(sddraft, description):
    sddraft.description = description
    assert sddraft.description == description

@pytest.mark.parametrize(("enabled_extensions"), [
    ([arcpyext.mapping.SDDraft.EXTENSIONS.KMLSERVER]),
    ([arcpyext.mapping.SDDraft.EXTENSIONS.KMLSERVER, arcpyext.mapping.SDDraft.EXTENSIONS.MOBILESERVER]),
    ([])
])
def test_enabled_extensions(sddraft, enabled_extensions):
    sddraft.enabled_extensions = enabled_extensions
    assert set(sddraft.enabled_extensions) == set(enabled_extensions)

@pytest.mark.parametrize(("file_path", "equal"), [
    (SDDRAFT_FILE_PATH, True),
    ("./FooBar", False),
])
def test_file_path(sddraft, file_path, equal):
    assert (os.path.normpath(sddraft.file_path) == os.path.normpath(file_path)) == equal

@pytest.mark.parametrize(("instances"), [
    (1), (2), (8)
])
def test_instances_per_container(sddraft, instances):
    sddraft.instances_per_container = instances
    assert sddraft.instances_per_container == instances

@pytest.mark.parametrize(("high_isolation"), [
    (True), (False), (1), (0)
])
def test_high_isolation(sddraft, high_isolation):
    sddraft.high_isolation = high_isolation
    assert sddraft.high_isolation == bool(high_isolation)

@pytest.mark.parametrize(("number", "raises_ex", "ex"), [
    (-1, True, ValueError), (0, False, None), (2, False, None), (8, False, None)
])
def test_min_instances(sddraft, number, raises_ex, ex):
    if (raises_ex):
        with pytest.raises(ex):
            sddraft.min_instances = number
    else:
        sddraft.min_instances = number
        assert sddraft.min_instances == number

@pytest.mark.parametrize(("min_number", "max_number", "raises_ex", "ex"), [
    (0, -1, True, ValueError), (0, 0, True, ValueError), (0, 2, False, None), (1, 8, False, None), 
    (5, 2, True, ValueError)
])
def test_max_instances(sddraft, min_number, max_number, raises_ex, ex):
    sddraft.min_instances = min_number

    if (raises_ex):
        with pytest.raises(ex):
            sddraft.max_instances = max_number
    else:
        sddraft.max_instances = max_number
        assert sddraft.max_instances == max_number

@pytest.mark.parametrize(("name", "raises_ex", "ex"), [
    ("TestName", False, None), ("", True, ValueError)
])
def test_name(sddraft, name, raises_ex, ex):
    if (raises_ex):
        with pytest.raises(ex):
            sddraft.name = name
    else:
        sddraft.name = name
        assert sddraft.name == name

@pytest.mark.parametrize(("replace"), [
    (True), (False), (1), (0)
])
def test_replace_existing(sddraft, replace):
    sddraft.replace_existing = replace
    assert sddraft.replace_existing == bool(replace)

@pytest.mark.parametrize(("summary"), [
    ("A test summary"), ("A test summary.\nIt also has line breaks."), ("")
])
def test_summary(sddraft, summary):
    sddraft.summary = summary
    assert sddraft.summary == summary

@pytest.mark.parametrize(("mode"), [
    (arcpyext.mapping.SDDraft.TEXT_ANTI_ALIASING_MODES.NONE),
    (arcpyext.mapping.SDDraft.TEXT_ANTI_ALIASING_MODES.FORCE),
    (arcpyext.mapping.SDDraft.TEXT_ANTI_ALIASING_MODES.NORMAL)
])
def test_text_aa_mode(sddraft, mode):
    sddraft.text_anti_aliasing_mode = mode
    assert sddraft.text_anti_aliasing_mode == mode

@pytest.mark.parametrize(("timeout"), [
    (20), (100), (600)
])
def test_wait_timeout(sddraft, timeout):
    sddraft.wait_timeout = timeout
    assert sddraft.wait_timeout == timeout
