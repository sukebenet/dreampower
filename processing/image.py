"""Image Transform Processing."""
import os
import sys

from config import Config as Conf
from processing import Processing
from processing.utils import select_phases
from utils import read_image, camel_case_to_str, write_image


class ImageProcessing(Processing):
    """Image Processing Class."""

    def __init__(self, args=None):
        """
        Process Image Constructor.

        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(args=args)
        self.__phases = select_phases(self._args)
        self.__input_path = self._args['input']
        self.__output_path = self._args['output']
        self.__altered_path = self._args.get('altered')
        self.__starting_step = self._args['steps'][0] if self._args.get('steps') else 0
        self.__ending_step = self._args['steps'][1] if self._args.get('steps') else None

        Conf.log.debug("All Phases : {}".format(self.__phases))
        Conf.log.debug("To Be Executed Phases : {}".format(self.__phases[self.__starting_step:self.__ending_step]))

        path = self.__altered_path if os.path.isfile(self.__input_path) or not self._args.get('folder_altered')  \
            else os.path.join(self._args['folder_altered'], os.path.basename(self.__output_path))

        self.__image_steps = [self.__input_path] + [
            os.path.join(path, "{}.png".format(p().__class__.__name__))
            for p in self.__phases[:self.__starting_step]
        ]
        Conf.log.debug(self.__image_steps)

    def _info_start_run(self):
        super()._info_start_run()
        Conf.log.info("Processing on {}".format(str(self.__image_steps)[2:-2]))

    def _setup(self, *args):
        try:
            self.__image_steps = [read_image(x) if isinstance(x, str) else x for x in self.__image_steps]
        except FileNotFoundError as e:
            Conf.log.error(e)
            Conf.log.error("{} is not able to resume because it not able to load required images. "
                           .format(camel_case_to_str(self.__class__.__name__)))
            Conf.log.error("Possible source of this error is that --altered argument is not a correct "
                           "directory path that contains valid images.")
            sys.exit(1)

    def _execute(self, *args):
        """
        Execute all phases on the image.

        :return: None
        """
        for p in (x(args=self._args) for x in self.__phases[self.__starting_step:self.__ending_step]):
            r = p.run(*[self.__image_steps[i] for i in p.input_index])
            self.__image_steps.append(r)

            if self.__altered_path:
                path = self.__altered_path \
                    if os.path.isfile(self._args['input']) or not self._args.get('folder_altered') \
                    else os.path.join(self._args['folder_altered'], os.path.basename(self.__output_path))

                write_image(r, os.path.join(path, "{}.png".format(p.__class__.__name__)))

                Conf.log.debug("{} Step Image Of {} Execution".format(
                    os.path.join(path, "{}.png".format(p.__class__.__name__)),
                    camel_case_to_str(p.__class__.__name__),
                ))

        write_image(self.__image_steps[-1], self.__output_path)
        Conf.log.info("{} Created".format(self.__output_path))
        Conf.log.debug("{} Result Image Of {} Execution"
                       .format(self.__output_path, camel_case_to_str(self.__class__.__name__)))

        return self.__image_steps[-1]
