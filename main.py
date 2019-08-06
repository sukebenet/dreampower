import json
import re
import shutil
import sys
import argparse
import tempfile
from json import JSONDecodeError

import cv2
import time
import os
import imageio

import sentry_sdk
import rook

import utils
import numpy as np

from run import process, process_gif
from multiprocessing import freeze_support
from multiprocessing.pool import ThreadPool
from dotenv import load_dotenv

import gpu_info

#
load_dotenv()

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser.add_argument(
    "-i", "--input", default="input.png", help="path of the photo to transform"
)
parser.add_argument(
    "-o",
    "--output",
    default="output.png",
    help="path where the transformed photo will be saved. (default: output.png or output.gif)",
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
    "-n", "--n_runs", type=int, help="number of times to process input (default: 1)",
)
parser.add_argument(
    "--n_cores", type=int, default=4, help="number of cpu cores to use (default: 4)",
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

"""
main.py

 How to run:
 python3 main.py

"""

# ------------------------------------------------- main()


def main(args):
    if not os.path.isfile(args.input):
        print("Error : {} file doesn't exist".format(
            args.input), file=sys.stderr)
        exit(1)
    start = time.time()

    gpu_ids = args.gpu

    prefs = {
        "titsize": args.bsize,
        "aursize": args.asize,
        "nipsize": args.nsize,
        "vagsize": args.vsize,
        "hairsize": args.hsize
    }

    if args.cpu:
        gpu_ids = None
    elif gpu_ids is None:
        gpu_ids = [0]

    if not args.gif:
        # Read image
        file = open(args.input, "rb")
        image_bytes = bytearray(file.read())
        np_image = np.asarray(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        # See if image loaded correctly
        if image is None:
            print("Error : {} file is not valid".format(
                args.input), file=sys.stderr)
            exit(1)

        # Preprocess
        if args.overlay:
            original_image = image.copy()
            image = utils.crop_input(
                image, args.overlay[0], args.overlay[1], args.overlay[2], args.overlay[3])
        elif args.auto_resize:
            image = utils.resize_input(image)
        elif args.auto_resize_crop:
            image = utils.resize_crop_input(image)
        elif args.auto_rescale:
            image = utils.rescale_input(image)

        # See if image has the correct shape after preprocessing
        if image.shape != (512, 512, 3):
            print("Error : image is not 512 x 512, got shape: {}".format(
                image.shape), file=sys.stderr)
            exit(1)

        # Process
        if args.n_runs is None or args.n_runs == 1:
            result = process(image, gpu_ids, prefs)

            if args.overlay:
                result = utils.overlay_original_img(original_image, result, args.overlay[0], args.overlay[1],
                                                    args.overlay[2], args.overlay[3])

            cv2.imwrite(args.output, result)
        else:
            base_output_filename = utils.strip_file_extension(
                args.output, ".png")

            def process_one_image(i):
                result = process(image, gpu_ids, args.enablepubes)

                if args.overlay:
                    result = utils.overlay_original_img(original_image, result, args.overlay[0], args.overlay[1],
                                                        args.overlay[2], args.overlay[3])
                cv2.imwrite(base_output_filename + "%03d.png" % i, result)

            if args.cpu:
                pool = ThreadPool(args.n_cores)
                pool.map(process_one_image, range(args.n_runs))
                pool.close()
                pool.join()
            else:
                for i in range(args.n_runs):
                    process_one_image(i)
    else:
        # Read images
        gif_imgs = imageio.mimread(args.input)
        print("Total {} frames in the gif!".format(len(gif_imgs)))

        # Preprocess
        if args.auto_resize:
            gif_imgs = [utils.resize_input(img) for img in gif_imgs]
        elif args.auto_resize_crop:
            gif_imgs = [utils.resize_crop_input(img) for img in gif_imgs]
        elif args.auto_rescale:
            gif_imgs = [utils.rescale_input(img) for img in gif_imgs]

        # Process
        if args.n_runs is None or args.n_runs == 1:
            process_gif_wrapper(gif_imgs, args.output if args.output != "output.png" else "output.gif", gpu_ids,
                                args.enablepubes, args.n_cores)
        else:
            base_output_filename = utils.strip_file_extension(args.output,
                                                              ".gif") if args.output != "output.png" else "output"
            for i in range(args.n_runs):
                process_gif_wrapper(gif_imgs, base_output_filename + "%03d.gif" % i, gpu_ids, args.enablepubes,
                                    args.n_cores)

    end = time.time()
    duration = end - start

    # Done
    print("Done! We have taken", round(duration, 2), "seconds")

    # Exit
    sys.exit()


# Register Command Handlers
parser.set_defaults(func=main)
gpu_info_parser.set_defaults(func=gpu_info.main)

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


def process_gif_wrapper(gif_imgs, filename, gpu_ids, enablepubes, n_cores):
    tmp_dir = tempfile.mkdtemp()
    process_gif(gif_imgs, gpu_ids, enablepubes, tmp_dir, n_cores)
    print("Creating gif")
    imageio.mimsave(
        filename,
        [
            imageio.imread(os.path.join(tmp_dir, "output_{}.jpg".format(i)))
            for i in range(len(gif_imgs))
        ],
    )
    shutil.rmtree(tmp_dir)


def start_sentry():
    dsn = os.getenv("SENTRY_DSN")

    if dsn:
        sentry_sdk.init(dsn=dsn)


def start_rook():
    token = os.getenv("ROOKOUT_TOKEN")

    if token:
        rook.start(token=token)


if __name__ == "__main__":
    freeze_support()
    start_sentry()
    start_rook()
    args.func(args)
