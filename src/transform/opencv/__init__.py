"""OpenCV Transforms."""
from transform import ImageTransform


class ImageTransformOpenCV(ImageTransform):
    """OPENCV Image Transform class."""

    def __init__(self, input_index=(-1,)):
        """
        Image Transform OpenCV Constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(input_index=input_index)
