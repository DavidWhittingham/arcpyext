import os
import arcpyext
import pytest

#TOOLBOX_PATH=os.path.abspath("{0}/../samples/test_python_toolbox.pyt".format(os.path.dirname(__file__)))
TOOLBOX_PATH=os.path.abspath("{0}/../samples/Toolbox.pyt".format(os.path.dirname(__file__)))

def test_update_toolbox_descriptions():
    pt=arcpyext.toolbox.PythonToolbox(TOOLBOX_PATH)
    pt.load()
    pt.load_xml()
    pt.apply_toolbox_descriptions()
    pt.save_definitions()
