"""Body part Module."""


class BodyPart:
    """Body part annotation."""

    def __init__(self, name, bounding_box, center, dimension):
        """
        Body Part constructor.

        :param name: <string>
        :param bounding_box: <int>
        :param center: <int>
        :param xmax: <int>
        """
        self.name = name
        # Bounding Box:
        self.bounding_box = bounding_box
        # Center:
        self.center = center
        # Dimension:
        self.dimension = dimension

    @staticmethod
    def add_body_part_to_list(name, bounding_box, center, dimension, l):
        l.append(
            BodyPart(name, bounding_box, center, dimension)
        )

    @property
    def xmin(self):
        return self.bounding_box.xmin

    @property
    def ymin(self):
        return self.bounding_box.ymin

    @property
    def xmax(self):
        return self.bounding_box.xmax

    @property
    def ymax(self):
        return self.bounding_box.ymax

    @property
    def x(self):
        return self.center.x

    @property
    def y(self):
        return self.center.y

    @property
    def w(self):
        return self.dimension.w

    @property
    def h(self):
        return self.dimension.h


class Dimension:
    """Dimension."""

    def __init__(self, w, h):
        """Dimension Constructor."""
        self.w = w
        self.h = h


class Center:
    """Center."""

    def __init__(self, x, y):
        """Center Constructor."""
        self.x = x
        self.y = y


class BoundingBox:
    """BoundingBox."""

    def __init__(self, xmin, ymin, xmax, ymax):
        """BoundingBox Constructor"""
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    @staticmethod
    def calculate_bounding_box(h, w, x, y):
        """Calculate Bounding Box."""
        xmin = int(x - (w / 2))
        xmax = int(x + (w / 2))
        ymin = int(y - (h / 2))
        ymax = int(y + (h / 2))
        return xmax, xmin, ymax, ymin
