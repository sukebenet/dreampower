import argparse
import copy
import logging
import sys

from config import Config as Conf
from argv.checkpoints import init_checkpoints_sub_parser, check_args_checkpoints_parser, set_args_checkpoints_parser
from argv.common import arg_help, arg_debug, arg_version
from argv.daemon import init_daemon_sub_parser, check_args_daemon_parser, set_args_daemon_parser
from argv.gpu_info import init_gpu_info_sub_parser
from argv.run import init_run_parser
from argv.run.config import set_args_run_parser, check_args_run_parser
from utils import setup_log, json_to_argv


class Parser:
    parser = None


def run():
    Parser.parser = init_parser()

    if len(sys.argv) == 1:
        Parser.parser.print_usage()
        Parser.parser.exit()

    args = Parser.parser.parse_args()

    Conf.log = setup_log(logging.DEBUG) if args.debug else setup_log()
    args = config_args(Parser.parser, args)

    Conf.log.debug(args)

    Conf.args = vars(args)
    args.func(args)


def init_parser():
    parser = argparse.ArgumentParser(
        description="Dreampower CLI application that allow to transform photos of people for private entertainment",
        add_help=False
    )

    # add args main
    arg_help(parser)
    arg_debug(parser)
    arg_version(parser)

    # add subparsers
    subparsers = parser.add_subparsers(dest="mode")
    init_run_parser(subparsers)
    init_checkpoints_sub_parser(subparsers)
    init_gpu_info_sub_parser(subparsers)
    init_daemon_sub_parser(subparsers)

    return parser


def config_args(parser, args, json_data=None):
    args = copy.deepcopy(args)
    set_args_parser(parser, args)
    check_args_parser(parser, args)
    if args.mode == "run":
        return merge_json_args(parser, args, json_data)
    else:
        return args


def check_args_parser(parser, args):
    if args.mode == "run":
        check_args_run_parser(parser, args)

    if args.mode == "checkpoints":
        check_args_checkpoints_parser(parser, args)

    if args.mode == "daemon":
        check_args_daemon_parser(parser, args)

    return parser


def set_args_parser(parser, args):
    if args.mode == "run":
        set_args_run_parser(args)

    if args.mode == "checkpoints":
        set_args_checkpoints_parser(args)

    if args.mode == "daemon":
        set_args_daemon_parser(args)

    return parser


def merge_json_args(parser, args, json_data=None):
    def filter_conflict_args(l1, l2):
        # l2 args got priority on l1
        l1 = copy.copy(l1)
        l2 = copy.copy(l2)
        # Handle special cases for ignoring arguments in json file if provided in command line
        if "--cpu" in l2 or "--gpu" in l2:
            l1 = list(filter(lambda x: x not in ("--cpu", "--gpu"), l1))

        if "--auto-resize" in l2 or "--auto-resize-crop" in l2 \
                or "--auto-rescale" in l2 or "--overlay" in l2:
            l1 = list(filter(lambda x: x not in ("--auto-resize", "--auto-resize-crop", "--auto-rescale"), l1))
            if "--overlay" in l1:
                del l1[l1.index("--overlay"):l1.index("--overlay") + 1]

        return l1 + l2

    # merge args
    cmdline_args = []
    if not json_data and not args.json_args:
        return args
    elif json_data and args.json_args:
        cmdline_args = filter_conflict_args(json_to_argv(json_data), json_to_argv(args.json_args))
    elif json_data and not args.json_args:
        cmdline_args = json_to_argv(json_data)
    elif not json_data and args.json_args:
        cmdline_args = json_to_argv(args.json_args)

    cmdline_args = filter_conflict_args(cmdline_args, sys.argv[1:])

    # remove json-args arg
    i = 0
    while i < len(cmdline_args):
        if "--json-args" == cmdline_args[i]:
            del cmdline_args[i:i + 2]
        i += 1

    # replace run arg
    cmdline_args.index('run')
    cmdline_args.remove('run')
    cmdline_args.insert(0, 'run')

    return config_args(parser, parser.parse_args(cmdline_args))
