"""
Event: The Song of Ducks and Dragons
Quest: Feast on the Board
"""

from typing import Iterator, TypeAlias

Position: TypeAlias = tuple[int, int]


def preprocessing(
    puzzle_inputs: dict[int, str],
) -> list[tuple[set[Position], set[Position], set[Position], int, int]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[
        tuple[set[Position], set[Position], set[Position], int, int]
    ] = []
    for puzzle_input in puzzle_inputs.values():
        parts_inputs.append(map_details(puzzle_input))
    return parts_inputs


def solver(
    grids: list[tuple[set[Position], set[Position], set[Position], int, int]],
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    dragons, sheeps, _, _, _ = grids[0]
    for _ in range(3 + (len(sheeps) > 50)):
        dragons = {
            (x + dx, y + dy)
            for (x, y) in dragons
            for dx, dy in [
                (0, 0),
                (1, 2),
                (1, -2),
                (-1, 2),
                (-1, -2),
                (2, 1),
                (2, -1),
                (-2, 1),
                (-2, -1),
            ]
        }
    yield len(sheeps.intersection(dragons))
    dragons, sheeps, hideouts, w, h = grids[1]
    n_sheeps: int = len(sheeps)
    for _ in range(3 + 17 * (len(sheeps) > 50)):
        dragons = {
            (x + dx, y + dy)
            for (x, y) in dragons
            for dx, dy in [
                (1, 2),
                (1, -2),
                (-1, 2),
                (-1, -2),
                (2, 1),
                (2, -1),
                (-2, 1),
                (-2, -1),
            ]
            if (0 <= x + dx <= w and 0 <= y + dy <= h)
        }

        new_sheeps: set[Position] = {
            s for s in sheeps if (s not in dragons) or (s in hideouts)
        }
        new_sheeps = {(x, y + 1) for (x, y) in new_sheeps}
        sheeps = {s for s in new_sheeps if s not in dragons or s in hideouts}
    yield n_sheeps - len(sheeps)


def map_details(
    puzzle_input: str,
) -> tuple[set[Position], set[Position], set[Position], int, int]:
    """
    Extract dragon and sheep positions from the map.
    """
    dragons: set[Position] = set()
    sheeps: set[Position] = set()
    hideouts: set[Position] = set()
    x = y = 0
    for y, line in enumerate(puzzle_input.splitlines()):
        for x, c in enumerate(line):
            if c == "S":
                sheeps.add((x, y))
            if c == "D":
                dragons.add((x, y))
            if c == "#":
                hideouts.add((x, y))
    return dragons, sheeps, hideouts, x, y
