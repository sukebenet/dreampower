"""Inference Body problems resolver."""
import random

from transform.opencv.bodypart import BodyPart, BoundingBox, Center, Dimension


def detect_tit_aur_missing_problem(tits_list, aur_list):
    """
    Detect tits aur missing problem.

    (<int> problem code)
    #   TIT  |  AUR  |  code |  SOLVE?  |
    #    0   |   0   |   1   |    NO    |
    #    0   |   1   |   2   |    NO    |
    #    0   |   2   |   3   |    YES   |
    #    1   |   0   |   4   |    NO    |
    #    1   |   1   |   5   |    NO    |
    #    1   |   2   |   6   |    YES   |
    #    2   |   0   |   7   |    YES   |
    #    2   |   1   |   8   |    YES   |

    :param tits_list: <BodyPart[]> tits list
    :param aur_list: <BodyPart[]> aur list
    :return: <int> problem code
    """
    return {
        (0, 0): 1,
        (0, 1): 2,
        (0, 2): 3,
        (1, 0): 4,
        (1, 1): 5,
        (1, 2): 6,
        (2, 0): 7,
        (2, 1): 8,
    }.get((len(tits_list), len(aur_list)), -1)


def resolve_tit_aur_missing_problems(tits_list, aur_list, problem_code):
    """
    Resolve tits missing aur problem.

    :param tits_list: <BodyPart[]> tits list
    :param aur_list: <BodyPart[]> aur list
    :param problem_code: <int> problem code
    :return: None
    """

    def find_l2_width_is_full(l1, l2):

        d1 = abs(l1[0].x - l2[0].x)
        d2 = abs(l1[0].x - l2[1].x)
        if d1 > d2:
            # l1[0] is empty
            new_x = l2[0].x
            new_y = l2[0].y
        else:
            # l1[1] is empty
            new_x = l2[1].x
            new_y = l2[1].y
        return new_x, new_y

    def resolve_problem_3():
        random_tit_factor = random.randint(2, 5)  # TOTEST

        # Add the first tit:
        new_w = aur_list[0].w * random_tit_factor  # TOTEST
        new_x = aur_list[0].x
        new_y = aur_list[0].y

        xmax, xmin, ymax, ymin = BoundingBox.calculate_bounding_box(new_w, new_w, new_x, new_y)

        BodyPart.add_body_part_to_list("tit", BoundingBox(xmin, ymin, xmax, ymax), Center(new_x, new_y),
                                       Dimension(new_w, new_w), tits_list)

        # Add the second tit:
        new_w = aur_list[1].w * random_tit_factor  # TOTEST
        new_x = aur_list[1].x
        new_y = aur_list[1].y

        xmax, xmin, ymax, ymin = BoundingBox.calculate_bounding_box(new_w, new_w, new_x, new_y)

        BodyPart.add_body_part_to_list("tit", BoundingBox(xmax, xmin, ymax, ymin), Center(new_x, new_y),
                                       Dimension(new_w, new_w), tits_list)

    def resolve_problem_6():
        # Find width aur is full:
        new_x, new_y = find_l2_width_is_full(tits_list, aur_list)
        new_w = tits_list[0].w / 2

        # Calculate Bounding Box:
        xmax, xmin, ymax, ymin = BoundingBox.calculate_bounding_box(new_w, new_w, new_x, new_y)

        BodyPart.add_body_part_to_list("tit", BoundingBox(xmin, ymin, xmax, ymax), Center(new_x, new_y),
                                       Dimension(tits_list[0].w, tits_list[0].w), tits_list)

    def resolve_problem_7():
        # Add the first aur:
        new_w = tits_list[0].w * random.uniform(0.03, 0.1)  # TOTEST
        new_x = tits_list[0].x
        new_y = tits_list[0].y

        xmax, xmin, ymax, ymin = BoundingBox.calculate_bounding_box(new_w, new_w, new_x, new_y)

        BodyPart.add_body_part_to_list("aur", BoundingBox(xmin, ymin, xmax, ymax), Center(new_x, new_y),
                                       Dimension(new_w, new_w), aur_list)

        # Add the second aur:
        new_w = tits_list[1].w * random.uniform(0.03, 0.1)  # TOTEST
        new_x = tits_list[1].x
        new_y = tits_list[1].y

        xmax, xmin, ymax, ymin = BoundingBox.calculate_bounding_box(new_w, new_w, new_x, new_y)

        BodyPart.add_body_part_to_list("aur", BoundingBox(xmin, ymin, xmax, ymax), Center(new_x, new_y),
                                       Dimension(new_w, new_w), aur_list)

    def resolve_problem_8():
        # Find width tit is full
        new_x, new_y = find_l2_width_is_full(aur_list, tits_list)

        # Calculate Bounding Box:
        xmin = int(new_x - (aur_list[0].w / 2))
        xmax = int(new_x + (aur_list[0].w / 2))
        ymin = int(new_y - (aur_list[0].w / 2))
        ymax = int(new_y + (aur_list[0].w / 2))

        BodyPart.add_body_part_to_list("aur", BoundingBox(xmin, ymin, xmax, ymax), Center(new_x, new_y),
                                       Dimension(aur_list[0].w, aur_list[0].w), aur_list)

    {
        3: resolve_problem_3,
        6: resolve_problem_6,
        7: resolve_problem_7,
        8: resolve_problem_8,
    }.get(problem_code, lambda: None)()


def detect_tit_aur_position_problem(tits_list, aur_list):
    """
    Detect tits position problem.

    :param tits_list: <BodyPart[]> tits list
    :param aur_list: <BodyPart[]> aur list
    :return: <Boolean>
    """

    def detect_tits_too_narrow_horizontally():
        diff_tits_x = abs(tits_list[0].x - tits_list[1].x)
        return diff_tits_x < 40

    def detect_tits_too_narrow_vertically():
        diff_tits_y = abs(tits_list[0].y - tits_list[1].y)
        return diff_tits_y > 120

    def detect_tits_too_equal_or_different_width():
        diff_tits_w = abs(tits_list[0].w - tits_list[1].w)
        return (diff_tits_w < 0.1) or (diff_tits_w > 60)

    def detect_tits_body_position_is_too_low():
        # Calculate the ratio between y and aurs distance
        rapp = aur_list[0].y / (abs(aur_list[0].x - aur_list[1].x))
        return aur_list[0].y > 350 and rapp > 2.8

    return (detect_tits_too_narrow_horizontally() or detect_tits_too_narrow_vertically() or
            detect_tits_too_equal_or_different_width() or detect_tits_body_position_is_too_low)
