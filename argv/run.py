import json
import os
import re
from json import JSONDecodeError

import gpu_info
import main
from argv.checkpoints import check_arg_checkpoints, set_arg_checkpoints, arg_checkpoints
from argv.common import arg_debug, arg_help, arg_version
from utils import check_image_file_validity, cv2_supported_extension


def init_run_parser(subparsers):
    run_parser = subparsers.add_parser(
        'run',
        description="Process image(s) with dreampower.",
        help="Process image(s) with dreampower.",
        add_help=False
    )
    run_parser.set_defaults(func=main.main)

    # conflicts handler
    processing_mod = run_parser.add_mutually_exclusive_group()
    scale_mod = run_parser.add_mutually_exclusive_group()

    # add run arguments
    arg_input(run_parser)
    arg_output(run_parser)

    arg_auto_rescale(scale_mod)
    arg_auto_resize(scale_mod)
    arg_auto_resize_crop(scale_mod)
    arg_overlay(scale_mod)
    arg_ignore_size(scale_mod)

    arg_color_transfer(run_parser)

    arg_preferences(run_parser)
    arg_n_run(run_parser)
    arg_step(run_parser)
    arg_altered(run_parser)

    arg_cpu(processing_mod)
    arg_gpu(processing_mod)
    arg_checkpoints(run_parser)
    arg_n_core(run_parser)

    arg_json_args(run_parser)
    arg_json_folder_name(run_parser)

    arg_help(run_parser)
    arg_debug(run_parser)
    arg_version(run_parser)


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


def arg_altered(parser):
    parser.add_argument(
        "-a",
        "--altered",
        help="Path of the directory where steps images transformation are write."
    )


def arg_auto_rescale(parser):
    parser.add_argument(
        "--auto-rescale",
        action="store_true",
        help="Scale image to 512x512.",
    )


def arg_auto_resize(parser):
    parser.add_argument(
        "--auto-resize",
        action="store_true",
        help="Scale and pad image to 512x512 (maintains aspect ratio).",
    )


def arg_auto_resize_crop(parser):
    parser.add_argument(
        "--auto-resize-crop",
        action="store_true",
        help="Scale and crop image to 512x512 (maintains aspect ratio).",
    )


def arg_color_transfer(parser):
    parser.add_argument(
        "--color-transfer",
        action="store_true",
        help="Transfers the color distribution from the input image to the output image."
    )


def set_gpu_ids(args):
    if args.cpu:
        args.gpu_ids = None
    elif args.gpu:
        args.gpu_ids = args.gpu
    else:
        args.gpu_ids = None if not gpu_info.get_info()['has_cuda'] else [0]


def arg_cpu(parser):
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force photo processing with CPU (slower)",
    )


def arg_gpu(parser):
    parser.add_argument(
        "--gpu",
        action="append",
        type=int,
        help="ID of the GPU to use for processing. "
             "It can be used multiple times to specify multiple GPUs "
             "(Example: --gpu 0 --gpu 1 --gpu 2). Default : 0"
    )


def arg_ignore_size(parser):
    parser.add_argument(
        "--ignore-size",
        action="store_true",
        help="Ignore image size checks."
    )


def arg_input(parser):
    parser.add_argument(
        "-i",
        "--input",
        help="Path of the photo or directory to transform .",
    )


def check_arg_input(parser, args):
    if not args.input:
        parser.error("-i, --input INPUT is required.")
    if not os.path.isdir(args.input) and not os.path.isfile(args.input):
        parser.ArgumentTypeError("Input {} file or directory doesn't exist.".format(args.input))
    elif os.path.isfile(args.input) and os.path.splitext(args.input)[1] not in cv2_supported_extension() + [".gif"]:
        parser.ArgumentTypeError("Input {} file not supported format.".format(args.input))
    if os.path.isfile(args.input):
        check_image_file_validity(args.input)
    return args.input


def arg_json_args(parser):
    def check_json_args_file():
        def type_func(a):
            try:
                if os.path.isfile(a):
                    with open(a, 'r') as f:
                        j = json.load(f)
                else:
                    j = json.loads(str(a))
            except JSONDecodeError:
                raise parser.error(
                    "Arguments json {} is not in valid JSON format.".format(a))
            return j

        return type_func

    parser.add_argument(
        "-j",
        "--json-args",
        type=check_json_args_file(),
        help="Load arguments from json files or json string. "
             "If a command line argument is also provide the json value will be ignore for this argument.",
    )


def arg_json_folder_name(parser):
    parser.add_argument(
        "--json-folder-name",
        default="settings.json",
        help="Path to the json per folder configuration to looks for when processing folder. Default: settings.json"
    )


def arg_n_core(parser):
    parser.add_argument(
        "--n-cores",
        type=int,
        default=1,
        help="Number of cpu cores to use. Default : 1",
    )


def arg_n_run(parser):
    parser.add_argument(
        "-n",
        "--n-runs",
        type=int,
        default=1,
        help="Number of times to process input. Default : 1"
    )


def arg_output(parser):
    parser.add_argument(
        "-o",
        "--output",
        help="Path of the file or the directory where the transformed photo(s) "
             "will be saved. Default : output<input extension>"
    )


def check_arg_output(parser, args):
    if os.path.isfile(args.input) and not args.output:
        _, extension = os.path.splitext(args.input)
        args.output = "output{}".format(extension)
    elif args.output and os.path.isfile(args.input) and os.path.splitext(args.output)[1] \
            not in cv2_supported_extension() + [".gif"]:
        parser.error("Output {} file not a supported format.".format(args.output))


def arg_overlay(parser):
    def check_crops_coord():
        def type_func(a):
            if not re.match(r"^\d+,\d+:\d+,\d+$", a):
                raise parser.error("Incorrect coordinates format. "
                                   "Valid format is <x_top_left>,"
                                   "<y_top_left>:<x_bot_right>,<x_bot_right>.")
            return tuple(int(x) for x in re.findall(r'\d+', a))

        return type_func

    parser.add_argument(
        "--overlay",
        type=check_crops_coord(),
        help="Processing the part of the image given by the coordinates "
             "(<x_top_left>,<y_top_left>:<x_bot_right>,<x_bot_right>) and overlay the result on the original image."
    )


def set_arg_preference(args):
    args.prefs = {
        "titsize": args.bsize,
        "aursize": args.asize,
        "nipsize": args.nsize,
        "vagsize": args.vsize,
        "hairsize": args.hsize
    }


def arg_preferences(parser):
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


def arg_step(parser):
    def check_steps_args():
        def type_func(a):
            if not re.match(r"^[0-5]:[0-5]$", a):
                raise parser.error("Incorrect skip format. "
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
                raise parser.error("The ending step should be greater than starting the step.")

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
