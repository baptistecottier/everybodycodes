"""
Event: Lord of the Wings
Quest: The Coneservation
"""

from typing import Callable, Iterator


def preprocessing(puzzle_input: dict[int, str]) -> list[list[int]]:
    """
    Parse the raw input content into per-part sorted lists of pines.
    """
    pines_set: list[list[int]] = []
    for pines_txt in puzzle_input.values():
        pines_set.append(sorted(list(map(int, pines_txt.split(',')))))
    return pines_set


def solver(pines_set: list[list[int]]) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    yield compute_missing_pines(pines_set.pop(0), 1, 1, lambda x: x * x)
    yield compute_missing_pines(pines_set.pop(0), 3, 1, lambda x: 4 * (x - 1))
    yield compute_missing_pines(pines_set.pop(0), 3, 2, lambda x: x * x - 1)


def compute_missing_pines(
        pines: list[int],
        size: int,
        incr_size: int,
        f: Callable[[int], int]
) -> int:
    """
    Count the pines to add to bring each value up to f(size), growing
    size by incr_size whenever a value exceeds the formation size.
    """
    formation_size: int = f(size)
    to_add: int = 0
    pines.append(-1)
    pine = pines.pop(0)
    while pine != -1:
        if formation_size >= pine:
            to_add += formation_size - pine
            pine = pines.pop(0)
        else:
            size += incr_size
            formation_size = f(size)
    return to_add
