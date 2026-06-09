"""
Event: The Song of Ducks and Dragons
Quest: Teeth of the Wind
"""

from math import ceil, floor, prod
from typing import Iterator


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[list[list[int]]]:
    """
    Parse the raw input content into per-part structures.
    """
    mills: list[list[list[int]]] = []
    for note in puzzle_input.values():
        gears: list[list[int]] = []
        for s in note.splitlines():
            gears.append(list(map(int, s.split("|"))) * (2 - s.count("|")))
        mills.append(gears)
    return mills


def solver(
    mills: list[list[list[int]]]
) -> Iterator[int]:
    """
    Calibrate mills
    """
    yield floor(2_025 * ratio(mills[0]))
    yield ceil(10_000_000_000_000 / ratio(mills[1]))
    yield floor(100 * ratio(mills[2]))


def ratio(
    gears: list[list[int]]
) -> float:
    """
    Given a list of gears, return the number of full turns the last gear makes
    if the first one turns exactly once.
    """
    numerator = prod(gears[i][1] for i in range(len(gears) - 1))
    denominator = prod(gears[i][0] for i in range(1, len(gears)))
    return numerator / denominator
