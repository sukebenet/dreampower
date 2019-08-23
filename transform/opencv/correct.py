import cv2
import math
import numpy as np

from third.opencv.color_transfer import color_transfer
from transform.opencv import ImageTransformOpenCV


class DressToCorrect(ImageTransformOpenCV):
    """
    Dress -> Correct [OPENCV]
    """

    def execute(self, img):
        """
        Execute dress to correct phase
        :param img: <RGB> Image to correct
        :return: <RGB> image corrected
        """
        return self.correct_color(img, 5)

    @staticmethod
    def correct_color(img, percent):
        """
        Correct the color of an image
        :param img: <RGB> Image to correct
        :param percent: <int> Percent of correction (1-100)
        :return <RGB>: image corrected
        """
        assert img.shape[2] == 3
        assert 0 < percent < 100

        half_percent = percent / 200.0

        channels = cv2.split(img)

        out_channels = []
        for channel in channels:
            assert len(channel.shape) == 2
            # find the low and high precentile values (based on the input percentile)
            height, width = channel.shape
            vec_size = width * height
            flat = channel.reshape(vec_size)

            assert len(flat.shape) == 1

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
        Apply a threshold on a matrix
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
        Apply a mask on a matrix
        :param matrix: <array> matrix
        :param mask: <RGB> image mask
        :param fill_value: <> fill value
        :return: None
        """
        masked = np.ma.array(matrix, mask=mask, fill_value=fill_value)
        return masked.filled()


class ColorTransfer(ImageTransformOpenCV):
    """
    ColorTransfer [OPENCV]
    """
    def __init__(self, input_index=(0, -1), args=None):
        super().__init__(input_index=input_index, args=args)

    def execute(self, img, img_target):
        """
        Transfers the color distribution from the source to the target
        :param img: <RGB> Image source
        :param img_target: <RGB> Image target
        :return: <RGB> Color transfer image
        """
        return color_transfer(img, img_target, clip=True, preserve_paper=False)
