"""main logic."""
import os
import sys
import time
from multiprocessing import freeze_support

import argv
from config import Config as Conf
from processing import SimpleProcessing
from processing.folder import FolderImageProcessing
from processing.multiple import MultipleImageProcessing

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
    Conf.log.success("Done! We have taken {} seconds".format(round(time.time() - start, 2)))

    # Exit
    sys.exit()


def select_processing():
    """
    Select the processing to use following args parameters.

    :return: <Process> a process to run
    """
    if Conf.args['image_size'] and Conf.args['image_size'] >= 256:
      Conf.set_image_size(Conf.args['image_size'])

    if os.path.isdir(Conf.args['input']):
        process = processing_image_folder()
    elif Conf.args['n_runs'] != 1:
        process = multiple_image_processing()
    else:
        process = simple_image_processing()
    Conf.log.debug("Process to execute : {}".format(process))
    return process


def simple_image_processing():
    """
    Define a simple image process ready to run.

    :param phases: <ImageTransform[]> list of image transformation
    :return: <SimpleTransform> a image process run ready
    """
    return SimpleProcessing()


def multiple_image_processing():
    """
    Define a multiple image process ready to run.

    :param n_runs: number of times to process
    :return: <MultipleTransform> a multiple image process run ready
    """
    filename, extension = os.path.splitext(Conf.args['output'])
    Conf.args['input'] = [Conf.args['input'] for _ in range(Conf.args['n_runs'])]
    Conf.args['output'] = ["{}{}{}".format(filename, i, extension) for i in range(Conf.args['n_runs'])]
    return MultipleImageProcessing()


def processing_image_folder():
    """
    Define a folder image process ready to run.

    :return: <FolderImageTransform> a image process run ready
    """
    return FolderImageProcessing()


if __name__ == "__main__":
    freeze_support()
    argv.run()
