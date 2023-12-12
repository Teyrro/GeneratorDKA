import pathlib
import subprocess
from enum import Enum
import sys

DEV_MODULES = ["flake8 Widgets", "black Widgets", "mypy Widgets"]


def all_check():
    processes = [subprocess.Popen(file) for file in DEV_MODULES]
    for process in processes:
        process.wait()


all_check()
