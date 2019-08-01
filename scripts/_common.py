import logging
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from enum import Enum
from sys import platform as _platform


class OS(Enum):
    UNKNOWN = "unknown"
    LINUX = "linux"
    MAC = "mac"
    WIN = "win"


def get_os():
    if _platform == "linux" or _platform == "linux2":
        return OS.LINUX
    elif _platform == "darwin":
        return OS.MAC
    elif _platform == "win32" or _platform == "win64":
        return OS.WIN
    else:
        return OS.UNKNOWN


def get_python_version():
    return sys.version_info[0], sys.version_info[1]


def check_pyinstaller():
    return shutil.which("pyinstaller")


def setup_log(log_lvl=logging.DEBUG):
    log = logging.getLogger(__name__)
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    log.addHandler(out_hdlr)
    log.setLevel(log_lvl)
    return log

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def create_temporary_copy(path, copy_name):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, copy_name)
    shutil.copy2(path, temp_path)
    return temp_path

def wait_subprocs(poller):
    while True:
        for fd, flags in poller.poll(timeout=1):  # never more than a second without a UI update
            poller.unregister(fd)