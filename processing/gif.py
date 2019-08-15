import os
import shutil
import tempfile

import cv2
import imageio

from config import Config as conf
from processing import Process
from processing.image import MultipleImageTransform
from utils import write_image


class SimpleGIFTransform(Process):
    """
    GIF Image Processing Class
    """

    def __init__(self, input_path, phases, output_path):
        """
        ImageTransformGIF Constructor
        :param images: <string> gif path to process
        :param output_path: <string> image path to write the result
        :param phases: <ImageTransform[]> list of transformation use by the process each image
        """
        super().__init__()
        self.__phases = phases
        self.__input_path = input_path
        self.__output_path = output_path
        self.__tmp_dir = None
        self.__temp_input_paths = []
        self.__temp_output_paths = []

    def setup(self):
        self.__tmp_dir = tempfile.mkdtemp()
        conf.log.debug("Temporay dir is {}".format(self.__tmp_dir))
        imgs = imageio.mimread(self.__input_path)
        conf.log.info("GIF have {} Frames To Process".format(len(imgs)))
        self.__temp_input_paths = [os.path.join(self.__tmp_dir, "intput_{}.png".format(i))
                                   for i in range(len(imgs))]

        self.__temp_output_paths = [os.path.join(self.__tmp_dir, "output_{}.png".format(i))
                                    for i in range(len(imgs))]

        [write_image(cv2.cvtColor(i[0], cv2.COLOR_RGB2BGR), i[1]) for i in zip(imgs, self.__temp_input_paths)]

    def execute(self):
        """
        Execute all phases on each frames of the gif and recreate the gif
        :return: None
        """
        MultipleImageTransform(self.__temp_input_paths, self.__phases, self.__temp_output_paths).run()

        imageio.mimsave(self.__output_path, [imageio.imread(i) for i in self.__temp_output_paths])
        conf.log.info("{} Gif Created ".format(self.__output_path))

    def clean(self):
        shutil.rmtree(self.__tmp_dir)