"""GAN Mask Transforms."""
from transform.gan import ImageTransformGAN
from transform.opencv.bodypart.extract import find_color
from config import Config as Conf

import cv2
import numpy as np


class MaskImageTransformGAN(ImageTransformGAN):
    def __init__(self, mask_name, input_index=(-1,)):
        """
        Correct To Mask constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(
            Conf.args['checkpoints'][mask_name],
            mask_name,
            input_index=input_index,
        )


class CorrectToMask(MaskImageTransformGAN):
    """Correct -> Mask [GAN]."""

    def __init__(self, input_index=(-1,)):
        """
        Correct To Mask constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__("correct_to_mask", input_index=input_index)


class MaskrefToMaskdet(MaskImageTransformGAN):
    """Maskref -> Maskdet [GAN]."""

    def __init__(self, input_index=(-1,)):
        """
        Maskref To Maskdet constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__("maskref_to_maskdet", input_index=input_index)


class MaskfinToNude(MaskImageTransformGAN):
    """Maskfin -> Nude [GAN]."""

    def __init__(self, input_index=(-1,)):
        """
        Maskfin To Nude constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__("maskfin_to_nude", input_index=input_index)

    def _execute(self, *args):
      mask = super()._execute(*args)

      if self._args["experimental_artifacts_inpaint"]:
        mask = self._inpaint(args[0], mask)

      return mask

    def _get_color_mask(self, vagina, lower, upper):
      mask_bounds = find_color(vagina, lower, upper)

      if not mask_bounds:
        return False

      # Create a black image and fill the detected areas with white.
      mask = np.zeros(vagina.shape, np.uint8)
      mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
      mask = cv2.drawContours(mask, mask_bounds[9], -1, (255, 255, 255), 6)

      return mask

    def _get_vagina_artifacts_mask(self, maskfin, nude):
      bounds = find_color(maskfin, np.asarray([250, 0, 0]), np.asarray([255, 0, 0]))

      if not bounds:
        Conf.log.info("Vagina not detected.")
        return False

      # TODO: Verify that this works on all photos.
      bounds[0] = bounds[0] - 15 # top
      bounds[2] = bounds[2] - 5 # left
      #bounds[1] = bounds[1] + 5 # bottom
      bounds[3] = bounds[3] + 15 # right

      # Image only with the vagina zone.
      vagina = nude[bounds[0]:bounds[1], bounds[2]:bounds[3]]

      # Black image with the size of the fake nude
      inpaint_mask = np.zeros(nude.shape, np.uint8)
      inpaint_mask = cv2.cvtColor(inpaint_mask, cv2.COLOR_BGR2GRAY)

      # Black image with the size of the vagina.
      vagina_mask = np.zeros(vagina.shape, np.uint8)
      vagina_mask = cv2.cvtColor(vagina_mask, cv2.COLOR_BGR2GRAY)

      # Mask with the areas that have visual artifacts.
      vagina_mask = self._get_color_mask(vagina, np.asarray([0, 50, 0]), np.asarray([100, 255, 100]))

      if isinstance(vagina_mask, bool): # oh lord
        Conf.log.info("No visual artifacts detected.")
        return False

      #
      inpaint_mask[bounds[0]:bounds[1], bounds[2]:bounds[3]] = vagina_mask[:, :]

      return inpaint_mask


    def _inpaint(self, maskfin, nude):
      """
      We try to fix visual artifacts that are generated in the vagina.
      """
      Conf.log.info("Fixing vagina visual artifacts...")

      bad_mask = self._get_vagina_artifacts_mask(maskfin, nude)

      if not isinstance(bad_mask, bool): # oh lord x2
        nude = cv2.inpaint(nude, bad_mask, 3, cv2.INPAINT_TELEA)

      return nude
