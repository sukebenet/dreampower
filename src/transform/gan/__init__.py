"""GAN Transforms."""
import time

import cv2
import torch

from config import Config as Conf
from transform import ImageTransform
from transform.gan.generator import tensor2im
from transform.gan.model import DeepModel, DataLoader


class ImageTransformGAN(ImageTransform):
    """Abstract GAN Image Transformation Class."""

    def __init__(self, checkpoint, phase, input_index=(-1,)):
        """
        Abstract GAN Image Transformation Class Constructor.

        :param checkpoint: <string> path to the checkpoint
        :param phase: <string> phase name
        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(input_index=input_index)

        self._checkpoint = checkpoint
        self._phase = phase
        self._persistent = not Conf.args["disable_persistent_gan"]
        self._gpu_ids = Conf.args["gpu_ids"]

        if self._persistent:
            self.__init_model()

    def __init_model(self):
        start = time.time()
        Conf.log.debug("Loading GAN Model For {}".format(self._phase))
        # Create Model
        self.__model = DeepModel()
        self.__model.initialize(Conf(), self._gpu_ids, self._checkpoint)
        Conf.log.debug("Model load done in {} seconds".format(round(time.time() - start, 2)))

    def _setup(self, *args):
        """
        Load Dataset and Model for the image.

        :param args: <[RGB]> image to be transform
        :return: None
        """
        #if self._gpu_ids:
        #    Conf.log.debug("GAN Processing will use GPU IDs: {}".format(self._gpu_ids))
        #else:
        #    Conf.log.debug("GAN Processing will use CPU")

        if not self._persistent:
            self.__init_model()

    def _execute(self, *args):
        """
        Execute the GAN Transformation the image.

        :param *args: <[RGB]> image to transform
        :return: <RGB> image transformed
        """
        c = Conf()

        # Load custom phase options:
        data_loader = DataLoader(c, args[0])
        self.__dataset = data_loader.load_data()

        mask = None
        for data in self.__dataset:
            generated = self.__model.inference(data["label"], data["inst"])
            im = tensor2im(generated.data[0])
            mask = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
        return mask

    def _clean(self, *args):
        if not self._persistent:
            del self.__dataset
            del self.__model
            torch.cuda.empty_cache()
