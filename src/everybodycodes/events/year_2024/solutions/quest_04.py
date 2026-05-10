"""
Event: The Kingdom of Algorithmia
Quest: Royal Smith's Puzzle
"""

from collections.abc import Callable, Iterator
from statistics import median
from typing import TypeAlias

NailLengths: TypeAlias = list[int]


def min_level(nails: NailLengths) -> int:
    """
    Return the minimum nail length.

    This typed wrapper exists to avoid type-checker warnings when passing
    overloaded builtins like min as callbacks.
    """
    return min(nails)


def median_level(nails: NailLengths) -> int:
    """
    Return the integer median nail length.

    This typed wrapper exists to avoid type-checker warnings in callback
    tuples used by solver.
    """
    return int(median(nails))


def preprocessing(puzzle_input: str) -> list[NailLengths]:
    """
    Parse the raw input content into per-part structures.
    """
    return [
        list(map(int, _nails.strip().splitlines()))
        for _nails in puzzle_input.split("---")
    ]


def solver(lengths: list[NailLengths]) -> Iterator[int]:
    """
    Yield three aggregated hammer_strikes results for the input parts,
    using min for the first two parts and median for the third.
    """
    target_levels: tuple[Callable[[NailLengths], int], ...] = (
        min_level,
        min_level,
        median_level,
    )
    for to_level in zip(lengths, target_levels):
        yield hammer_strikes(*to_level)


def hammer_strikes(nails: NailLengths, f: Callable[[NailLengths], int]) -> int:
    """
    Return the total number of strikes required to move each nail to the
    integer target produced by applying f to the nails.
    """
    target = int(f(nails))
    return sum(abs(nail - target) for nail in nails)
