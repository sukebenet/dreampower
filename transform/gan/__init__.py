"""GAN Transforms."""

import cv2

from config import Config as Conf
from transform import ImageTransform
from transform.gan.generator import tensor2im
from transform.gan.model import DeepModel, DataLoader


class ImageTransformGAN(ImageTransform):
    """Abstract GAN Image Transformation Class."""

    def __init__(self, checkpoint, phase, input_index=(-1,), args=None):
        """
        Abstract GAN Image Transformation Class Constructor.

        :param checkpoint: <string> path to the checkpoint
        :param phase: <string> phase name
        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(input_index=input_index, args=args)
        self.__checkpoint = checkpoint
        self.__phase = phase
        self.__gpu_ids = self._args["gpu_ids"]

    def _setup(self, *args):
        """
        Load Dataset and Model fot the image.

        :param args: <[RGB]> image to be transform
        :return: None
        """
        if self.__gpu_ids:
            Conf.log.debug("GAN Processing Using GPU IDs: {}".format(self.__gpu_ids))
        else:
            Conf.log.debug("GAN Processing Using CPU")

        c = Conf()

        # Load custom phase options:
        data_loader = DataLoader(c, args[0])
        self.__dataset = data_loader.load_data()

        # Create Model
        self.__model = DeepModel()
        self.__model.initialize(c, self.__gpu_ids, self.__checkpoint)

    def _execute(self, *args):
        """
        Execute the GAN Transformation the image.

        :param *args: <[RGB]> image to transform
        :return: <RGB> image transformed
        """
        mask = None
        for data in self.__dataset:
            generated = self.__model.inference(data["label"], data["inst"])
            im = tensor2im(generated.data[0])
            mask = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
        return mask
