"""Loader."""


class Loader:
    """ Abstract Loader Class """

    @staticmethod
    def load(uri):
        """
            Load the uri ressource
            :return: <RGB> image
        """
        pass

    @staticmethod
    def uri_validator(uri):
        """
            Validate the uri for the loader
            :return: <bool> True is a valid uri
        """
        return False

    @staticmethod
    def get_loader(uri):
        from loader.fs import FSLoader
        from loader.http import HTTPLoader
        for loader in (FSLoader, HTTPLoader):
            if loader.uri_validator(uri):
                return loader
        return None
