import argparse
import json
import os
import re
import sys
from json import JSONDecodeError

import gpu_info
from main import main
from config import Config as conf


def set_config_args(args):
    def set_body_parts_prefs():
        prefs = {
            "titsize": args.bsize,
            "aursize": args.asize,
            "nipsize": args.nsize,
            "vagsize": args.vsize,
            "hairsize": args.hsize
        }
        return prefs

    def set_gpu_ids():
        gpu_ids = args.gpu
        if args.cpu:
            gpu_ids = None
        elif gpu_ids is None:
            gpu_ids = [0]
        return gpu_ids

    conf.args = vars(args)
    conf.args['gpu_ids'] = set_gpu_ids()
    conf.args['prefs'] = set_body_parts_prefs()


def check_args(args):
    def check_args_in():
        if not os.path.isfile(args.input):
            print("Error : {} file doesn't exist".format(
                args.input), file=sys.stderr)
            sys.exit(1)

    def check_args_out():
        if not args.output:
            _, extension = os.path.splitext(args.input)
            args.output = "output{}".format(extension)
    check_args_out()
    check_args_in()


def run():
    """
    Run argparse for Dreampower
    :return: None
    """
    parser = argparse.ArgumentParser(
        description="Dreampower CLI application that allow to transform photos of people for "
                    "private entertainment")
    subparsers = parser.add_subparsers()
    parser.add_argument(
        "-d", "--debug", action="store_true", help="enble log debug mod"
    )
    parser.add_argument(
        "-i", "--input", help="path of the photo to transform", required=True
    )
    parser.add_argument(
        "-o",
        "--output",
        help="path where the transformed photo will be saved. (default: output.<input extension>)",
    )
    processing_mod = parser.add_mutually_exclusive_group()
    processing_mod.add_argument(
        "--cpu",
        default=False,
        action="store_true",
        help="force photo processing with CPU (slower)",
    )
    processing_mod.add_argument(
        "--gpu",
        action="append",
        type=int,
        help="ID of the GPU to use for processing. "
             "It can be used multiple times to specify multiple GPUs (Example: --gpu 0 --gpu 1 --gpu 2)"
             " This argument will be ignored if --cpu is active. (default: 0)",
    )
    parser.add_argument(
        "--bsize",
        type=float,
        default=1,
        help="Boob size scalar best results 0.3 - 2.0",
    )
    parser.add_argument(
        "--asize",
        type=float,
        default=1,
        help="Areola size scalar best results 0.3 - 2.0",
    )
    parser.add_argument(
        "--nsize",
        type=float,
        default=1,
        help="Nipple size scalar best results 0.3 - 2.0",
    )
    parser.add_argument(
        "--vsize",
        type=float,
        default=1,
        help="Vagina size scalar best results 0.3 - 1.5",
    )
    parser.add_argument(
        "--hsize",
        type=float,
        default=0,
        help="Pubic hair size scalar best results set to 0 to disable",
    )
    parser.add_argument(
        "--gif", action="store_true", default=False, help="run the processing on a gif"
    )
    parser.add_argument(
        "-n", "--n_runs", type=int, default=1, help="number of times to process input (default: 1)",
    )
    parser.add_argument(
        "--n_cores", type=int, default=1, help="number of cpu cores to use (default: 1)",
    )

    scale_mod = parser.add_mutually_exclusive_group()
    scale_mod.add_argument(
        "--auto-resize",
        action="store_true",
        default=False,
        help="Scale and pad image to 512x512 (maintains aspect ratio)",
    )
    scale_mod.add_argument(
        "--auto-resize-crop",
        action="store_true",
        default=False,
        help="Scale and crop image to 512x512 (maintains aspect ratio)",
    )
    scale_mod.add_argument(
        "--auto-rescale",
        action="store_true",
        default=False,
        help="Scale image to 512x512",
    )

    gpu_info_parser = subparsers.add_parser('gpu-info')

    gpu_info_parser.add_argument(
        "-j",
        "--json",
        default=False,
        action="store_true",
        help="Print GPU info as JSON"
    )

    def check_crops_coord():
        def type_func(a):
            if not re.match(r"^\d+,\d+:\d+,\d+$", a):
                raise argparse.ArgumentTypeError("Incorrect coordinates format. "
                                                 "Valid format is <x_top_left>,<y_top_left>:<x_bot_right>,<x_bot_right>")
            return tuple(int(x) for x in re.findall('\d+', a))

        return type_func

    scale_mod.add_argument(
        "--overlay",
        type=check_crops_coord(),
        help="Processing the part of the image given by the coordinates "
             "(<x_top_left>,<y_top_left>:<x_bot_right>,<x_bot_right>) and overlay the result on the original image.",
    )

    def check_json_args_file():
        def type_func(a):
            if not os.path.isfile(a):
                raise argparse.ArgumentTypeError(
                    "Arguments json file {} not found.".format(a))
            with open(a) as f:
                data = {}
                try:
                    data = json.load(f)
                except JSONDecodeError:
                    raise argparse.ArgumentTypeError(
                        "Arguments json file {} is not in valid JSON format.".format(a))
            l = []
            for k, v in data.items():
                if not isinstance(v, bool):
                    l.extend(["--{}".format(k), str(v)])
                elif v:
                    l.append("--{}".format(k))
            return l

        return type_func

    parser.add_argument(
        "-j",
        "--json_args",
        type=check_json_args_file(),
        help="Load arguments from json files. "
             "If a command line argument is also provide the json value will be ignore for this argument.",
    )

    # Register Command Handlers
    parser.set_defaults(func=main)
    gpu_info_parser.set_defaults(func=gpu_info.main)

    # Show usage is no args is provided
    if len(sys.argv) == 1:
        parser.print_usage()
        parser.exit()

    args = parser.parse_args()

    # Handle special cases for ignoring arguments in json file if provided in command line
    if args.json_args:
        l = args.json_args
        if "--cpu" in sys.argv[1:] or "--gpu" in sys.argv[1:]:
            l = list(filter(lambda a: a not in ("--cpu", "--gpu"), l))

        if "--auto-resize" in sys.argv[1:] or "--auto-resize-crop" in sys.argv[1:] \
                or "--auto-rescale" in sys.argv[1:] or "--overlay" in sys.argv[1:]:
            l = list(filter(lambda a: a not in ("--auto-resize",
                                                "--auto-resize-crop", "--auto-rescale", "--overlay"), l))

        args = parser.parse_args(l + sys.argv[1:])
    check_args(args)
    set_config_args(args)
    args.func(args)
