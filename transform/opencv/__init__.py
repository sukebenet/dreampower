from transform import ImageTransform


class ImageTransformOpenCV(ImageTransform):
    """
    OPENCV Image Transform class
    """

    def __init__(self, input_index=(-1,), args=None,):
        """
        ImageTransformOpenCV Constructor
        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use conf.args)
        """
        super().__init__(args=args, input_index=input_index)


class BodyPart:
    """
    Body part annotation
    """

    def __init__(self, name, xmin, ymin, xmax, ymax, x, y, w, h):
        self.name = name
        # Bounding Box:
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        # Center:
        self.x = x
        self.y = y
        # Dimensione:
        self.w = w
        self.h = h
