"""
Event: The Song of Ducks and Dragons
Quest: One Spark to Burn Them All
"""

from collections import deque
from typing import Iterator, TypeAlias

Grid: TypeAlias = list[list[int]]
Coordinates: TypeAlias = set[tuple[int, int]]


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[Grid]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[Grid] = []
    for puzzle_input in puzzle_inputs.values():
        parts_inputs.append(
            [list(map(int, list(line))) for line in puzzle_input.splitlines()]
        )
    return parts_inputs


def solver(
    layouts: list[Grid]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    yield cnt_destroyed_w_n_ignition(layouts[0], 1, {(0, 0)})
    yield cnt_destroyed_w_n_ignition(layouts[1], 2, {(0, 0), (-1, -1)})
    grid = layouts[2]
    yield cnt_destroyed_w_n_ignition(
        grid,
        3,
        {(x, y) for y in range(len(grid)) for x in range(len(grid[0]))}
    )


def ignite(
    grid: Grid,
    seen: Coordinates
) -> Coordinates:
    """
    Spread ignition through grid from seen cells to adjacent cells with lower
    or equal values.
    """
    x, y = 0, 0
    w, h = len(grid[0]), len(grid)
    seen = {(x % w, y % h) for (x, y) in seen}
    queue = deque(seen)
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((-1, 0), (1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in seen:
                continue
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if grid[ny][nx] > grid[y][x]:
                continue
            queue.append((nx, ny))
            seen.add((nx, ny))
    return seen


def cnt_destroyed_w_n_ignition(
    grid: Grid,
    n: int,
    starts: Coordinates
) -> int:
    """
    Find the sum of sizes of the three largest chain reactions when barrels
    are ignited in descending order of their values.
    """
    values: list[Coordinates] = []
    target = 9
    nines = {(x, y) for (x, y) in starts if grid[y][x] == target}

    while starts and nines:
        start = nines.pop()
        if start in starts:
            v = ignite(grid, {start})
            values.append(v)
            starts.difference_update(v)

        while nines == set() and target >= 0:
            target -= 1
            nines = {(x, y) for (x, y) in starts if grid[y][x] == target}

    total = 0
    for _ in range(n):
        exploded = max(values, key=len)
        values = [v.difference(exploded) for v in values]
        total += len(exploded)
    return total
