"""Extract Body part functions."""
import cv2
import numpy as np

from transform.opencv.bodypart import BodyPart, Dimension, BoundingBox, Center
from transform.opencv.bodypart.inferrer import infer_nip, infer_hair
from transform.opencv.bodypart.resolver import detect_tit_aur_missing_problem, resolve_tit_aur_missing_problems


def extract_annotations(maskdet, enable_pubes):
    """
    Extract Body part annotations.

    :param maskdet: <RGB> maskdet image
    :param enable_pubes: <Boolean> enable/disable pubic hair generation
    :return: (<BodyPart []> bodypart_list) - for failure/error, return an empty list []
    """
    # Find body part
    tits_list = find_body_part(maskdet, "tit")
    aur_list = find_body_part(maskdet, "aur")
    vag_list = find_body_part(maskdet, "vag")
    belly_list = find_body_part(maskdet, "belly")

    # Filter out parts basing on dimension (area and aspect ratio):
    aur_list = filter_dim_parts(aur_list, (100, 1000), (0.5, 3))
    tits_list = filter_dim_parts(tits_list, (1000, 60000), (0.2, 3))
    vag_list = filter_dim_parts(vag_list, (10, 1000), (0.2, 3))
    belly_list = filter_dim_parts(belly_list, (10, 1000), (0.2, 3))

    # Filter couple (if parts are > 2, choose only 2)
    aur_list = filter_couple(aur_list)
    tits_list = filter_couple(tits_list)

    # Detect a missing problem (code of the problem)
    missing_problem = detect_tit_aur_missing_problem(tits_list, aur_list)

    # Check if problem is SOLVEABLE:
    if missing_problem in [3, 6, 7, 8]:
        resolve_tit_aur_missing_problems(tits_list, aur_list, missing_problem)

    # Infer the nips:
    nip_list = infer_nip(aur_list)

    # Infer the hair:
    hair_list = infer_hair(vag_list, enable_pubes)

    # Return a combined list:
    return tits_list + aur_list + nip_list + vag_list + hair_list + belly_list


def find_body_part(image, part_name):
    """
    Find body part.

    :param image: <RGB> image
    :param part_name: <string> part_name
    :return: <BodyPart[]>list
    """
    bodypart_list = []  # empty BodyPart list

    color_mask = get_correct_filter_color(image, part_name)

    # find contours:
    contours, _ = cv2.findContours(color_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # for every contour:
    for cnt in contours:

        if len(cnt) > 5:  # at least 5 points to fit ellipse

            # (x, y), (MA, ma), angle = cv2.fitEllipse(cnt)
            ellipse = cv2.fitEllipse(cnt)

            # Fit Result:
            x = ellipse[0][0]  # center x
            y = ellipse[0][1]  # center y
            angle = ellipse[2]  # angle
            a_min = ellipse[1][0]  # asse minore
            a_max = ellipse[1][1]  # asse maggiore

            h, w = detect_direction(a_max, a_min, angle)

            h, w = normalize_belly_vag(h, part_name, w)

            xmax, xmin, ymax, ymin = BoundingBox.calculate_bounding_box(h, w, x, y)

            BodyPart.add_body_part_to_list(part_name, BoundingBox(xmin, ymin, xmax, ymax), Center(x, y),
                                           Dimension(w, h), bodypart_list)

    return bodypart_list


def detect_direction(a_max, a_min, angle):
    """Detect direction."""
    if angle == 0:
        h = a_max
        w = a_min
    else:
        h = a_min
        w = a_max
    return h, w


def normalize_belly_vag(h, part_name, w):
    """Normalize the belly and vag size."""
    if part_name in ("belly", "vag"):
        if w < 15:
            w *= 2
        if h < 15:
            h *= 2
    return h, w


def get_correct_filter_color(image, part_name):
    """Get the correct color filter."""

    def get_simple_mask(image, l1, l2):
        f1 = np.asarray(l1)  # aur color filter
        f2 = np.asarray(l2)
        color_mask = cv2.inRange(image, f1, f2)
        return color_mask

    if part_name == "tit":
        # Use combined color filter
        f1 = np.asarray([0, 0, 0])  # tit color filter
        f2 = np.asarray([10, 10, 10])
        f3 = np.asarray([0, 0, 250])  # aur color filter
        f4 = np.asarray([0, 0, 255])
        color_mask1 = cv2.inRange(image, f1, f2)
        color_mask2 = cv2.inRange(image, f3, f4)
        color_mask = cv2.bitwise_or(color_mask1, color_mask2)  # combine

    elif part_name == "aur":
        color_mask = get_simple_mask(image, [0, 0, 250], [0, 0, 255])

    elif part_name == "vag":
        color_mask = get_simple_mask(image, [250, 0, 0], [255, 0, 0])

    elif part_name == "belly":
        color_mask = get_simple_mask(image, [250, 0, 250], [255, 0, 255])

    return color_mask


def filter_dim_parts(bp_list, min_max_area, min_max_ar):
    """
    Filter a body part list with area and aspect ration.

    :param bp_list: BodyPart[]>list
    :param min_max_area: <(num,num)> minimum,max area of part
    :param min_max_area: <num> minimum,max aspect ratio
    :return: <BodyPart[]>list
    """
    b_filt = []

    for obj in bp_list:
        if min_max_area[0] < obj.w * obj.h < min_max_area[1] and min_max_ar[0] < obj.w / obj.h < min_max_ar[1]:
            b_filt.append(obj)

    return b_filt


def filter_couple(bp_list):
    """
    Filter couple in body part list.

    :param bp_list: <BodyPart[]>list
    :return: <BodyPart[]>list
    """
    # Remove exceed parts
    if len(bp_list) > 2:

        # trovare coppia (a,b) che minimizza bp_list[a].y-bp_list[b].y
        min_a = 0
        min_b = 1
        min_diff = abs(bp_list[min_a].y - bp_list[min_b].y)

        min_a, min_b = find_min(bp_list, min_a, min_b, min_diff)

        b_filt = [bp_list[min_a], bp_list[min_b]]

        return b_filt
    else:
        # No change
        return bp_list


def find_min(bp_list, min_a, min_b, min_diff):
    for a, _ in enumerate(bp_list):
        for b, _ in enumerate(bp_list):
            # TODO: avoid repetition (1,0) (0,1)
            diff = abs(bp_list[a].y - bp_list[b].y)
            if a != b and diff < min_diff:
                min_diff = diff
                min_a = a
                min_b = b
    return min_a, min_b

def find_color(img, lower, upper):
  color_mask = cv2.inRange(img, lower, upper)
  contours, _ = cv2.findContours(color_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  found = False

  for cnt in contours:
    if len(cnt) > 5:
      found = True
      ellipse = cv2.fitEllipse(cnt)

      x = ellipse[0][0]  # center x
      y = ellipse[0][1]  # center y
      angle = ellipse[2]  # angle
      a_min = ellipse[1][0]  # asse minore
      a_max = ellipse[1][1]  # asse maggiore

      if angle == 0:
        h = a_max
        w = a_min
      else:
        h = a_min
        w = a_max

      xmax, xmin, ymax, ymin = BoundingBox.calculate_bounding_box(h, w, x, y)

  if not found:
    return False

  return [ymin, ymax, xmin, xmax, x, y, a_min, a_max, angle, contours]
