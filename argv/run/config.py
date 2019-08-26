import os

import gpu_info
from argv.checkpoints import set_arg_checkpoints, check_arg_checkpoints
from utils import check_image_file_validity, is_a_supported_image_file_extension


def set_args_run_parser(args):
    set_arg_checkpoints(args)
    set_arg_preference(args)
    set_gpu_ids(args)


def check_args_run_parser(parser, args):
    check_arg_input(parser, args)
    check_arg_output(parser, args)
    check_args_altered(parser, args)
    check_arg_checkpoints(parser, args)


def check_args_altered(parser, args):
    if args.steps and not args.altered:
        parser.error("--steps requires --altered.")
    elif args.steps and args.altered:
        if not os.path.isdir(args.altered):
            parser.error("{} directory doesn't exist.".format(args.altered))


def set_gpu_ids(args):
    if args.cpu:
        args.gpu_ids = None
    elif args.gpu:
        args.gpu_ids = args.gpu
    else:
        args.gpu_ids = None if not gpu_info.get_info()['has_cuda'] else [0]


def check_arg_input(parser, args):
    if not args.input:
        parser.error("-i, --input INPUT is required.")
    if not os.path.isdir(args.input) and not os.path.isfile(args.input):
        parser.error("Input {} file or directory doesn't exist.".format(args.input))
    elif os.path.isfile(args.input) and not is_a_supported_image_file_extension(args.input):
        parser.error("Input {} file not supported format.".format(args.input))
    if os.path.isfile(args.input):
        check_image_file_validity(args.input)
    return args.input


def check_arg_output(parser, args):
    if os.path.isfile(args.input) and not args.output:
        _, extension = os.path.splitext(args.input)
        args.output = "output{}".format(extension)
    elif args.output and os.path.isfile(args.input) and not is_a_supported_image_file_extension(args.output):
        parser.error("Output {} file not a supported format.".format(args.output))


def set_arg_preference(args):
    args.prefs = {
        "titsize": args.bsize,
        "aursize": args.asize,
        "nipsize": args.nsize,
        "vagsize": args.vsize,
        "hairsize": args.hsize
    }
