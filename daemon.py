"""daemon logic."""
import os
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config import Config as Conf
from transform.gan.mask import CorrectToMask, MaskrefToMaskdet, MaskfinToNude
from transform.opencv.correct import DressToCorrect
from transform.opencv.mask import MaskToMaskref, MaskdetToMaskfin


class Watcher:
    """Watch a directory change."""

    def __init__(self, watching_dir, out_dir):
        """
        Watcher constructor.

        :param watching_dir: <string> directory to watch
        :param out_dir: <string> directory where save transformations
        """
        self.__observer = Observer()
        self.__watching_dir = watching_dir
        self.__out_dir = out_dir

        if not os.path.isdir(self.__watching_dir):
            Conf.log.error("{} Watching Dir Doesn't Exit.".format(self.__watching_dir))
            sys.exit(0)

        if not os.path.isdir(self.__out_dir):
            Conf.log.error("{} Output Dir Doesn't Exit.".format(self.__watching_dir))
            sys.exit(0)

    def run(self):
        """
        Run the Watcher.

        :return: None
        """
        event_handler = Handler(self.__out_dir)
        self.__observer.schedule(event_handler, self.__watching_dir, recursive=True)
        self.__observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.__observer.stop()
        except Exception as e:
            self.__observer.stop()
            Conf.log.error(e)
            Conf.log.error("An Unhandled Error Occurred.")
            sys.exit(1)
        self.__observer.join()


class Handler(FileSystemEventHandler):
    """Handle a change in a watch directory."""

    def __init__(self, out_dir):
        """
        Create an Handler.

        :param out_dir: <string> directory where save transformations
        """
        self.__out_dir = out_dir
        self.__phases = [
            DressToCorrect, CorrectToMask, MaskToMaskref, MaskrefToMaskdet, MaskdetToMaskfin, MaskfinToNude
        ]

    def on_created(self, event):
        """
        Call when a file or directory is created.

        :param event: <DirCreatedEvent|FileCreatedEvent> trigger event
        :return: None
        """
        if event.is_directory:
            Conf.log.debug("Received directory created event {}.".format(event.src_path))
            # TODO Implements this


def main(_):
    """
    Start daemon main logic.

    :param _: None
    :return: None
    """
    Watcher("test_dir", "out_dir").run()
