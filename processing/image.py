import os
import sys
from multiprocessing.pool import ThreadPool

from config import Config as conf
from processing import Process
from utils import read_image, write_image, camel_case_to_str


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
        conf.log.debug("Processing on {}".format(self.__image_steps))

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
        conf.log.debug("Writing {}, Result Image Of {} Execution"
                       .format(self.__output_path, camel_case_to_str(self.__class__.__name__)))

        return self.__image_steps[-1]


class MultipleImageTransform(Process):
    """
    Multiple Image Processing Class
    """

    def __init__(self, input_paths, phases, output_paths, children_process=SimpleImageTransform):
        """
        ProcessMultipleImages Constructor
        :param input_paths: <string[]> images path list to process
        :param output_paths: <string> images path to write the result
        :param children_process: <ImageTransform> Process to use on the list of input
        :param phases: <ImageTransform[]> list of transformation use by the process each image
        """
        super().__init__()
        self.__phases = phases
        self.__input_paths = input_paths
        self.__output_paths = output_paths
        self.__process_list = []
        self.__multiprocessing = conf.multiprocessing()
        self.__children_process = children_process

    def setup(self):
        self.__process_list = [self.__children_process(i[0], self.__phases, i[1])
                               for i in zip(self.__input_paths, self.__output_paths)]

    def execute(self):
        """
        Execute all phases on the list of images
        :return: None
        """

        def process_one_image(a):
            conf.log.info("Processing image : {}/{}".format(a[1] + 1, len(self.__process_list)))
            a[0].run()

        if not self.__multiprocessing:
            for x in zip(self.__process_list, range(len(self.__process_list))):
                process_one_image(x)
        else:
            conf.log.debug("Using Multiprocessing")
            pool = ThreadPool(conf.args['n_cores'])
            pool.map(process_one_image, zip(self.__process_list, range(len(self.__process_list))))
            pool.close()
            pool.join()
