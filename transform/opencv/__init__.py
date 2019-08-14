from transform import ImageTransform


class ImageTransformOpenCV(ImageTransform):
    """
    OPENCV Image Transform class
    """

    def __init__(self, input_index=(-1,)):
        super().__init__(input_index)


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
