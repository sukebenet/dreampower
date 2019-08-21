import json
import logging
import os
import sys
from re import finditer

import coloredlogs
import cv2
import numpy as np
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
    Write a file image to the path (create the directory if needed)
    :param image: <RGB> image to write
    :param path: <string> location where write the image
    :return: None
    """
    dir = os.path.dirname(path)
    if dir != '':
        os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.splitext(path)[1] not in cv2_supported_extension():
        conf.log.error("{} invalid extension format.".format(path))
        sys.exit(1)

    cv2.imwrite(path, image)

    if not check_image_file_validity(path):
        conf.log.error(
            "Something gone wrong writing {} image file. The final result is not a valid image file.".format(path))
        sys.exit(1)


def check_shape(image, shape=(512, 512, 3)):
    """
    Valid the shape of an image
    :param image: <RGB> Image to check
    :param shape: <(int,int,int)> Valid shape
    :return: None
    """
    if image.shape != shape:
        conf.log.error("Image is not 512 x 512, got shape: {}".format(image.shape))
        conf.log.error("You should use one of the rescale options".format(image.shape))
        sys.exit(1)


def check_image_file_validity(image_path):
    """
    Check is a file is valid image file
    :param image_path: <string> Path to the file to check
    :return: <Boolean> True if it's an image file
    """
    try:
        im = Image.open(image_path)
        im.verify()
    except Exception:
        return False
    return True if os.stat(image_path).st_size != 0 else False


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


def cv2_supported_extension():
    """
    List of extension supported by cv2
    :return: <string[]> extensions list
    """
    return [".bmp", ".dib", ".jpeg", ".jpg", ".jpe", ".jp2", ".png",
            ".pbm", ".pgm", "ppm", ".sr", ".ras", ".tiff", ".tif"]


def json_to_argv(data):
    """
    Json to args parameters
    :param data: <json>
    :return: <Dict>
    """
    l = []
    for k, v in data.items():
        if not isinstance(v, bool):
            l.extend(["--{}".format(k), str(v)])
        elif v:
            l.append("--{}".format(k))
    return l