import argparse
import importlib
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


def check_dependencies():
    ## System & Dependencies Check
    c.log.debug("OS : {}".format(c.get_os()))
    c.log.debug("Python version : {}".format(c.get_python_version()))

    if c.get_os() == c.OS.UNKNOWN:
        c.log.fatal("Unknown OS !")
        exit(1)

    if c.get_python_version() < (3, 5):
        c.log.fatal("Unsupported python version !")
        exit(1)

    if not c.check_pyinstaller():
        c.log.fatal("Pyinstaller is not install. It's a required dependency !")
        exit(1)


def cli_build(args, dist_path="./dist"):
    def pyinstaller_args():
        pyinstaller_args = [
            '--workpath=./build/',
            '--specpath=.',
            '-y',
            '--onedir',
            '--name=dreampower',
            '--distpath={}'.format(dist_path),
            'main.py',
        ]
        if c.get_os() == c.OS.LINUX:
            return pyinstaller_args
        if c.get_os() == c.OS.MAC:
            pyinstaller_args.extend(['--add-binary=/System/Library/Frameworks/Tk.framework/Tk:tk'])
            pyinstaller_args.extend(['--add-binary=/System/Library/Frameworks/Tcl.framework/Tcl:tcl'])
            return pyinstaller_args
        if c.get_os() == c.OS.WIN:
            pyinstaller_args.extend(['--add-binary=./third/msvcp/msvcp140.dll;.'])
            return pyinstaller_args

    c.log.info('Building Cli')
    with c.cd(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")):
        cmd = [sys.executable, '-m', 'PyInstaller'] + pyinstaller_args()
        c.log.debug(cmd)
        r = subprocess.run(cmd)
        if r.returncode != 0:
            c.log.fatal("Cli build failed")
            exit(1)
    c.log.info('Cli successfully built')


def run(args, dist_path="./dist"):
    cli_build(args, dist_path)

    c.log.info('Build completed!')
    c.log.info(
        'It should have generated a folder called dist/, inside you will find '
        'the final project files that you can share with everyone!')
    c.log.info('Enjoy and remember to respect the License!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='cli builder')
    add_arg_parser(parser)
    args = parser.parse_args()

    check_dependencies()

    if args.debug:
        c.log.setLevel(logging.DEBUG)

    ## Build Cli
    run(args)
