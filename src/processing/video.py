"""Video Transform Processing."""
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


class VideoProcessing(Processing):
    """Video Image Processing Class."""
    def _setup(self, *args):
        self.__phases = select_phases(self._args)
        self.__input_path = self._args['input']
        self.__output_path = self._args['output']
        self.__tmp_dir = None
        self.__temp_input_paths = []
        self.__temp_output_paths = []
        self.__tmp_dir = tempfile.mkdtemp()

        Conf.log.debug("Temporay dir is {}".format(self.__tmp_dir))

        imgs = imageio.get_reader(self.__input_path)

        self.__temp_input_paths = []
        self.__temp_output_paths = []

        for i, im in enumerate(imgs):
            frame_input_path = os.path.join(self.__tmp_dir, "input_{}.png".format(i))
            frame_output_path = os.path.join(self.__tmp_dir, "output_{}.png".format(i))

            self.__temp_input_paths = self.__temp_input_paths + [frame_input_path]
            self.__temp_output_paths = self.__temp_output_paths + [frame_output_path]

            write_image(cv2.cvtColor(im, cv2.COLOR_RGB2BGR), frame_input_path)

        Conf.log.info("Video have {} Frames To Process".format(len(self.__temp_input_paths)))

        self._args['input'] = self.__temp_input_paths
        self._args['output'] = self.__temp_output_paths

    def _execute(self, *args):
        """
        Execute all phases on each frames of the gif and recreate the gif.

        :return: None
        """
        MultipleImageProcessing().run(config=self._args)

        dir_out = os.path.dirname(self.__output_path)

        if dir_out != '':
            os.makedirs(dir_out, exist_ok=True)

        imageio.mimsave(self.__output_path, [imageio.imread(i) for i in self.__temp_output_paths])

        Conf.log.info("{} Video Created ".format(self.__output_path))

    def _clean(self, *args):
        shutil.rmtree(self.__tmp_dir)
