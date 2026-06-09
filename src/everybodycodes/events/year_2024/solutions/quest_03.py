"""
Event: The Kingdom of Algorithmia
Quest: Mining Maestro
"""

from collections import defaultdict
from collections.abc import Iterator
from typing import TypeAlias

Coords: TypeAlias = set[tuple[int, int]]
Map: TypeAlias = dict[int, Coords]


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[Map]:
    """
    Parse the raw input content into per-part structures.
    """
    parts: list[Map] = []
    for _landscape in puzzle_input.values():
        _depths: defaultdict[int, Coords] = defaultdict(set)
        for _y, _row in enumerate(_landscape.splitlines()):
            for _x, _c in enumerate(_row):
                _depths[int(_c == "#")].add((_x, _y))
        parts.append(_depths)
    return parts


def solver(
    grid_maps: list[dict[int, set[tuple[int, int]]]]
) -> Iterator[int]:
    """
    Yield the three part solutions by fetching inputs with
    get_part_input(content) and applying dig to each part (the third part
    uses True).
    """
    for part, grid in enumerate(grid_maps, 1):
        yield dig(grid, part == 3)


def dig(
    depths: dict[int, set[tuple[int, int]]],
    diagonal: bool = False
) -> int:
    """
    Simulate moving positions from each depth to the next when all required
    adjacent neighbors are present (optionally including diagonals) and return
    the total weighted depth sum.
    """
    neighbours: set[tuple[int, int]] = {(0, 1), (0, -1), (1, 0), (-1, 0)}

    if diagonal:
        neighbours.update({(1, 1), (1, -1), (-1, 1), (-1, -1)})
    depth: int = len(depths) - 1
    candidates: Coords = depths[depth].union(depths[depth + 1])
    deeper: bool = True

    while deeper:
        deeper = False
        for x, y in depths[depth].copy():
            if all((x + dx, y + dy) in candidates for (dx, dy) in neighbours):
                depths[depth].remove((x, y))
                depths[depth + 1].add((x, y))
                deeper = True
        depth += 1
        candidates = depths[depth].union(depths[depth + 1])

    return sum(k * len(v) for k, v in depths.items())
