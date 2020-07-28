"""OpenCV Resize Transforms."""
import cv2
import numpy as np
import tempfile
from PIL import Image

from config import closest_number, Config as Conf
from transform.opencv import ImageTransformOpenCV
from transform.opencv.correct import DressToCorrect


class ImageToCrop(ImageTransformOpenCV):
    """Image -> Crop [OPENCV]."""

    def __init__(self, input_index=(-1,)):
        """
        Image To Crop Constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(input_index=input_index)
        self.__x1 = Conf.args['overlay'][0]
        self.__y1 = Conf.args['overlay'][1]
        self.__x2 = Conf.args['overlay'][2]
        self.__y2 = Conf.args['overlay'][3]

    def _execute(self, *args):
        """
        Crop the image by the given coords.

        :param args: <[RGB]> Image to crop
        :param x1: <int> x1 coord
        :param y1: <int> y1 coord
        :param x2: <int> x2 coord
        :param y2: <int> y2 coord
        :return: <RGB> image cropped
        """
        return args[0][self.__y1:self.__y2, self.__x1:self.__x2]


class ImageToOverlay(ImageToCrop):
    """Image -> Overlay [OPENCV]."""

    def __init__(self, input_index=(0, -1)):
        """
        Image To Crop Overlay.

        :param input_index: <tuple> index where to take the inputs (default is (0,-1) for first
        and previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(input_index=input_index)
        self.__x1 = Conf.args['overlay'][0]
        self.__y1 = Conf.args['overlay'][1]
        self.__x2 = Conf.args['overlay'][2]
        self.__y2 = Conf.args['overlay'][3]

    def _execute(self, *args):
        """
        Overlay an image by at the given coords with an another.

        :param args: <[RGB,RGB]] Image to overlay, the overlay
        :return: <RGB> image
        """
        img = args[1]
        img = cv2.resize(img, (abs(self.__x1 - self.__x2), abs(self.__y1 - self.__y2)))
        img = img[:, :, :3]
        img_to_overlay = DressToCorrect.correct_color(args[0], 5)
        img_to_overlay[self.__y1:self.__y2, self.__x1:self.__x2] = img[:, :, :3]
        return img_to_overlay


class ImageToResized(ImageTransformOpenCV):
    """Image -> Resized [OPENCV]."""

    def _execute(self, *args):
        new_size = self._calculate_new_size(args[0])
        img = cv2.resize(args[0], (new_size[1], new_size[0]))
        return self._make_new_image(img, new_size)

    @staticmethod
    def _calculate_new_size(img):
        old_size = img.shape[:2]
        ratio = float(Conf.desired_size) / max(old_size)
        new_size = tuple([int(x * ratio) for x in old_size])

        return new_size

    @staticmethod
    def _make_new_image(img, new_size):
        delta_w = Conf.desired_size - new_size[1]
        delta_h = Conf.desired_size - new_size[0]
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)

        return cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[255, 255, 255])


class ImageToResizedCrop(ImageToResized):
    """Image -> Resized Crop [OPENCV]."""

    @staticmethod
    def _calculate_new_size(img):
        if (img.shape[1] > img.shape[0]):
            ratio = float(img.shape[1] / img.shape[0])
            new_height = Conf.desired_size
            new_width = int(new_height * ratio)
        elif (img.shape[1] < img.shape[0]):
            ratio = float(img.shape[0] / img.shape[1])
            new_width = Conf.desired_size
            new_height = int(new_width * ratio)
        else:
            new_width = Conf.desired_size
            new_height = Conf.desired_size

        new_size = (new_height, new_width)

        return new_size

    @staticmethod
    def _make_new_image(img, new_size):
        delta_w = new_size[1] - Conf.desired_size
        delta_h = new_size[0] - Conf.desired_size
        top = delta_h // 2
        left = delta_w // 2

        return img[top:Conf.desired_size + top, left:Conf.desired_size + left]


class ImageToRescale(ImageTransformOpenCV):
    """Image -> Rescale [OPENCV]."""

    def _execute(self, *args):
        """
        Rescale an image.

        :param args: <[RGB]> image to rescale
        :return: <RGB> image
        """
        return cv2.resize(args[0], (Conf.desired_size, Conf.desired_size))

class ImageToNearest(ImageTransformOpenCV):
    """Image -> Rescale [OPENCV]."""

    def _execute(self, *args):
        """
        Rescale an image.

        :param args: <[RGB]> image to rescale
        :return: <RGB> image
        """
        height, width = args[0].shape[:2]

        new_width = closest_number(width)
        new_height = closest_number(height)

        Conf.log.info("Image resize to Nearest: {}x{} -> {}x{}".format(width, height, new_width, new_height))

        return cv2.resize(args[0], (new_width, new_height))

class ImageCompress(ImageTransformOpenCV):
    """Image -> Rescale [OPENCV]."""

    def _execute(self, *args):
        """
        Rescale an image.

        :param args: <[RGB]> image to rescale
        :return: <RGB> image
        """
        temp_path = tempfile.mktemp(".jpg")

        quality = int(self._args["compress"])
        quality = abs(quality - 100)

        if quality <= 0:
          quality = 1

        Conf.log.info("Compressing Image with level {} (Quality: {})".format(self._args["compress"], quality))

        cv2.imwrite(temp_path, args[0], [cv2.IMWRITE_JPEG_QUALITY, quality])

        return cv2.imread(temp_path)
