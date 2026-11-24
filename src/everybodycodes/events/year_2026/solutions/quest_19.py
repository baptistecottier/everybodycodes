"""
Event: Lord of the Wings
Quest: The Glasscraft
"""

from collections import defaultdict
from itertools import permutations
from math import prod
from typing import Iterable, Iterator


def preprocessing(puzzle_inputs: dict[int, str]) -> list[list[str]]:
    """
    Parse each input into its layers, each one flattened on a single line.
    """
    windows: list[list[str]] = []
    for notes in puzzle_inputs.values():
        windows.append([
            grid.replace('\n', '') for grid in notes.split('\n\n')
            ])
    return windows


def solver(windows: list[list[str]]) -> Iterator[int]:
    """
    Yield the product of the sizes of the three largest groups of equal
    colors once the two layers of the first notes are mixed; the best such
    product over every way of replacing the digits 1 to 4 of the second
    layer of the second notes by the colors C, K, M and Y; then, for the
    layer of the third notes, the largest product reachable by choosing the
    second layer among C, M and Y: either three groups of non-K cells as
    even as possible, or the K cells and two such groups.
    """
    yield cnt_white_crystals(*windows[0])

    layer1, layer2 = windows[1]
    max_wc = 0
    for perm in permutations("CKMY"):
        candidate = [perm[int(i) - 1] for i in layer2]
        max_wc = max(max_wc, cnt_white_crystals(layer1, candidate))
    yield max_wc

    [layer1] = windows[2]
    k_cnt = layer1.count('K')
    free = len(layer1) - k_cnt
    root, rem = divmod(free, 3)
    half = free // 2
    yield max((root + (rem == 2)) * (root + (rem >= 1)) * root,
              k_cnt * half * (free - half))


def cnt_white_crystals(layer1: Iterable[str], layer2: Iterable[str]) -> int:
    """
    Mix the layers cell by cell and return the product of the sizes of the
    three largest groups of cells with the same color.
    """
    color_cnts: defaultdict[str, int] = defaultdict(int)
    for c1, c2 in zip(layer1, layer2):
        color_cnts[color_add(c1, c2)] += 1
    return prod(sorted(color_cnts.values())[-3:])


def color_add(c1: str, c2: str) -> str:
    """
    Mix two colors: identical colors stay as they are, K absorbs any other
    color, and two different ones among C, M and Y give B for C and M, G for
    C and Y, and R for M and Y.
    """
    if c1 == c2:
        return c1
    if c1 == 'K' or c2 == 'K':
        return 'K'
    match sorted([c1, c2]):
        case ['C', 'M']:
            return 'B'
        case ['C', 'Y']:
            return 'G'
        case ['M', 'Y']:
            return 'R'
        case _:
            raise ValueError("Invalid color combination")
