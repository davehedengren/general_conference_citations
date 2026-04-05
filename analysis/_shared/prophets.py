"""Prophet tenure dates for the period covered by the dataset (1971+).

Start dates are when they became President of the Church.
Tuples: (name, start_year, start_month, end_year, end_month). None end = incumbent.
"""

PROPHETS = [
    ("Joseph Fielding Smith", 1970, 1, 1972, 7),
    ("Harold B. Lee",         1972, 7, 1973, 12),
    ("Spencer W. Kimball",    1973, 12, 1985, 11),
    ("Ezra Taft Benson",      1985, 11, 1994, 5),
    ("Howard W. Hunter",      1994, 6, 1995, 3),
    ("Gordon B. Hinckley",    1995, 3, 2008, 1),
    ("Thomas S. Monson",      2008, 2, 2018, 1),
    ("Russell M. Nelson",     2018, 1, None, None),
]


def prophet_at(year: int, month: int) -> str:
    y = year * 100 + month
    for name, sy, sm, ey, em in PROPHETS:
        start = sy * 100 + sm
        end = (ey * 100 + em) if ey is not None else 9999_99
        if start <= y <= end:
            return name
    return "Unknown"
