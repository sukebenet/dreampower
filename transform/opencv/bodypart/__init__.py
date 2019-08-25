"""Body part Module."""


class BodyPart:
    """Body part annotation."""

    def __init__(self, name, xmin, ymin, xmax, ymax, x, y, w, h):
        """
        Body Part constructor.

        :param name: <string>
        :param xmin: <int>
        :param ymin: <int>
        :param xmax: <int>
        :param ymax: <int>
        :param x: <int>
        :param y: <int>
        :param w: <int>
        :param h: <int>
        """
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
