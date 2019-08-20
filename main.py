import logging
import os
import sys
import time
from multiprocessing import freeze_support

import argv
from config import Config as conf
from utils import setup_log, read_image, check_shape

from processing.gif import SimpleGIFTransform
from processing.image import SimpleImageTransform, MultipleImageTransform, FolderImageTransform
from transform.gan.mask import CorrectToMask, MaskrefToMaskdet, MaskfinToNude
from transform.opencv.resize import ImageToCrop, ImageToOverlay, ImageToRescale, ImageToResized, ImageToResizedCrop
from transform.opencv.correct import DressToCorrect
from transform.opencv.mask import MaskToMaskref, MaskdetToMaskfin


def main(_):
    """
    Main logic entry point
    """
    conf.log = setup_log(logging.DEBUG) if conf.args['debug'] else setup_log()
    conf.log.debug("Args : {}".format(conf.args))
    conf.log.info("Welcome to DreamPower")

    if conf.args['gpu_ids']:
        conf.log.info("GAN Processing Will Use GPU IDs: {}".format(conf.args['gpu_ids']))
    else:
        conf.log.info("GAN Processing Will Use CPU")

    # Processing
    start = time.time()
    select_processing().run()
    conf.log.info("Done! We have taken {} seconds".format(round(time.time() - start, 2)))

    # Exit
    sys.exit()


def select_phases():
    """
    Select the transformation phases to use following args parameters
    :return: <ImageTransform[]> list of image transformation
    """

    def shift_step(shift_starting=0, shift_ending=0):
        if not conf.args['steps']:
            conf.args['steps'] = (0, 5)
        conf.args['steps'] = (
            conf.args['steps'][0] + shift_starting,
            conf.args['steps'][1] + shift_ending
        )

    def add_tail(phases, phase):
        phases = [phase] + phases
        if conf.args['steps'] and conf.args['steps'][0] != 0:
            shift_step(shift_starting=1)
        return phases

    def add_head(phases, phase):
        phases = phases + [phase]
        if conf.args['steps'] and conf.args['steps'][0] == len(phases) - 1:
            shift_step(shift_ending=1)
        return phases

    phases = [DressToCorrect(), CorrectToMask(), MaskToMaskref(),
              MaskrefToMaskdet(), MaskdetToMaskfin(), MaskfinToNude()]

    if conf.args['overlay']:
        phases = add_tail(phases, ImageToResized())
        phases = add_tail(phases, ImageToCrop())
        phases = add_head(phases, ImageToOverlay())
    elif conf.args['auto_resize']:
        phases = add_tail(phases, ImageToResized())
    elif conf.args['auto_resize_crop']:
        phases = add_tail(phases, ImageToResizedCrop())
    elif conf.args['auto_rescale']:
        phases = add_tail(phases, ImageToRescale())
    elif not conf.args['folder']:
        check_shape(read_image(conf.args['input']))
    return phases


def select_processing():
    """
    Select the processing to use following args parameters
    :return:
    """
    phases = select_phases()
    if conf.args['folder']:
      process = processing_image_folder(phases)
    elif conf.args['gif'] and conf.args['n_runs'] != 1:
        process = multiple_gif_processing(phases, conf.args['n_runs'])
    elif conf.args['gif']:
        process = simple_gif_processing(phases)
    elif conf.args['n_runs'] != 1:
        process = multiple_image_processing(phases, conf.args['n_runs'])
    else:
        process = simple_image_processing(phases)
    conf.log.debug("Process to execute : {}".format(process))
    return process


def simple_gif_processing(phases):
    """
    Define a simple gif process ready to run
    :param phases: <ImageTransform[]> list of image transformation
    :return: <SimpleGIFTransform> a gif process run ready
    """
    return SimpleGIFTransform(conf.args['input'], phases, conf.args['output'])


def multiple_gif_processing(phases, n):
    """
    Define a multiple gif process ready to run
    :param phases: <ImageTransform[]> list of image transformation
    :param n: number of times to process
    :return: <MultipleTransform> a multiple gif process run ready
    """
    filename, extension = os.path.splitext(conf.args['output'])
    return MultipleImageTransform(
        [conf.args['input'] for _ in range(n)],
        phases,
        ["{}{}{}".format(filename, i, extension) for i in range(n)],
        SimpleGIFTransform
    )


def simple_image_processing(phases):
    """
    Define a simple image process ready to run
    :param phases: <ImageTransform[]> list of image transformation
    :return: <SimpleImageTransform> a image process run ready
    """
    return SimpleImageTransform(conf.args['input'], phases, conf.args['output'])


def multiple_image_processing(phases, n):
    """
    Define a multiple image process ready to run
    :param phases: <ImageTransform[]> list of image transformation
    :param n: number of times to process
    :return: <MultipleTransform> a multiple image process run ready
    """
    filename, extension = os.path.splitext(conf.args['output'])
    return MultipleImageTransform(
        [conf.args['input'] for _ in range(n)],
        phases,
        ["{}{}{}".format(filename, i, extension) for i in range(n)]
    )

def processing_image_folder(phases):
    """
    Define a folder image process ready to run
    :param phases: <ImageTransform[]> list of image transformation
    :return: <SimpleImageTransform> a image process run ready
    """
    return FolderImageTransform(conf.args['input'], phases, conf.args['output'])

if __name__ == "__main__":
    freeze_support()
    # start_rook()
    argv.run()
