"""OpenCV Mask Transforms."""

import cv2
import numpy as np

from transform.opencv import ImageTransformOpenCV
from transform.opencv.bodypart.extract import extract_annotations
from transform.gan.generator import tensor2im


class MaskImageTransformOpenCV(ImageTransformOpenCV):
    """Mask Image Transform OpenCV."""

    def __init__(self, input_index=(-2, -1)):
        """
        Mask Image Transform OpenCV constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-2,-1)
        for the two previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(input_index=input_index)


class MaskToMaskref(MaskImageTransformOpenCV):
    """Mask & Correct -> MaskRef [OPENCV]."""

    def _execute(self, *args):
        """
        Create mask ref.

        :param args: <[RGB,RGB]>image correct, image mask
        :return: <RGB> image
        """
        # Create a total green image
        green = np.zeros(args[0].shape, np.uint8)
        green[:, :, :] = (0, 255, 0)  # (B, G, R)

        # Define the green color filter
        f1 = np.asarray([0, 250, 0])  # green color filter
        f2 = np.asarray([10, 255, 10])

        # From mask, extrapolate only the green mask
        green_mask = cv2.inRange(args[1], f1, f2)  # green is 0

        # (OPTIONAL) Apply dilate and open to mask
        kernel = np.ones((5, 5), np.uint8)  # Try change it?
        green_mask = cv2.dilate(green_mask, kernel, iterations=1)
        # green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)

        # Create an inverted mask
        green_mask_inv = cv2.bitwise_not(green_mask)

        # Cut correct and green image, using the green_mask & green_mask_inv
        res1 = cv2.bitwise_and(args[0], args[0], mask=green_mask_inv)
        res2 = cv2.bitwise_and(green, green, mask=green_mask)

        # Compone:
        return cv2.add(res1, res2)


class MaskdetToMaskfin(MaskImageTransformOpenCV):
    """Maskdet -> Maskfin [OPENCV]."""

    def __init__(self, input_index=(-2, -1)):
        """
        Maskdet To Maskfin constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-2,-1)
        for the two previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(input_index=input_index)

    def _setup(self, *args):
        self.__aur_size = self._args["prefs"]["aursize"]
        self.__nip_size = self._args["prefs"]["nipsize"]
        self.__tit_size = self._args["prefs"]["titsize"]
        self.__vag_size = self._args["prefs"]["vagsize"]
        self.__hair_size = self._args["prefs"]["hairsize"]

    def _execute(self, *args):
        """
        Create maskfin.

        steps:
            1. Extract annotation
                1.a: Filter by color
                1.b: Find ellipses
                1.c: Filter out ellipses by max size, and max total numbers
                1.d: Detect Problems
                1.e: Resolve the problems, or discard the transformation
            2. With the body list, draw maskfin, using maskref

        :param args: <[RGB, RGB]> maskref image, maskdet image
        :return: <RGB> image
        """
        def to_int(a, b):
            return int(round(a * float(b)))

        enable_pubes = (self.__hair_size > 0)

        # Create a total green image, in which draw details ellipses
        details = np.zeros(args[0].shape, np.uint8)
        details[:, :, :] = (0, 255, 0)  # (B, G, R)

        # Extract body part features:
        bodypart_list = extract_annotations(args[1], enable_pubes)

        # Check if the list is not empty:
        if bodypart_list:

            self.__draw_bodypart_details(bodypart_list, details, to_int)

            # Define the green color filter
            f1 = np.asarray([0, 250, 0])  # green color filter
            f2 = np.asarray([10, 255, 10])

            # From maskref, extrapolate only the green mask
            green_mask = cv2.bitwise_not(cv2.inRange(args[0], f1, f2))  # green is 0

            # Create an inverted mask
            green_mask_inv = cv2.bitwise_not(green_mask)

            # Cut maskref and detail image, using the green_mask & green_mask_inv
            res1 = cv2.bitwise_and(args[0], args[0], mask=green_mask)
            res2 = cv2.bitwise_and(details, details, mask=green_mask_inv)

            # Compone:
            maskfin = cv2.add(res1, res2)
            return maskfin

    def __draw_bodypart_details(self, bodypart_list, details, to_int):
        # Draw body part in details image:
        for obj in bodypart_list:

            if obj.w < obj.h:
                a_max = int(obj.h / 2)  # asse maggiore
                a_min = int(obj.w / 2)  # asse minore
                angle = 0  # angle
            else:
                a_max = int(obj.w / 2)
                a_min = int(obj.h / 2)
                angle = 90

            x = int(obj.x)
            y = int(obj.y)

            aurmax = to_int(self.__aur_size, a_max)
            aurmin = to_int(self.__aur_size, a_min)
            nipmax = to_int(self.__nip_size, a_max)
            nipmin = to_int(self.__nip_size, a_min)
            titmax = to_int(self.__tit_size, a_max)
            titmin = to_int(self.__tit_size, a_min)
            vagmax = to_int(self.__vag_size, a_max)
            vagmin = to_int(self.__vag_size, a_min)
            hairmax = to_int(self.__hair_size, a_max)
            hairmin = to_int(self.__hair_size, a_min)

            self.__draw_ellipse(a_max, a_min, angle, aurmax, aurmin, details, hairmax, hairmin, nipmax, nipmin, obj,
                                titmax, titmin, vagmax, vagmin, x, y)

    @staticmethod
    def __draw_ellipse(a_max, a_min, angle, aurmax, aurmin, details, hairmax, hairmin, nipmax, nipmin, obj,
                       titmax, titmin, vagmax, vagmin, x, y):
        # Draw ellipse
        if obj.name == "tit":
            cv2.ellipse(details, (x, y), (titmax, titmin), angle, 0, 360, (0, 205, 0), -1)  # (0,0,0,50)
        elif obj.name == "aur":
            cv2.ellipse(details, (x, y), (aurmax, aurmin), angle, 0, 360, (0, 0, 255), -1)  # red
        elif obj.name == "nip":
            cv2.ellipse(details, (x, y), (nipmax, nipmin), angle, 0, 360, (255, 255, 255), -1)  # white
        elif obj.name == "belly":
            cv2.ellipse(details, (x, y), (a_max, a_min), angle, 0, 360, (255, 0, 255), -1)  # purple
        elif obj.name == "vag":
            cv2.ellipse(details, (x, y), (vagmax, vagmin), angle, 0, 360, (255, 0, 0), -1)  # blue
        elif obj.name == "hair":
            xmin = x - hairmax
            ymin = y - hairmin
            xmax = x + hairmax
            ymax = y + hairmax
            cv2.rectangle(details, (xmin, ymin), (xmax, ymax), (100, 100, 100), -1)
