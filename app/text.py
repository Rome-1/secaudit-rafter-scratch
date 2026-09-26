import re


def normalize(s):
    s = s.strip().lower()
    return re.sub(r"\s+", " ", s)
