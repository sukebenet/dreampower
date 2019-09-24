"""GAN Mask Transforms."""
from transform.gan import ImageTransformGAN
from config import Config as Conf


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
