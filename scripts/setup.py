import argparse
import fileinput
import logging

import subprocess

import os

import sys
from _common import get_os, setup_log, OS, create_temporary_copy, get_python_version, cd

parser = argparse.ArgumentParser(description='cli dependencies setup')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Set log level to Debug')
parser.add_argument('-np', '--no_pyinstaller', action='store_true',
                    help='Don\'t install pyinstaller')
parser.add_argument('--cpu', action='store_true',
                    help='No cuda support')
parser.add_argument('-pnc', '--pip_no_cache_dir', action='store_true',
                    help='Use --no_cache_dir for pip commands')
parser.add_argument('-pu', '--pip_user', action='store_true',
                    help='Use --user for pip commands')
args = parser.parse_args()

log = setup_log(logging.DEBUG if args.debug else logging.INFO)

## System & Dependencies Check
detected_os = get_os()
detected_py = get_python_version()
log.debug("OS : {}".format(detected_os))
log.debug("Python version : {}".format(detected_py))

if detected_os == OS.UNKNOWN:
    log.fatal("Unknown OS !")
    exit(1)

if detected_py < (3, 5):
    log.fatal("Unsupported python version !")
    exit(1)

## Cli dependencies
pip_commands_extend = (['--user'] if args.pip_user else []) + (['--no-cache-dir'] if args.pip_no_cache_dir else [])


## Pyinstaller
if not args.no_pyinstaller:
    log.info('Installing pyinstaller')
    r = subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'] + pip_commands_extend)
    if r.returncode != 0:
        log.fatal("Pyinstaller installation failed")
        exit(1)
    log.info('Pyinstaller successfully installed')


def torch_version():
    if args.cpu:
        if detected_os == OS.LINUX:
            return "https://download.pytorch.org/whl/cpu/torch-1.1.0-cp{0}{1}-cp{0}{1}m-linux_x86_64.whl".format(
                *get_python_version())
        if detected_os == OS.MAC:
            return "torch"
        if detected_os == OS.WIN:
            return "https://download.pytorch.org/whl/cpu/torch-1.1.0-cp{0}{1}-cp{0}{1}m-win_amd64.whl".format(
                *get_python_version())
    else:
        if detected_os == OS.LINUX:
            return "https://download.pytorch.org/whl/cu100/torch-1.1.0-cp{0}{1}-cp{0}{1}m-linux_x86_64.whl".format(
                *get_python_version())
        if detected_os == OS.MAC:
            log.warning(
                "# MacOS Binaries dont support CUDA, install from source if CUDA is needed. This script will install "
                "the cpu version.")
            return "torch"
        if detected_os == OS.WIN:
            return "https://download.pytorch.org/whl/cu100/torch-1.1.0-cp{0}{1}-cp{0}{1}m-win_amd64.whl".format(
                *get_python_version())


log.info('Installing Cli dependencies')
path = create_temporary_copy("../requirements-generic.txt", "cli-requirements.txt")
with fileinput.FileInput(path, inplace=True) as f:
    for l in f:
        print(l.replace("torch==1.1.0", torch_version()), end='')
r = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', path] + pip_commands_extend)
os.remove(path)
if r.returncode != 0:
    log.fatal("Cli dependencies installation failed")
    exit(1)
log.info('Cli dependencies successfully installed')
