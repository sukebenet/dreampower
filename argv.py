import argparse
import json
import os
import re
import sys
from json import JSONDecodeError

import gpu_info
from main import main
from config import Config as conf
from gpu_info import get_info
from utils import cv2_supported_extension


def config_args(parser, args):
    def config_checkpoints():
        checkpoints = {
            'correct_to_mask': os.path.join(args.checkpoints, "cm.lib"),
            'maskref_to_maskdet': os.path.join(args.checkpoints, "mm.lib"),
            'maskfin_to_nude': os.path.join(args.checkpoints, "mn.lib"),
        }
        for _, v in checkpoints.items():
            if not os.path.isfile(v):
                parser.error("Checkpoints file not found in directory {}".format(args.checkpoints))
        return checkpoints

    def config_body_parts_prefs():
        prefs = {
            "titsize": args.bsize,
            "aursize": args.asize,
            "nipsize": args.nsize,
            "vagsize": args.vsize,
            "hairsize": args.hsize
        }
        return prefs

    def config_gpu_ids():
        if args.cpu:
            gpu_ids = None
        elif args.gpu:
            gpu_ids = args.gpu
        else:
            gpu_ids = None if not gpu_info.get_info()['has_cuda'] else [0]
        return gpu_ids

    def config_args_in():
        if not args.input:
            parser.error("-i, --input INPUT is required.")
        elif not args.folder and not os.path.isfile(args.input):
            parser.error("Input {} file doesn't exist.".format(args.input))
        elif args.folder and not os.path.isdir(args.input):
            parser.error("Input {} directory doesn't exist.".format(args.input))
        elif not args.folder and os.path.splitext(args.input)[1] not in cv2_supported_extension() + [".gif"]:
            parser.error("Input {} file not supported format.".format(args.input))

    def config_args_out():
        if not args.folder and not args.output:
            _, extension = os.path.splitext(args.input)
            args.output = "output{}".format(extension)
        elif args.output and not args.folder and os.path.splitext(args.output)[1] not in cv2_supported_extension():
            parser.error("Output {} file not a supported format.".format(args.output))

    def config_args_altered():
        if args.steps and not args.altered:
            parser.error("--steps requires --altered.")
        elif args.steps and args.altered:
            if not os.path.isdir(args.altered):
                parser.error("{} directory doesn't exist.".format(args.input))

    if args.func == main:
        conf.args = vars(args)
        conf.args['checkpoints'] = config_checkpoints()
        conf.args['gpu_ids'] = config_gpu_ids()
        conf.args['prefs'] = config_body_parts_prefs()
        config_args_in()
        config_args_out()
        config_args_altered()


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
        "-i", "--input", help="path of the photo to transform"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="path where the transformed photo will be saved. (default: output.<input extension>)",
    )
    parser.add_argument(
        "-f",
        "--folder",
        action="store_true",
        help="Folder mode processing. "
             ""  # TODO Json config by dir
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

    def check_crops_coord():
        def type_func(a):
            if not re.match(r"^\d+,\d+:\d+,\d+$", a):
                raise argparse.ArgumentTypeError("Incorrect coordinates format. "
                                                 "Valid format is <x_top_left>,<y_top_left>:<x_bot_right>,<x_bot_right>")
            return tuple(int(x) for x in re.findall(r'\d+', a))

        return type_func

    scale_mod.add_argument(
        "--overlay",
        type=check_crops_coord(),
        help="Processing the part of the image given by the coordinates "
             "(<x_top_left>,<y_top_left>:<x_bot_right>,<x_bot_right>) and overlay the result on the original image.",
    )

    def check_steps_args():
        def type_func(a):
            if not re.match(r"^[0-5]:[0-5]$", a):
                raise argparse.ArgumentTypeError("Incorrect skip format. "
                                                 "Valid format is <starting step>:<ending step>.\n"
                                                 "Steps are : \n"
                                                 "0 : dress -> correct [OPENCV]\n"
                                                 "1 : correct -> mask [GAN]\n"
                                                 "2 : mask -> maskref [OPENCV]\n"
                                                 "3 : maskref -> maskdet [GAN]\n"
                                                 "4 : maskdet -> maskfin [OPENCV]\n"
                                                 "5 : maskfin -> nude [GAN]"
                                                 )

            steps = tuple(int(x) for x in re.findall(r'\d+', a))

            if steps[0] > steps[1]:
                raise argparse.ArgumentTypeError("The ending step should be greater than starting the step.")

            return steps[0], steps[1] + 1

        return type_func

    parser.add_argument(
        "-s",
        "--steps",
        type=check_steps_args(),
        help="Select a range of steps to execute <starting step>:<ending step>."
             "Steps are : \n"
             "0 : dress -> correct [OPENCV]\n"
             "1 : correct -> mask [GAN]\n"
             "2 : mask -> maskref [OPENCV]\n"
             "3 : maskref -> maskdet [GAN]\n"
             "4 : maskdet -> maskfin [OPENCV]\n"
             "5 : maskfin -> nude [GAN]"
    )

    parser.add_argument(
        "-a",
        "--altered",
        help="path of the directory where steps images transformation are write."
    )

    parser.add_argument(
        "-c",
        "--checkpoints",
        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "checkpoints"),
        help="path of the directory containing the checkpoints."
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

    gpu_info_parser = subparsers.add_parser('gpu-info')
    gpu_info_parser.add_argument(
        "-j",
        "--json",
        default=False,
        action="store_true",
        help="Print GPU info as JSON"
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

    config_args(parser, args)
    args.func(args)
