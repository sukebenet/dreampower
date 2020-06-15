""" File Sytem Loading """
import os

from loader import Loader
from utils import read_image


class FSLoader(Loader):
    """ File System Loader Class """
    @staticmethod
    def load(uri):
        """
            Load the file system ressource
            :return: <RGB> image
        """
        return read_image(uri)

    @staticmethod
    def uri_validator(uri):
        """
            Validate the uri is a filesystem file
            :return: <bool> True is a valid uri
        """
        return os.path.exists(uri)
