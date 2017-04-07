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

    if importable("pytest_cov"):
        cmd.append("--cov=arcpyext")
        cmd.append("--cov-report=term")
        cmd.append("--cov-report=html")

    cmd.append(repr(dirname(abspath(__file__))))
    
    pytest.main(" ".join(cmd))

if __name__ == "__main__":
    runtests()