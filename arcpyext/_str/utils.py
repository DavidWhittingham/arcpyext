import unicodedata


def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)


def caseless_find(input_str, sub, start=None, end=None):
    return normalize_caseless(input_str).find(normalize_caseless(sub), start, end)


def normalize_caseless(text):
    if hasattr(text, "casefold"):
        # use casefold on Py3 to normalize correctly
        return unicodedata.normalize("NFKD", text.casefold())
    else:
        # Python 2 or other weird non-casefoldable string, just use upper/lower as fallback
        return text.upper().lower()