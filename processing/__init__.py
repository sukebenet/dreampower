import os
import shutil
import sys
import tempfile
import time
from multiprocessing.pool import ThreadPool

import cv2
import imageio

from config import Config as conf
from utils import camel_case_to_str, cv2_supported_extension, read_image, write_image


class Process:
    """
    Abstract Process Class
    """
    def __init__(self):
        self.__start = time.time()

    def run(self):
        self.info_start_run()
        self.setup()
        self.execute()
        self.clean()
        self.info_end_run()

    def info_start_run(self):
        self.__start = time.time()
        conf.log.info("Executing {}".format(camel_case_to_str(self.__class__.__name__)))

    def info_end_run(self):
        conf.log.info("{} Finish".format(camel_case_to_str(self.__class__.__name__)))
        conf.log.debug("{} Done in {} seconds".format(
            camel_case_to_str(self.__class__.__name__), round(time.time() - self.__start, 2)))

    def setup(self):
        pass

    def execute(self):
        pass

    def clean(self):
        pass

    def __str__(self):
        return str(self.__class__.__name__)


class SimpleTransform(Process):
    def __init__(self, *args):
        super().__init__()

    def __new__(cls, input_path, phases, output_path):
        if os.path.splitext(input_path)[1] == ".gif":
            return GifTransform(input_path, phases, output_path)
        elif os.path.splitext(input_path)[1] in cv2_supported_extension():
            return SimpleImageTransform(input_path, phases, output_path)
        else:
            return None


class SimpleImageTransform(Process):
    """
    Simple Image Processing Class
    """

    def __init__(self, input_path, phases, output_path):
        """
        ProcessImage Constructor
        :param input_path: <string> original image path to process
        :param output_path: <string> image path to write the result.
        :param phases: <ImageTransform[]> list of transformation each image
        """
        super().__init__()
        self.__phases = phases
        self.__output_path = output_path
        self.__altered_path = conf.args['altered']
        self.__starting_step = conf.args['steps'][0] if conf.args['steps'] else 0
        self.__ending_step = conf.args['steps'][1] if conf.args['steps'] else None

        conf.log.debug("All Phases : {}".format(self.__phases))
        conf.log.debug("To Be Executed Phases : {}".format(self.__phases[self.__starting_step:self.__ending_step]))

        self.__image_steps = [input_path] + [
            os.path.join(self.__altered_path, "{}.png".format(p.__class__.__name__))
            for p in self.__phases[:self.__starting_step]
        ]

    def info_start_run(self):
        super().info_start_run()
        conf.log.info("Processing on {}".format(str(self.__image_steps)[2:-2]))

    def setup(self):
        try:
            self.__image_steps = [read_image(x) if isinstance(x, str) else x for x in self.__image_steps]
        except FileNotFoundError as e:
            conf.log.error(e)
            conf.log.error("{} is not able to resume because it not able to load required images. "
                           .format(camel_case_to_str(self.__class__.__name__)))
            conf.log.error("Possible source of this error is that --altered argument is not a correct "
                           "directory path that contains valid images.")
            sys.exit(1)

    def execute(self):
        """
        Execute all phases on the image
        :return: None
        """
        for p in self.__phases[len(self.__image_steps) - 1:]:
            r = p.run(*[self.__image_steps[i] for i in p.input_index])
            self.__image_steps.append(r)

            if self.__altered_path:
                write_image(r, os.path.join(self.__altered_path, "{}.png".format(p.__class__.__name__)))
                conf.log.debug("Writing {}, Result of the Execution of {}"
                               .format(
                                    os.path.join(self.__altered_path, "{}.png".format(p.__class__.__name__)),
                                    camel_case_to_str(p.__class__.__name__),
                                ))

        write_image(self.__image_steps[-1], self.__output_path)
        conf.log.info("{} Created".format(self.__output_path))
        conf.log.debug("{} Result Image Of {} Execution"
                       .format(self.__output_path, camel_case_to_str(self.__class__.__name__)))

        return self.__image_steps[-1]


class MultipleImageTransform(Process):
    """
    Multiple Image Processing Class
    """

    def __init__(self, input_paths, phases, output_paths, children_process=SimpleTransform):
        """
        ProcessMultipleImages Constructor
        :param input_paths: <string[]> images path list to process
        :param output_paths: <string> images path to write the result
        :param children_process: <ImageTransform> Process to use on the list of input
        :param phases: <ImageTransform[]> list of transformation use by the process each image
        """
        super().__init__()
        self._phases = phases
        self._input_paths = input_paths
        self._output_paths = output_paths
        self._process_list = []
        self.__multiprocessing = conf.multiprocessing()
        self.__children_process = children_process

    def setup(self):
        # TODO detect GIF or JPEG
        self._process_list = [self.__children_process(i[0], self._phases, i[1])
                              for i in zip(self._input_paths, self._output_paths)]

    def execute(self):
        """
        Execute all phases on the list of images
        :return: None
        """

        def process_one_image(a):
            conf.log.info("Processing image : {}/{}".format(a[1] + 1, len(self._process_list)))
            a[0].run()

        if not self.__multiprocessing:
            for x in zip(self._process_list, range(len(self._process_list))):
                process_one_image(x)
        else:
            conf.log.debug("Using Multiprocessing")
            pool = ThreadPool(conf.args['n_cores'])
            pool.map(process_one_image, zip(self._process_list, range(len(self._process_list))))
            pool.close()
            pool.join()


class FolderImageTransform(MultipleImageTransform):
    """
    Folder Image Processing Class
    """

    def __init__(self, input_folder_path, phases, output_folder_path):
        """
        FolderImageTransform Constructor
        """
        super().__init__([], phases, [])
        self.__input_folder_path = input_folder_path
        self.__output_folder_path = output_folder_path
        self.__multiprocessing = conf.multiprocessing()

    def setup(self):
        conf.log.debug([(r, d, f) for r, d, f in os.walk(self.__input_folder_path)])
        self._process_list = [
            MultipleImageTransform(
                [
                    x.path for x in os.scandir(os.path.join(r))
                    if x.is_file() and os.path.splitext(x.path)[1] in cv2_supported_extension() + [".gif"]
                ],
                self._phases,
                [
                    "{}{}{}".format(os.path.splitext(x.path)[0], '_out', os.path.splitext(x.path)[1])
                    if not conf.args['output'] else os.path.join(conf.args['output'], r, os.path.basename(x.path))
                    for x in os.scandir(os.path.join(r))
                    if x.is_file() and os.path.splitext(x.path)[1] in cv2_supported_extension() + [".gif"]
                ]
            ) for r, _, _ in os.walk(self.__input_folder_path)
        ]


class GifTransform(Process):
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
