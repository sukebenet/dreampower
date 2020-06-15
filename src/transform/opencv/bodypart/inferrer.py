"""Inference Body part functions."""
import random

from transform.opencv.bodypart import BodyPart, BoundingBox, Dimension, Center


def infer_nip(aur_list):
    """
    Infer nipples.

    :param aur_list: <BodyPart[]> aur list)
    :return: <BodyPart[]> nip list
    """
    nip_list = []

    for aur in aur_list:
        # Nip rules:
        # - circle (w == h)
        # - min dim: 5
        # - bigger if aur is bigger
        nip_dim = int(5 + aur.w * random.uniform(0.03, 0.09))

        # center:
        x = aur.x
        y = aur.y

        # Calculate Bounding Box:
        xmax, xmin, ymax, ymin = BoundingBox.calculate_bounding_box(nip_dim, nip_dim, x, y)

        BodyPart.add_body_part_to_list("nip", BoundingBox(xmin, ymin, xmax, ymax), Center(x, y),
                                       Dimension(nip_dim, nip_dim), nip_list)

    return nip_list


def infer_hair(vag_list, enable):
    """
    Infer vaginal hair.

    :param vag_list: <BodyPart[]> vag list
    :param enable: <Boolean> Enable or disable hair generation
    :return: <BodyPart[]> hair list
    """
    hair_list = []

    if enable:
        for vag in vag_list:
            # Hair rules:
            hair_w = vag.w * random.uniform(0.4, 1.5)
            hair_h = vag.h * random.uniform(0.4, 1.5)

            # center:
            x = vag.x
            y = vag.y - (hair_h / 2) - (vag.h / 2)

            xmax, xmin, ymax, ymin = BoundingBox.calculate_bounding_box(hair_h, hair_w, x, y)

            BodyPart.add_body_part_to_list("hair", BoundingBox(xmin, ymin, xmax, ymax), Center(x, y),
                                           Dimension(hair_w, hair_h), hair_list)

    return hair_list
