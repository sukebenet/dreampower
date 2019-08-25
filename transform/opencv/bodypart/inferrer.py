"""Inference Body part functions."""
import random

from transform.opencv.bodypart import BodyPart


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
        xmin = int(x - (nip_dim / 2))
        xmax = int(x + (nip_dim / 2))
        ymin = int(y - (nip_dim / 2))
        ymax = int(y + (nip_dim / 2))

        nip_list.append(BodyPart("nip", xmin, ymin, xmax, ymax, x, y, nip_dim, nip_dim))

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

            # Calculate Bounding Box:
            xmin = int(x - (hair_w / 2))
            xmax = int(x + (hair_w / 2))
            ymin = int(y - (hair_h / 2))
            ymax = int(y + (hair_h / 2))

            hair_list.append(BodyPart("hair", xmin, ymin, xmax, ymax, x, y, hair_w, hair_h))

    return hair_list
