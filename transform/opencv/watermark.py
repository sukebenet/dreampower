import cv2
import numpy as np

from transform.opencv import ImageTransformOpenCV
from config import Config as conf


class ImageToWatermark(ImageTransformOpenCV):
    """
    Image -> Watermarked Image [OPENCV]
    """

    def __init__(self, input_index=(-1,), args=None, watermark="fake.png"):
        """
        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use conf.args)
        :param watermark: <string> path to the watermark image
        """
        super().__init__(args=args, input_index=input_index)
        self.__watermark = cv2.imread(watermark, cv2.IMREAD_UNCHANGED)

    def execute(self, img):
        """
        Create a watermark image
        :param img: <RGB> image to watermark
        :return: <RGB> watermarked image
        """
        # Add alpha channel if missing
        if img.shape[2] < 4:
            img = np.dstack([img, np.ones((512, 512), dtype="uint8") * 255])

        f1 = np.asarray([0, 0, 0, 250])  # red color filter
        f2 = np.asarray([255, 255, 255, 255])
        mask = cv2.bitwise_not(cv2.inRange(self.__watermark, f1, f2))
        mask_inv = cv2.bitwise_not(mask)

        res1 = cv2.bitwise_and(img, img, mask=mask)
        res2 = cv2.bitwise_and(self.__watermark, self.__watermark, mask=mask_inv)
        res = cv2.add(res1, res2)

        alpha = 0.6
        return cv2.addWeighted(res, alpha, img, 1 - alpha, 0)