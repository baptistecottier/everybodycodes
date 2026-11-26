"""
Event: Lord of the Wings
Quest: The Sortcery
"""

from collections.abc import Iterator
from itertools import groupby


def preprocessing(puzzle_inputs: dict[int, str]) -> list[str]:
    """
    Return the shelf of each input.
    """
    return list(puzzle_inputs.values())


def solver(shelves: list[str]) -> Iterator[int]:
    """
    Yield the number of flips applied to the first shelf until it has as many
    groups of identical items as kinds of items, then the total number of
    items moved by the flips applied to the second shelf repeated ten times.
    """
    shelf = shelves[0]
    moved: list[int] = []
    while (shelf := flip(shelf, moved)):
        continue
    yield len(moved)

    shelf = shelves[1] * 10
    moved = []
    while (shelf := flip(shelf, moved)):
        continue
    yield sum(moved)


def flip(shelf: str, moved: list[int]) -> str:
    """
    Return the shelf rearranged once, or an empty string if it already has as
    many groups of identical items as kinds of items. Otherwise, the number
    of items moved is appended to moved.
    """
    groups = [(k, ''.join(g)) for k, g in (groupby(shelf))]
    n = len(set(shelf))
    shelf = ""
    if len(groups) == n:
        return shelf
    to_match, grp = groups[0]
    shelf += grp
    i = len(groups) - 1
    si = 0
    m = 0
    while i >= si:
        if groups[i][0] == to_match:
            if i == si:
                si += 1
                to_match = groups[si][0]
                shelf += groups[si][1]
                i = len(groups) - 1
                continue
            for j in range(i, si, -1):
                shelf += groups[j][1]
                m += len(groups[j][1])
            for j in range(i + 1, len(groups)):
                shelf += groups[j][1]
            break
        i -= 1
    moved.append(m)
    return shelf
