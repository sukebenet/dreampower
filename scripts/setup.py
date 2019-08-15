import argparse
import fileinput
import importlib
from importlib import util
import logging
import os
import subprocess
import sys

spec = importlib.util.spec_from_file_location("_common",
                                              os.path.join(os.path.dirname(os.path.abspath(__file__)), "./_common.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def add_arg_parser(parser):
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


def check_dependencies():
    c.log.debug("OS : {}".format(c.get_os()))
    c.log.debug("Python version : {}".format(c.get_python_version()))

    if c.get_os() == c.OS.UNKNOWN:
        c.log.fatal("Unknown OS !")
        sys.exit(1)

    if c.get_python_version() < (3, 5):
        c.log.fatal("Unsupported python version !")
        sys.exit(1)


def pyinstaller(args, pip_commands_extend=None):
    if pip_commands_extend is None:
        pip_commands_extend = []

    c.log.info('Installing pyinstaller')
    r = subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'] + pip_commands_extend)
    if r.returncode != 0:
        c.log.fatal("Pyinstaller installation failed")
        sys.exit(1)
    c.log.info('Pyinstaller successfully installed')


def cli_setup(args, pip_commands_extend=None):
    if pip_commands_extend is None:
        pip_commands_extend = []

    def torch_version():
        if args.cpu:
            if c.get_os() == c.OS.LINUX:
                return "https://download.pytorch.org/whl/cpu/torch-1.1.0-cp{0}{1}-cp{0}{1}m-linux_x86_64.whl".format(
                    *c.get_python_version())
            if c.get_os() == c.OS.MAC:
                return "torch"
            if c.get_os() == c.OS.WIN:
                return "https://download.pytorch.org/whl/cpu/torch-1.1.0-cp{0}{1}-cp{0}{1}m-win_amd64.whl".format(
                    *c.get_python_version())
        else:
            if c.get_os() == c.OS.LINUX:
                return "https://download.pytorch.org/whl/cu100/torch-1.1.0-cp{0}{1}-cp{0}{1}m-linux_x86_64.whl".format(
                    *c.get_python_version())
            if c.get_os() == c.OS.MAC:
                c.log.warning(
                    "# MacOS Binaries dont support CUDA, install from source if CUDA is needed. "
                    "This script will install the cpu version.")
                return "torch"
            if c.get_os() == c.OS.WIN:
                return "https://download.pytorch.org/whl/cu100/torch-1.1.0-cp{0}{1}-cp{0}{1}m-win_amd64.whl".format(
                    *c.get_python_version())

    c.log.info('Installing Cli dependencies')
    path = c.create_temporary_copy(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../requirements.txt"), "cli-requirements.txt")
    with fileinput.FileInput(path, inplace=True) as f:
        for l in f:
            print(l.replace("torch==1.1.0", torch_version()), end='')
    r = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', path] + pip_commands_extend)
    os.remove(path)
    if r.returncode != 0:
        c.log.fatal("Cli dependencies installation failed")
        sys.exit(1)
    c.log.info('Cli dependencies successfully installed')


def run(args):
    ## System & Dependencies Check
    check_dependencies()

    if args.debug:
        c.log.setLevel(logging.DEBUG)

    ## Cli dependencies
    pip_commands_extend = (['--user'] if args.pip_user else []) + (['--no-cache-dir'] if args.pip_no_cache_dir else [])

    ## Pyinstaller
    if not args.no_pyinstaller:
        pyinstaller(pip_commands_extend)

    cli_setup(args, pip_commands_extend)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='cli dependencies setup')
    add_arg_parser(parser)
    args = parser.parse_args()
    run(args)
