import arcpyext
import pytest



def test_update_toolbox_descriptions():
    toolboxPath='samples/test_python_toolbox.pyt'
    pt=arcpyext.toolbox.PythonToolbox(toolboxPath)
    pt.load()
    pt.load_xml()
    pt.apply_toolbox_descriptions()
    pt.save_definitions()
