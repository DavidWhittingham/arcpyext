TRUEISH_TEST_PARAMS = [
    (True, True),
    ("TRUE", True),
    ("T", True),
    ("tRUe", True),
    ("t", True),
    (False, False),
    ("FALSE", False),
    ("F", False),
    ("faLSe", False),
    ("f", False),
    (1, True),
    (0, False),
    (2, False),
    (-1, False)
]