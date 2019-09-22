import os
import re
import tempfile

from utils import dl_file, read_image
from loader import Loader


regex_url = re.compile(
    r'^(?:http)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class HTTPLoader(Loader):
    """ Abstract Loader Class """
    @staticmethod
    def run(uri):
        """
            Run the loader ressource
            :return: <RGB> image
        """
        _, tmp_path = tempfile.mkstemp()
        dl_file(uri, tmp_path)
        img = read_image(tmp_path)
        os.remove(tmp_path)
        return img

    @staticmethod
    def uri_validator(uri):
        return regex_url.match(uri)
