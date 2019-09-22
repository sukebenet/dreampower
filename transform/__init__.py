"""Images Transforms."""
from processing import Processing


class ImageTransform(Processing):
    """Abstract Image Transformation Class."""

    def __init__(self, input_index=(-1,)):
        """
        Image Transformation Class Constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """

        super().__init__()
        self.input_index = input_index
