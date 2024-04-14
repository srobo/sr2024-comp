import itertools
import math

import numpy as np

DPI = 150
SIZE_INCHES = (1920 / DPI, 1080 / DPI)


def coprime(a, b):
    return math.gcd(a, b) == 1


def find_coprime(n):
    for a in range(3, math.ceil(math.sqrt(n))):
        if coprime(a, n):
            return a

    return 3


def nth_steps(items):
    """
    >>> nth_steps('ABCDEFG')
    ['A', 'F', 'D', 'B', 'G', 'E']
    """
    n = find_coprime(len(items))
    return list(itertools.islice(
        itertools.islice(
            itertools.cycle(items),
            None,
            None,
            n,
        ),
        len(items),
    ))


def get_teams_with_hues(comp, final_match_num, tlas, highlight):
    # Add 1 to prevent overlap when only showing a small number of teams; due to
    # the circular nature of colour wheels.
    hues = nth_steps(nth_steps(nth_steps(np.linspace(0., 1., len(comp.teams.keys()) + 1))))

    return [
        (team, hue)
        for team, hue in zip(comp.teams.values(), hues)
        if team.tla in tlas
        if team.is_still_around(final_match_num)
    ]
