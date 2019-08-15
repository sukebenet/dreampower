import logging
import os
import sys
from re import finditer

import coloredlogs
import cv2
import numpy as np
import rook
from PIL import Image
from config import Config as conf


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
        conf.log.error("{} file is not valid image".format(path))
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
    if not check_image_file_validity(path):
        conf.log.error(
            "Something gone wrong writing {} image file. The final result is not a valid image file.".format(path))
        sys.exit(1)


def check_shape(image, shape=(512, 512, 3)):
    """
    Valid the shape of an image
    :param image: <RGB> Image to check
    :param shape: <(int,int,int)> Valid hape
    :return: None
    """
    if image.shape != shape:
        conf.log.error("Image is not 512 x 512, got shape: {}".format(image.shape))
        sys.exit(1)


def check_image_file_validity(image_path):
    """
    Check is a file is valid image file
    :param image_path: <string> Path to the file to check
    :return: <Boolean> True if it's an image file
    """
    im, r = None, True
    try:
        im = Image.open(image_path)
        im.verify()
    except Exception:
        r = False
    finally:
        if im:
            im.close()
    return r


def start_rook():
    """
    Start rock
    :return: None
    """
    token = os.getenv("ROOKOUT_TOKEN")

    if token:
        rook.start(token=token)


def setup_log(log_lvl=logging.INFO):
    """
    Setup a logger
    :param log_lvl: <loggin.LVL> level of the log
    :return: <Logger> a logger
    """
    log = logging.getLogger(__name__)
    coloredlogs.install(level=log_lvl, fmt='[%(levelname)s] %(message)s')
    return log


def camel_case_to_str(identifier):
    """
    Return the string representation of a Camel case word
    :param identifier: <string> camel case word
    :return: a string representation
    """
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0) for m in matches])
