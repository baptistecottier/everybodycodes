"""
Event: Lord of the Wings
Quest: The Cartograffity
"""

from collections import deque
from collections.abc import Set
from typing import Iterator, NamedTuple

type Cell = tuple[int, int]
type Grid = tuple[set[Cell], int, int]


class ExtraRules(NamedTuple):
    """
    Friendly neighbours to exceed, cells to stay away from, and rounds to grow
    for (negative for no limit).
    """
    threshold: int = 4
    forbidden: Set[Cell] = frozenset()
    rounds: int = -1


def preprocessing(puzzle_input: dict[int, str]) -> list[Grid]:
    """
    Parse each input into its dark cells, width and height.
    """
    grids: list[Grid] = []
    for grid in puzzle_input.values():
        dark_cells: set[Cell] = set()
        lines = grid.splitlines()
        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                if c == '1':
                    dark_cells.add((x, y))
        grids.append((dark_cells, len(lines[0]), len(lines)))
    return grids


def solver(grids: list[Grid]) -> Iterator[int]:
    """
    Yield, for each part, its count on the map built from its own input.
    """
    for i, data in enumerate(grids):
        yield make_map(*data)[i]


def make_map(dark_cells: set[Cell], w: int, h: int) -> tuple[int, int, int]:
    """
    Grow the land from the centre, its sand from the shore and its trees from
    the inner land. Return the number of land, sand and tree cells.
    """
    x = w // 2
    y = h // 2

    land = {(x, y)}
    dark_cells.add((x, y))
    grow(land, dark_cells, land)

    sand = discover(land)
    grow(sand, sand, land)
    land.difference_update(sand)

    extra_nb = {(-1, -2), (0, -2), (1, -2), (-2, -1),
                (2, -1), (-2, 0), (2, 0), (-2, 1),
                (2, 1), (-1, 2),  (0, 2),  (1, 2)}
    trees = discover(land, False, extra_nb)
    grow(trees, trees, land, ExtraRules(3, sand, 2))

    return (len(land) + len(sand), len(sand), len(trees))


def grow(
        items: set[Cell],
        friendly_nb: set[Cell],
        land: set[Cell],
        rules: ExtraRules = ExtraRules()
) -> None:
    """
    Add the cells around items with more than threshold friendly neighbours
    and no forbidden one to items, round by round, until no cell is left to
    check or the rounds are exhausted. New cells only count from the following
    round.
    """
    threshold, forbidden, rounds = rules
    friendly_land = items != land
    nuclear_neigbours = set(
        ((-1, -1), (0, -1), (1, -1), (-1, 0),
         (1, 0), (-1, 1), (0, 1), (1, 1)))
    queue = deque((x + tx, y + ty) for x, y in items
                  for tx, ty in nuclear_neigbours
                  if ((x + tx, y + ty) in land) == friendly_land)
    while queue and rounds != 0:
        rounds -= 1
        new_items: set[Cell] = set()
        for _ in range(len(queue)):
            (x, y) = queue.popleft()
            if (x, y) in items or (x, y) in new_items:
                continue
            neighbours = {(x + tx, y + ty) for tx, ty in nuclear_neigbours}
            if (len(neighbours & friendly_nb) > threshold
                    and not neighbours & forbidden):
                new_items.add((x, y))
                queue.extend(n for n in neighbours
                             if (n in land) == friendly_land)
        items |= new_items
        friendly_nb |= new_items


def discover(
        land: set[Cell],
        expected: bool = True,
        extra_nb: Set[Cell] = frozenset()
) -> set[Cell]:
    """
    Return the land cells that do (expected) or do not touch a non-land cell,
    extra_nb widening the neighbourhood.
    """
    nuclear_neigbours = set(
        ((-1, -1), (0, -1), (1, -1), (-1, 0),
         (1, 0), (-1, 1), (0, 1), (1, 1)))
    all_neighbours = nuclear_neigbours.union(extra_nb)
    items: set[Cell] = set()
    for x, y in land:
        if (any((x + dx, y + dy) not in land for dx, dy in all_neighbours)
                == expected):
            items.add((x, y))
    return items
