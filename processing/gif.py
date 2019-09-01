"""GIF Transform Processing."""
import os
import shutil
import tempfile

import cv2
import imageio

from config import Config as Conf
from processing import Processing
from processing.multiple import MultipleImageProcessing
from processing.utils import select_phases
from utils import write_image


class GifProcessing(Processing):
    """GIF Image Processing Class."""

    def __init__(self, args=None):
        """
        Image Transform GIF Constructor.

        :param args: <dict> args parameter to run images transformations (default use Conf.args)
        """
        super().__init__(args=args)
        self.__phases = select_phases(self._args)
        self.__input_path = args['input']
        self.__output_path = args['output']
        self.__tmp_dir = None
        self.__temp_input_paths = []
        self.__temp_output_paths = []

    def _setup(self, *args):
        self.__tmp_dir = tempfile.mkdtemp()
        Conf.log.debug("Temporay dir is {}".format(self.__tmp_dir))
        imgs = imageio.mimread(self.__input_path)
        Conf.log.info("GIF have {} Frames To Process".format(len(imgs)))
        self.__temp_input_paths = [os.path.join(self.__tmp_dir, "intput_{}.png".format(i))
                                   for i in range(len(imgs))]
        self._args['input'] = self.__temp_input_paths
        self.__temp_output_paths = [os.path.join(self.__tmp_dir, "output_{}.png".format(i))
                                    for i in range(len(imgs))]
        self._args['output'] = self.__temp_output_paths

        for i in zip(imgs, self.__temp_input_paths):
            write_image(cv2.cvtColor(i[0], cv2.COLOR_RGB2BGR), i[1])

    def _execute(self, *args):
        """
        Execute all phases on each frames of the gif and recreate the gif.

        :return: None
        """
        MultipleImageProcessing(args=self._args).run()

        dir_out = os.path.dirname(self.__output_path)
        if dir_out != '':
            os.makedirs(dir_out, exist_ok=True)
        imageio.mimsave(self.__output_path, [imageio.imread(i) for i in self.__temp_output_paths])

        Conf.log.info("{} Gif Created ".format(self.__output_path))

    def _clean(self, *args):
        shutil.rmtree(self.__tmp_dir)
