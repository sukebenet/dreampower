"""OpenCV Resize Transforms."""
import cv2
import numpy as np

from config import Config as Conf
from transform.opencv import ImageTransformOpenCV
from transform.opencv.correct import DressToCorrect


class ImageToCrop(ImageTransformOpenCV):
    """Image -> Crop [OPENCV]."""

    def __init__(self, input_index=(-1,), args=None):
        """
        Image To Crop Constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(args=args, input_index=input_index)
        self.__x1 = self._args['overlay'][0]
        self.__y1 = self._args['overlay'][1]
        self.__x2 = self._args['overlay'][2]
        self.__y2 = self._args['overlay'][3]

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

    def __init__(self, input_index=(0, -1), args=None):
        """
        Image To Crop Overlay.

        :param input_index: <tuple> index where to take the inputs (default is (0,-1) for first
        and previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(input_index=input_index, args=args, )

    def _execute(self, *args):
        """
        Overlay an image by at the given coords with an another.

        :param args: <[RGB,RGB]] Image to overlay, the overlay
        :return: <RGB> image
        """
        # Remove white border add by resizing in case of the overlay selection was less than 512x512
        if abs(self.__x1 - self.__x2) < 512 or abs(self.__y1 - self.__y2) < 512:
            gray = cv2.cvtColor(args[1], cv2.COLOR_BGR2GRAY)
            gray = 255 * (gray < 128).astype(np.uint8)
            coords = cv2.findNonZero(gray)
            x, y, w, h = cv2.boundingRect(coords)
            img = args[1][y:y + h, x:x + w]

        img = cv2.resize(img, (abs(self.__x1 - self.__x2), abs(self.__y1 - self.__y2)))
        img_to_overlay = args[0][:, :, :3]
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
