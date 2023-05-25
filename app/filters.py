from slugify import slugify


def slug(text):
    """Convert a string to all caps."""
    return slugify(text)
