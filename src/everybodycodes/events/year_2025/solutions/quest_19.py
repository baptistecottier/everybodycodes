"""
Event: The Song of Ducks and Dragons
Quest: Flappy Quack
"""

from collections import defaultdict
from typing import Iterator


def preprocessing(puzzle_inputs: dict[int, str]):
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[tuple[int, ...]]] = []
    for puzzle_input in puzzle_inputs.values():
        values: list[tuple[int, ...]] = [
            tuple(map(int, n.split(","))) for n in puzzle_input.splitlines()
        ]
        parts_inputs.append(values)
    return parts_inputs


def solver(chambers: list[list[tuple[int, ...]]]) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for chamber in chambers:
        yield min_flaps(chamber)


def min_flaps(chambre: list[tuple[int, ...]]):
    """
    Calculate the minimum number of flaps needed to navigate through a series
    of passages by finding a valid position that stays within all opening
    constraints.
    """
    openings: defaultdict[int, list[tuple[int, ...]]] = defaultdict(list)

    x = 0
    for x, start, size in chambre:
        openings[x].append((start, start + size - 1))

    y_min = y_max = 0

    for dx in range(1, x + 1):
        y_min = max(0, y_min - 1)
        y_max = min(x, y_max + 1)

        if dx in openings:
            y_min = max(y_min, min(a for a, _ in openings[dx]))
            y_max = min(y_min, max(b for _, b in openings[dx]))

    return (y_min + y_min % 2 + x) // 2
