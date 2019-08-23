import argparse
import copy
import json
import os
import re
import sys
from json import JSONDecodeError

import checkpoints
import gpu_info
from main import main
from config import Config as conf
from utils import cv2_supported_extension, json_to_argv, check_image_file_validity


class ArgvParser:
    parser = argparse.ArgumentParser(
        description="Dreampower CLI application that allow to transform photos of people for private entertainment",
        add_help=False
    )

    @staticmethod
    def config_args(args, json_data=None):
        """
        Config, do check for a Namespace and give this dict representation of args
        :param json_path: <string> a json config file to use to update args
        :param args: <Namespace> args Namespace
        :return: <dict> dict representation of args
        """

        def config_checkpoints(a):
            checkpoints_dir = a.checkpoints
            a.checkpoints = {
                'correct_to_mask': os.path.join(str(a.checkpoints), "cm.lib"),
                'maskref_to_maskdet': os.path.join(str(a.checkpoints), "mm.lib"),
                'maskfin_to_nude': os.path.join(str(a.checkpoints), "mn.lib"),
            }
            for _, v in a.checkpoints.items():
                if not os.path.isfile(v):
                    ArgvParser.parser.error(
                        "Checkpoints file not found in directory {}. "
                        "You can download them using : {} checkpoints download".format(checkpoints_dir, sys.argv[0])
                    )

        def config_body_parts_prefs(a):
            a.prefs = {
                "titsize": a.bsize,
                "aursize": a.asize,
                "nipsize": a.nsize,
                "vagsize": a.vsize,
                "hairsize": a.hsize
            }

        def config_gpu_ids(a):
            if a.cpu:
                a.gpu_ids = None
            elif a.gpu:
                a.gpu_ids = a.gpu
            else:
                a.gpu_ids = None if not gpu_info.get_info()['has_cuda'] else [0]

        def config_args_in(a):
            if not a.input:
                ArgvParser.parser.error("-i, --input INPUT is required.")
            elif not os.path.isdir(a.input) and not os.path.isfile(a.input):
                ArgvParser.parser.error("Input {} file or directory doesn't exist.".format(a.input))
            elif os.path.isfile(a.input) and os.path.splitext(a.input)[1] \
                    not in cv2_supported_extension() + [".gif"]:
                ArgvParser.parser.error("Input {} file not supported format.".format(a.input))
            if os.path.isfile(a.input):
                check_image_file_validity(a.input)

        def config_args_out(a):
            if os.path.isfile(a.input) and not a.output:
                _, extension = os.path.splitext(a.input)
                a.output = "output{}".format(extension)
            elif a.output and os.path.isfile(a.input) and os.path.splitext(a.output)[1] \
                    not in cv2_supported_extension() + [".gif"]:
                ArgvParser.parser.error("Output {} file not a supported format.".format(a.output))

        def config_args_altered(a):
            if a.steps and not a.altered:
                ArgvParser.parser.error("--steps requires --altered.")
            elif a.steps and a.altered:
                if not os.path.isdir(a.altered):
                    ArgvParser.parser.error("{} directory doesn't exist.".format(a.altered))

        def config_all(a):
            config_checkpoints(a)
            config_gpu_ids(a)
            config_body_parts_prefs(a)
            config_args_in(a)
            config_args_out(a)
            config_args_altered(a)
            return a

        def merge_args_json_in_dict(a, json_data=None):
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

            cmdline_args = []
            if not json_data and not a.json_args:
                return vars(a)
            elif json_data and a.json_args:
                cmdline_args = filter_conflict_args(json_to_argv(json_data), json_to_argv(a.json_args))
            elif json_data and not a.json_args:
                cmdline_args = json_to_argv(json_data)
            elif not json_data and a.json_args:
                cmdline_args = json_to_argv(a.json_args)

            cmdline_args = filter_conflict_args(cmdline_args, sys.argv[1:])

            i = 0
            while i < len(cmdline_args):
                if "--json-args" == cmdline_args[i]:
                    del cmdline_args[i:i + 1]
                i += 1

            return vars(config_all(ArgvParser.parser.parse_args(cmdline_args)))

        args = copy.deepcopy(args)
        if args.func == main:
            config_all(args)
            return merge_args_json_in_dict(args, json_data)
        return vars(args)

    @staticmethod
    def run():
        """
        Run argparse for Dreampower
        :return: None
        """
        ArgvParser.parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                                       help='Show this help message and exit.')
        subparsers = ArgvParser.parser.add_subparsers()
        ArgvParser.parser.add_argument(
            "-d", "--debug", action="store_true", help="Enable log debug mod."
        )
        ArgvParser.parser.add_argument(
            "-i", "--input", help="Path of the photo or directory to transform ."
        )
        ArgvParser.parser.add_argument(
            "-o", "--output",
            help="Path of the file or the directory where the transformed photo(s)"
                 "will be saved. Default : output<input extension>",
        )
        processing_mod = ArgvParser.parser.add_mutually_exclusive_group()
        processing_mod.add_argument(
            "--cpu",
            default=False,
            action="store_true",
            help="Force photo processing with CPU (slower)",
        )
        processing_mod.add_argument(
            "--gpu",
            action="append",
            type=int,
            help="ID of the GPU to use for processing. "
                 "It can be used multiple times to specify multiple GPUs "
                 "(Example: --gpu 0 --gpu 1 --gpu 2). Default : 0"
        )
        ArgvParser.parser.add_argument(
            "--bsize",
            type=float,
            default=1,
            help="Boob size scalar best results 0.3 - 2.0",
        )
        ArgvParser.parser.add_argument(
            "--asize",
            type=float,
            default=1,
            help="Areola size scalar best results 0.3 - 2.0",
        )
        ArgvParser.parser.add_argument(
            "--nsize",
            type=float,
            default=1,
            help="Nipple size scalar best results 0.3 - 2.0",
        )
        ArgvParser.parser.add_argument(
            "--vsize",
            type=float,
            default=1,
            help="Vagina size scalar best results 0.3 - 1.5",
        )
        ArgvParser.parser.add_argument(
            "--hsize",
            type=float,
            default=0,
            help="Pubic hair size scalar best results set to 0 to disable",
        )
        ArgvParser.parser.add_argument(
            "-n", "--n-runs", type=int, default=1, help="Number of times to process input. Default : 1",
        )
        ArgvParser.parser.add_argument(
            "--n-cores", type=int, default=1, help="Number of cpu cores to use. Default : 1",
        )

        scale_mod = ArgvParser.parser.add_mutually_exclusive_group()
        scale_mod.add_argument(
            "--auto-resize",
            action="store_true",
            default=False,
            help="Scale and pad image to 512x512 (maintains aspect ratio).",
        )
        scale_mod.add_argument(
            "--auto-resize-crop",
            action="store_true",
            default=False,
            help="Scale and crop image to 512x512 (maintains aspect ratio).",
        )
        scale_mod.add_argument(
            "--auto-rescale",
            action="store_true",
            default=False,
            help="Scale image to 512x512.",
        )

        def check_crops_coord():
            def type_func(a):
                if not re.match(r"^\d+,\d+:\d+,\d+$", a):
                    raise argparse.ArgumentTypeError("Incorrect coordinates format. "
                                                     "Valid format is <x_top_left>,"
                                                     "<y_top_left>:<x_bot_right>,<x_bot_right>.")
                return tuple(int(x) for x in re.findall(r'\d+', a))

            return type_func

        scale_mod.add_argument(
            "--overlay",
            type=check_crops_coord(),
            help="Processing the part of the image given by the coordinates "
                 "(<x_top_left>,<y_top_left>:<x_bot_right>,<x_bot_right>) and overlay the result on the original image."
        )

        scale_mod.add_argument(
            "--ignore-size",
            action="store_true",
            help="Ignore image size checks."
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

        ArgvParser.parser.add_argument(
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

        ArgvParser.parser.add_argument(
            "-a",
            "--altered",
            help="Path of the directory where steps images transformation are write."
        )

        ArgvParser.parser.add_argument(
            "-c",
            "--checkpoints",
            default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "checkpoints"),
            help="Path of the directory containing the checkpoints. Default : ./checkpoints"
        )

        def check_json_args_file():
            def type_func(a):
                try:
                    if os.path.isfile(a):
                        with open(a, 'r') as f:
                            j = json.load(f)
                    else:
                        j = json.loads(str(a))
                except JSONDecodeError:
                    raise argparse.ArgumentTypeError(
                        "Arguments json {} is not in valid JSON format.".format(a))
                return j

            return type_func

        ArgvParser.parser.add_argument(
            "-j",
            "--json-args",
            type=check_json_args_file(),
            help="Load arguments from json files or json string. "
                 "If a command line argument is also provide the json value will be ignore for this argument.",
        )
        ArgvParser.parser.add_argument(
            "--json-folder-name",
            default="settings.json",
            help="Path to the json per folder configuration to looks for when processing folder. Default: settings.json"
        )

        ArgvParser.parser.add_argument(
            "-v",
            "--version",
            action='version', version='%(prog)s {}'.format(conf.version)
        )

        gpu_info_parser = subparsers.add_parser('gpu-info')
        gpu_info_subparser = gpu_info_parser.add_subparsers()
        gpu_info_json_parser = gpu_info_subparser.add_parser('json')

        checkpoints_parser = subparsers.add_parser('checkpoints')
        checkpoints_parser_subparser = checkpoints_parser.add_subparsers()
        checkpoints_parser_info_parser = checkpoints_parser_subparser.add_parser('download')

        checkpoints_parser.add_argument(
            "-v",
            "--version",
            action='version', version='checkpoints {}'.format(conf.checkpoints_version)
        )

        # Register Command Handlers
        ArgvParser.parser.set_defaults(func=main)
        gpu_info_parser.set_defaults(func=gpu_info.main)
        gpu_info_json_parser.set_defaults(func=gpu_info.json)
        checkpoints_parser.set_defaults(func=checkpoints.main)
        checkpoints_parser_info_parser.set_defaults(func=checkpoints.download)

        # Show usage is no args is provided
        if len(sys.argv) == 1:
            ArgvParser.parser.print_usage()
            ArgvParser.parser.exit()

        args = ArgvParser.parser.parse_args()
        conf.args = ArgvParser.config_args(args)
        args.func(args)
