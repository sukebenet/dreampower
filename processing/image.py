"""Image Transform Processing."""
import os
import sys
import hashlib

from config import Config as Conf
from processing import Processing
from processing.utils import select_phases
from processing.worker import run_worker
from utils import camel_case_to_str, write_image
from loader import Loader


class ImageProcessing(Processing):
    """Image Processing Class."""
    def _setup(self, *args):
        """
        Process Image Constructor.

        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        self.__phases = select_phases(self._args)
        self.__input_path = self._args['input']
        self.__output_path = self._args['output']
        self.__altered_path = self._args.get('altered')
        self.__starting_step = self._args['steps'][0] if self._args.get('steps') else 0
        self.__ending_step = self._args['steps'][1] if self._args.get('steps') else None

        Conf.log.debug("All Phases : {}".format(self.__phases))
        Conf.log.debug("To Be Executed Phases : {}".format(self.__phases[self.__starting_step:self.__ending_step]))

        if (self._args.get('folder_altered')):
            checksum_path = os.path.join(self._args['folder_altered'], str(hashlib.md5(open(self.__input_path, 'rb').read()).hexdigest()))
            if (not os.path.isdir(checksum_path)):
               os.makedirs(checksum_path, exist_ok=True)
            self._args['folder_altered'] = checksum_path
            path = checksum_path
        elif (self.__altered_path):
            checksum_path = os.path.join(self.__altered_path, str(hashlib.md5(open(self.__input_path, 'rb').read()).hexdigest()))
            if (not os.path.isdir(checksum_path)):
               os.makedirs(checksum_path, exist_ok=True)
            self.__altered_path = checksum_path
            path = self.__altered_path

        self.__image_steps = [self.__input_path] + [
            os.path.join(path, "{}.png".format(p().__class__.__name__))
            for p in self.__phases[:self.__starting_step]
        ]
        Conf.log.info("Processing on {}".format(str(self.__image_steps)[2:-2]))
        Conf.log.debug(self.__image_steps)

        try:
            self.__image_steps = [
                (Loader.get_loader(x)).load(x) if isinstance(x, str) else x for x in self.__image_steps
            ]
        except (FileNotFoundError, AttributeError) as e:
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
        for p in (x for x in self.__phases[self.__starting_step:self.__ending_step]):
            r = run_worker(p, self.__image_steps, config=self._args)
            self.__image_steps.append(r)

            if self.__altered_path:
                if (self._args.get('folder_altered')):
                    path = self._args['folder_altered']
                else:
                    path = self.__altered_path

                write_image(r, os.path.join(path, "{}.png".format(p.__name__)))

                Conf.log.debug("{} Step Image Of {} Execution".format(
                    os.path.join(path, "{}.png".format(p.__name__)),
                    camel_case_to_str(p.__name__),
                ))

        write_image(self.__image_steps[-1], self.__output_path)
        Conf.log.info("{} Created".format(self.__output_path))
        Conf.log.debug("{} Result Image Of {} Execution"
                       .format(self.__output_path, camel_case_to_str(self.__class__.__name__)))

        return self.__image_steps[-1]
