"""
Event: The Song of Ducks and Dragons
Quest: Deadline-Driven Development
"""

from collections import defaultdict
from math import ceil
from typing import Iterator


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[list[list[int]]]:
    """
    Parse the raw input content into per-part structures.
    """
    areas: list[list[list[int]]] = []
    for puzzle_input in puzzle_inputs.values():
        area: list[list[int]] = []
        for line in puzzle_input.splitlines():
            row: list[int] = []
            for c in list(line):
                if c == 'S':
                    row.append(-1)
                elif c == '@':
                    row.append(0)
                else:
                    row.append(int(c))
            area.append(row)
        areas.append(area)
    return areas


def solver(
    volcanos_map: list[list[list[int]]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for volcano in volcanos_map[:2]:
        total = 0
        destruction: defaultdict[int, int] = defaultdict(int)
        x: int = len(volcano) // 2
        y: int = len(volcano[0]) // 2
        max_r: int = min(x, y)
        for bx in range(-max_r, max_r + 1):
            tx: int = x + bx
            by = int((max_r**2 - (bx**2)) ** 0.5)
            for ty in range(y - by, y + by + 1):
                total += volcano[ty][tx]
                r = ceil(((x - tx) ** 2 + (y - ty) ** 2) ** 0.5)
                destruction[r] += volcano[ty][tx]
        yield total
