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

    if importable("pytest_cov"):
        cmd.append("--cov=arcpyext")
        cmd.append("--cov-report=term")
        cmd.append("--cov-report=html")

        # Discover the environment and set appropriate coverage
        if importable("arcpy.mapping"):
            # py2 arc desktop
            cmd.append("--cov-config=tests\\.coveragerc2")
        else:
            # py3 arc pro
            cmd.append("--cov-config=tests\\.coveragerc3")

    cmd.append(thisDir)

    pytest.main(cmd)

if __name__ == "__main__":
    runtests()