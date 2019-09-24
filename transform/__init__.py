"""Images Transforms."""
from processing import Processing


class ImageTransform(Processing):
    """Abstract Image Transformation Class."""

    class InvalidNumberOfArgs(ValueError):
        def __str__(self):
            return "Invalid nubmmer of arguments given"

    def __init__(self, input_index=(-1,)):
        """
        Image Transformation Class Constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """

        super().__init__()
        self.input_index = input_index

    def run(self, *args, config=None):
        if len(args) != len(self.input_index):
            raise ImageTransform.InvalidNumberOfArgs()
        return super().run(*args, config=config)
