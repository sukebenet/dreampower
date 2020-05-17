import os

import daemon
from argv.checkpoints import arg_checkpoints, set_arg_checkpoints, check_arg_checkpoints
from argv.common import arg_debug, arg_help, arg_version
from argv.run import arg_json_folder_name, arg_json_args, arg_gpu, arg_cpu, arg_preferences, \
    arg_color_transfer, arg_ignore_size, arg_auto_resize_crop, arg_auto_resize, \
    arg_auto_rescale, arg_n_core
from argv.run.config import set_arg_preference, set_gpu_ids
from argv.run.argument import arg_gan_persistent


def init_daemon_sub_parser(subparsers):
    daemon_parser = subparsers.add_parser(
        'daemon',
        description="Running dreampower on daemon mode.",
        help="Running dreampower on daemon mode.",
        add_help=False
    )
    daemon_parser.set_defaults(func=daemon.main)

    # conflicts handler
    processing_mod = daemon_parser.add_mutually_exclusive_group()
    scale_mod = daemon_parser.add_mutually_exclusive_group()

    # add daemon arguments
    arg_input(daemon_parser)
    arg_output(daemon_parser)

    arg_auto_rescale(scale_mod)
    arg_auto_resize(scale_mod)
    arg_auto_resize_crop(scale_mod)
    arg_ignore_size(daemon_parser)

    arg_color_transfer(daemon_parser)

    arg_preferences(daemon_parser)

    arg_cpu(processing_mod)
    arg_gpu(processing_mod)
    arg_checkpoints(daemon_parser)
    arg_n_core(daemon_parser)
    arg_gan_persistent(daemon_parser)

    arg_json_args(daemon_parser)
    arg_json_folder_name(daemon_parser)

    arg_help(daemon_parser)
    arg_debug(daemon_parser)
    arg_version(daemon_parser)

    return daemon_parser


def set_args_daemon_parser(args):
    set_arg_checkpoints(args)
    set_arg_preference(args)
    set_gpu_ids(args)


def check_args_daemon_parser(parser, args):
    check_arg_input(parser, args)
    check_arg_output(parser, args)
    check_arg_checkpoints(parser, args)


def arg_input(parser):
    parser.add_argument(
        "-i",
        "--input",
        help="Path directory to watching.",
        required=True
    )


def arg_output(parser):
    parser.add_argument(
        "-o",
        "--output",
        help="Path of directory where the transformed photo(s) will be saved.",
        required=True
    )


def check_arg_input(parser, args):
    if not args.input:
        parser.error("-i, --input INPUT is required.")
    if not os.path.isdir(args.input):
        parser.error("Input {} directory doesn't exist.".format(args.input))


def check_arg_output(parser, args):
    if not args.output:
        parser.error("-o, --output OUTPUT is required.")
    if not os.path.isdir(args.output):
        parser.error("Output {} directory doesn't exist.".format(args.output))
