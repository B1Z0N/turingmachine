"""

Script that runs all tests written

"""

import os
import pathlib

import pytest

cwd = pathlib.Path.cwd


os.chdir(cwd() / "tests")

def subfolders(dir):
    return [x[0] for x in os.walk(dir)][1:]  # without current directory

for subf in subfolders(cwd()):
    if not subf.endswith("__pycache__"):
        os.chdir(subf)
        pytest.main()


