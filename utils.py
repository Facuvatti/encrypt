import random

def split_into_parts(total, y, n, min_part=0):
    """
    Split an integer into `n` pseudo-random parts summing exactly to `total`,
    using the integer `y` as the sole source of randomness.

    `y` is used directly as the seed of a fresh PRNG, so the same `y`
    always produces the same split and a different `y` produces a
    different split. The `n - 1` cut points are drawn uniformly in
    `[0, slack]` (where `slack = total - n * min_part`), sorted, and
    differenced using the broken-stick construction.

    Parameters
    ----------
    total : int
        The integer to divide.
    y : int
        Integer seed acting as the entropy source.
    n : int
        Number of parts (must be >= 1).
    min_part : int, optional
        Minimum value guaranteed for every part (default 0).

    Returns
    -------
    list[int]
        `n` non-negative integers summing to `total`, each >= `min_part`.

    Raises
    ------
    ValueError
        If `n < 1`, `min_part < 0`, or `total < n * min_part`.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if min_part < 0:
        raise ValueError("min_part must be >= 0")
    if total < n * min_part:
        raise ValueError("total must be >= n * min_part")

    slack = total - n * min_part
    if n == 1:
        return [total]

    r = random.Random(y)
    cuts = sorted(r.randint(0, slack) for _ in range(n - 1))

    parts = []
    previous = 0
    for c in cuts:
        parts.append(min_part + c - previous)
        previous = c
    parts.append(min_part + slack - previous)
    return parts
def randint(min, max, divider):
    while True:
        number = random.randint(min, max)
        if number % divider != 0:
            return number
