import cv2
import numpy as np

from config import Config as conf
from transform.opencv import ImageTransformOpenCV
from transform.opencv.correct import DressToCorrect


class ImageToCrop(ImageTransformOpenCV):
    """
    Image -> Crop [OPENCV]
    :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
    :param args: <dict> args parameter to run the image transformation (default use conf.args)
    """
    def __init__(self, input_index=(-1,), args=None):
        super().__init__(args=args, input_index=input_index)
        self.__x1 = self._args['overlay'][0]
        self.__y1 = self._args['overlay'][1]
        self.__x2 = self._args['overlay'][2]
        self.__y2 = self._args['overlay'][3]

    def execute(self, img):
        """
        Crop the image by the given coords
        :param img: <RGB> Image to crop
        :param x1: <int> x1 coord
        :param y1: <int> y1 coord
        :param x2: <int> x2 coord
        :param y2: <int> y2 coord
        :return: <RGB> image cropped
        """
        return img[self.__y1:self.__y2, self.__x1:self.__x2]


class ImageToOverlay(ImageTransformOpenCV):
    """
    Image -> Overlay [OPENCV]
    :param input_index: <tuple> index where to take the inputs (default is (0,1) for first and previous transformation)
    :param args: <dict> args parameter to run the image transformation (default use conf.args)
    """
    def __init__(self, input_index=(0, -1), args=None):
        super().__init__(input_index=input_index, args=args,)
        self.__x1 = self._args['overlay'][0]
        self.__y1 = self._args['overlay'][1]
        self.__x2 = self._args['overlay'][2]
        self.__y2 = self._args['overlay'][3]

    def execute(self, img_to_overlay, img):
        """
        Overlay an image by at the given coords with an another
        :param <RGB> img_to_overlay: Image to overlay
        :param <RGB> img: the overlay
        :return: <RGB> image
        """
        # Remove white border add by resizing in case of the overlay selection was less than 512x512
        if abs(self.__x1 - self.__x2) < 512 or abs(self.__y1 - self.__y2) < 512:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = 255 * (gray < 128).astype(np.uint8)
            coords = cv2.findNonZero(gray)
            x, y, w, h = cv2.boundingRect(coords)
            img = img[y:y + h, x:x + w]

        img = cv2.resize(img, (abs(self.__x1 - self.__x2), abs(self.__y1 - self.__y2)))
        img_to_overlay = img_to_overlay[:, :, :3]
        img = img[:, :, :3]
        img_to_overlay = DressToCorrect.correct_color(img_to_overlay, 5)
        img_to_overlay[self.__y1:self.__y2, self.__x1:self.__x2] = img[:, :, :3]
        return img_to_overlay


class ImageToResized(ImageTransformOpenCV):
    """
    Image -> Resized [OPENCV]
    """

    def execute(self, img):
        """
        Resize an image
        :param img: <RGB> image to resize
        :return: <RGB> image
        """
        old_size = img.shape[:2]
        ratio = float(conf.desired_size) / max(old_size)
        new_size = tuple([int(x * ratio) for x in old_size])

        img = cv2.resize(img, (new_size[1], new_size[0]))

        delta_w = conf.desired_size - new_size[1]
        delta_h = conf.desired_size - new_size[0]
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)

        return cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[255, 255, 255])


class ImageToResizedCrop(ImageTransformOpenCV):
    """
    Image -> Resized Crop [OPENCV]
    """

    def execute(self, img):
        """
        Resize and crop an image
        :param img: <RGB> image to resize and crop
        :return: <RGB> image
        """
        old_size = img.shape[:2]
        ratio = float(conf.desired_size) / min(old_size)
        new_size = tuple([int(x * ratio) for x in old_size])

        img = cv2.resize(img, (new_size[1], new_size[0]))

        delta_w = new_size[1] - conf.desired_size
        delta_h = new_size[0] - conf.desired_size
        top = delta_h // 2
        left = delta_w // 2

        return img[top:conf.desired_size + top, left:conf.desired_size + left]


class ImageToRescale(ImageTransformOpenCV):
    """
    Image -> Rescale [OPENCV]
    """

    def execute(self, img):
        """
        Rescale an image
        :param img: <RGB> image to rescale
        :return: <RGB> image
        """
        return cv2.resize(img, (conf.desired_size, conf.desired_size))