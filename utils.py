import logging
import os
import sys
from re import finditer

import coloredlogs
import cv2
import numpy as np
import rook


def read_image(path):
    """
    Read a file image
    :param path: <string> Path of the image
    :return: <RGB> image
    """
    # Read image
    with open(path, "rb") as file:
        image_bytes = bytearray(file.read())
        np_image = np.asarray(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    # See if image loaded correctly
    if image is None:
        print("Error : {} file is not valid image".format(
            path), file=sys.stderr)
        sys.exit(1)
    return image


def write_image(image, path):
    """
    Write a file image to the path
    :param image: <RGB> image to write
    :param path: <string> location where write the image
    :return: <RGB> None
    """
    cv2.imwrite(path, image)


def check_shape(image, shape=(512, 512, 3)):
    """
    Valid the shape of an image
    :param image: <RGB> Image to check
    :param shape: <(int,int,int)> Valid hape
    :return: None
    """
    if image.shape != shape:
        print("Error : image is not 512 x 512, got shape: {}".format(
            image.shape), file=sys.stderr)
        sys.exit(1)



def start_rook():
    """
    Start rock
    :return: None
    """
    token = os.getenv("ROOKOUT_TOKEN")

    if token:
        rook.start(token=token)


def setup_log(log_lvl=logging.INFO):
    log = logging.getLogger(__name__)
    coloredlogs.install(level=log_lvl, fmt='[%(levelname)s] %(message)s')
    return log


def camel_case_to_str(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0) for m in matches])
