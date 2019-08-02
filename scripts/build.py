import argparse
import logging

import subprocess
import shutil

import sys

from _common import get_os, setup_log, OS, get_python_version, cd, check_pyinstaller

parser = argparse.ArgumentParser(description='cli builder')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Set log level to Debug')

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

if not check_pyinstaller():
    log.fatal("Pyinstaller is not install. It's a required dependency !")
    exit(1)


## Build Cli
def pyinstaller_args():
    pyinstaller_args = [
        '--workpath=./build/',
        '--specpath=.',
        '-y',
        '--onedir',
        '--name=cli',
        'main.py',
    ]
    if detected_os == OS.LINUX:
        return pyinstaller_args
    if detected_os == OS.MAC:
        return pyinstaller_args
    if detected_os == OS.WIN:
        pyinstaller_args.extend(['--add-binary=./third/msvcp/msvcp140.dll;.'])
        return pyinstaller_args


log.info('Building Cli')
with cd(".."):
    cmd = [sys.executable, '-m', 'PyInstaller'] + pyinstaller_args()
    log.debug(cmd)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        log.fatal("Cli build failed")
        exit(1)
log.info('Cli successfully built')

log.info('Build completed!')
log.info(
    'It should have generated a folder called dist/, inside you will find the final project files that you can share with everyone!')
log.info('Enjoy and remember to respect the License!')
