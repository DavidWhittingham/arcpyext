import sys

from types import ModuleType
from os.path import abspath, dirname

import pytest

def importable(module):
    try:
        m = __import__(module, globals(), locals())
        return type(m) is ModuleType
    except ImportError:
        return False

def runtests():
    cmd = ["-r fsxX"]
    thisDir = dirname(abspath(__file__))

    # Discover the environment and run appropriate tests
    if importable("arcpy.mapping"):
        # py2 arc desktop
        cmd.append("--ignore=tests\\mp\\")
    else:
        # py3 arc pro
        cmd.append("--ignore=tests\\mapping\\")
        cmd.append("--ignore=tests\\arcobjects\\test_arcobjects.py")

    if importable("pytest_cov"):
        cmd.append("--cov=arcpyext")
        cmd.append("--cov-report=term")
        cmd.append("--cov-report=html")

    cmd.append(thisDir)
    #cmd.append("C:/git/arcpyext/tests/publishing/test_wps_server_extension.py")
    
    pytest.main(cmd)
    
if __name__ == "__main__":
    runtests()