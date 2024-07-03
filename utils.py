import random
import string


def base62(length):
    """
    Generate a random base62 string of the specified length.
    """
    base62_chars = string.ascii_letters + string.digits
    return "".join(random.choice(base62_chars) for _ in range(length))
