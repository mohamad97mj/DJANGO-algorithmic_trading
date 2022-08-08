from math import floor


def round_down(n, d=2):
    if isinstance(n, (float, int)):
        d = int('1' + ('0' * d))
        return floor(n * d) / d


def find_decimal_place(n):
    n = str(n)
    if 'e' in n:
        return int(n.split('-')[1])
    return len(n.split(".")[1])
