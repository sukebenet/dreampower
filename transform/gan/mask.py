from transform.gan import ImageTransformGAN
from config import Config as conf


class CorrectToMask(ImageTransformGAN):
    """
    Correct -> Mask [GAN]
    """

    def __init__(self, input_index=(-1,), args=None):
        """
        CorrectToMask Constructor
        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use conf.args)
        """
        super().__init__(
            (args if args is not None else conf.args)['checkpoints']["correct_to_mask"],
            "correct_to_mask",
            input_index=input_index,
            args=args
        )


class MaskrefToMaskdet(ImageTransformGAN):
    """
    Maskref -> Maskdet [GAN]
    """

    def __init__(self, input_index=(-1,), args=None):
        """
        MaskrefToMaskdet Constructor
        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use conf.args)
        """
        super().__init__(
            (args if args is not None else conf.args)['checkpoints']["maskref_to_maskdet"],
            "maskref_to_maskdet",
            input_index=input_index,
            args=args
        )


class MaskfinToNude(ImageTransformGAN):
    """
    Maskfin -> Nude [GAN]
    """

    def __init__(self, input_index=(-1,), args=None):
        """
        MaskfinToNude Constructor
        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use conf.args)
        """
        super().__init__(
            (args if args is not None else conf.args)['checkpoints']["maskfin_to_nude"],
            "maskfin_to_nude",
            input_index=input_index,
            args=args
        )
