from slugify import slugify
import os

from autonomous import log


def slug(text):
    """Convert a string to all caps."""
    return slugify(text)


def basename(text):
    """Convert a string to all caps."""
    return os.path.splitext(os.path.basename(text))[0]


def flattenlistvalues(list_of_dicts):
    values = []
    for dictionary in list_of_dicts:
        for value in dictionary.values():
            values.append(value)
    return values
