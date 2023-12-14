import subprocess
import Widgets

DEV_MODULES = ["flake8 Widgets", "black Widgets", "mypy Widgets", "pytest"]


def all_check():
    processes = [subprocess.Popen(file) for file in DEV_MODULES]
    for process in processes:
        process.wait()


all_check()
