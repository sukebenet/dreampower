import cv2
import numpy as np

from transform.opencv import ImageTransformOpenCV


class ImageToWatermark(ImageTransformOpenCV):
    """
    Image -> Watermarked Image [OPENCV]
    """

    def __init__(self, watermark="fake.png"):
        super().__init__()
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