"""main logic."""
import os
import sys
import time
from multiprocessing import freeze_support

import colorama

import argv
from config import Config as Conf
from utils import check_shape
from processing import SimpleTransform, FolderImageTransform, MultipleImageTransform
from transform.gan.mask import CorrectToMask, MaskrefToMaskdet, MaskfinToNude
from transform.opencv.resize import ImageToCrop, ImageToOverlay, ImageToRescale, ImageToResized, ImageToResizedCrop
from transform.opencv.correct import DressToCorrect, ColorTransfer
from transform.opencv.mask import MaskToMaskref, MaskdetToMaskfin


def main(_):
    """Start main logic."""
    Conf.log.info("Welcome to DreamPower")

    if Conf.args['gpu_ids']:
        Conf.log.info("GAN Processing Will Use GPU IDs: {}".format(Conf.args['gpu_ids']))
    else:
        Conf.log.info("GAN Processing Will Use CPU")

    # Processing
    start = time.time()
    select_processing().run()
    Conf.log.info("Done! We have taken {} seconds".format(round(time.time() - start, 2)))

    # Exit
    sys.exit()


def select_phases():
    """
    Select the transformation phases to use following args parameters.

    :return: <ImageTransform[]> list of image transformation
    """
    def shift_step(shift_starting=0, shift_ending=0):
        if not Conf.args['steps']:
            Conf.args['steps'] = (0, 5)
        Conf.args['steps'] = (
            Conf.args['steps'][0] + shift_starting,
            Conf.args['steps'][1] + shift_ending
        )

    def add_tail(phases, phase):
        phases = [phase] + phases
        if Conf.args['steps'] and Conf.args['steps'][0] != 0:
            shift_step(shift_starting=1)
        if Conf.args['steps'] and Conf.args['steps'][1] == len(phases) - 1:
            shift_step(shift_ending=1)
        return phases

    def add_head(phases, phase):
        phases = phases + [phase]
        if Conf.args['steps'] and Conf.args['steps'][1] == len(phases) - 1:
            shift_step(shift_ending=1)
        return phases

    phases = [DressToCorrect, CorrectToMask, MaskToMaskref,
              MaskrefToMaskdet, MaskdetToMaskfin, MaskfinToNude]

    if Conf.args['overlay']:
        phases = add_tail(phases, ImageToResized)
        phases = add_tail(phases, ImageToCrop)
        phases = add_head(phases, ImageToOverlay)
    elif Conf.args['auto_resize']:
        phases = add_tail(phases, ImageToResized)
    elif Conf.args['auto_resize_crop']:
        phases = add_tail(phases, ImageToResizedCrop)
    elif Conf.args['auto_rescale']:
        phases = add_tail(phases, ImageToRescale)
    elif os.path.isfile(Conf.args['input']):
        if not Conf.args['ignore_size']:
            check_shape(Conf.args['input'])
        else:
            Conf.log.warn('Image Size Requirements Unchecked.')

    if Conf.args['color_transfer']:
        phases = add_head(phases, ColorTransfer)

    return phases


def select_processing():
    """
    Select the processing to use following args parameters.

    :return: <Process> a process to run
    """
    phases = select_phases()
    if os.path.isdir(Conf.args['input']):
        process = processing_image_folder(phases)
    elif Conf.args['n_runs'] != 1:
        process = multiple_image_processing(phases, Conf.args['n_runs'])
    else:
        process = simple_image_processing(phases)
    Conf.log.debug("Process to execute : {}".format(process))
    return process


def simple_image_processing(phases):
    """
    Define a simple image process ready to run.

    :param phases: <ImageTransform[]> list of image transformation
    :return: <SimpleTransform> a image process run ready
    """
    return SimpleTransform(Conf.args['input'], phases, Conf.args['output'])


def multiple_image_processing(phases, n_runs):
    """
    Define a multiple image process ready to run.

    :param phases: <ImageTransform[]> list of image transformation
    :param n_runs: number of times to process
    :return: <MultipleTransform> a multiple image process run ready
    """
    filename, extension = os.path.splitext(Conf.args['output'])
    return MultipleImageTransform(
        [Conf.args['input'] for _ in range(n_runs)],
        phases,
        ["{}{}{}".format(filename, i, extension) for i in range(n_runs)]
    )


def processing_image_folder(phases):
    """
    Define a folder image process ready to run.

    :param phases: <ImageTransform[]> list of image transformation
    :return: <FolderImageTransform> a image process run ready
    """
    return FolderImageTransform(Conf.args['input'], phases, Conf.args['output'])


if __name__ == "__main__":
    colorama.init()
    freeze_support()
    argv.run()
