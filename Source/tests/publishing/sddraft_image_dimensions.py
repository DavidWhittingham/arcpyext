import pytest

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