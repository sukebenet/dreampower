"""OpenCV Correct Transforms."""
import math

import cv2
import numpy as np
from third.opencv.color_transfer import color_transfer

from transform.opencv import ImageTransformOpenCV


class DressToCorrect(ImageTransformOpenCV):
    """Dress -> Correct [OPENCV]."""

    def _execute(self, *args):
        """
        Execute dress to correct phase.

        :param args: <[RGB]> Image to correct
        :return: <RGB> image corrected
        """
        return self.correct_color(args[0], 5)

    @staticmethod
    def correct_color(img, percent):
        """
        Correct the color of an image.

        :param img: <RGB> Image to correct
        :param percent: <int> Percent of correction (1-100)
        :return <RGB>: image corrected
        """
        if img.shape[2] != 3:
            raise AssertionError()
        if not 0 < percent <= 100:
            raise AssertionError()

        half_percent = percent / 200.0

        channels = cv2.split(img)

        out_channels = []
        for channel in channels:
            if len(channel.shape) != 2:
                raise AssertionError()
            # find the low and high precentile values (based on the input percentile)
            height, width = channel.shape
            vec_size = width * height
            flat = channel.reshape(vec_size)

            if len(flat.shape) != 1:
                raise AssertionError()

            flat = np.sort(flat)

            n_cols = flat.shape[0]

            low_val = flat[math.floor(n_cols * half_percent)]
            high_val = flat[math.ceil(n_cols * (1.0 - half_percent))]

            # saturate below the low percentile and above the high percentile
            thresholded = DressToCorrect.apply_threshold(channel, low_val, high_val)
            # scale the channel
            normalized = cv2.normalize(thresholded, thresholded.copy(), 0, 255, cv2.NORM_MINMAX)
            out_channels.append(normalized)

        return cv2.merge(out_channels)

    @staticmethod
    def apply_threshold(matrix, low_value, high_value):
        """
        Apply a threshold on a matrix.

        :param matrix: <array> matrix
        :param low_value: <float> low value
        :param high_value: <float> high value
        :return: None
        """
        low_mask = matrix < low_value
        matrix = DressToCorrect.apply_mask(matrix, low_mask, low_value)

        high_mask = matrix > high_value
        matrix = DressToCorrect.apply_mask(matrix, high_mask, high_value)

        return matrix

    @staticmethod
    def apply_mask(matrix, mask, fill_value):
        """
        Apply a mask on a matrix.

        :param matrix: <array> matrix
        :param mask: <RGB> image mask
        :param fill_value: <> fill value
        :return: None
        """
        masked = np.ma.array(matrix, mask=mask, fill_value=fill_value)
        return masked.filled()


class ColorTransfer(ImageTransformOpenCV):
    """ColorTransfer [OPENCV]."""

    def __init__(self, input_index=(0, -1)):
        """
        Color Transfer constructor.

        :param input_index: <tuple> index where to take the inputs (default is (0,-1)
        for first and previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(input_index=input_index)

    def _execute(self, *args):
        """
        Transfers the color distribution from the source to the target.

        :param args: <[RGB,RGB]> Image source, Image target
        :return: <RGB> Color transfer image
        """
        return color_transfer(args[0], args[1], clip=True, preserve_paper=False)
