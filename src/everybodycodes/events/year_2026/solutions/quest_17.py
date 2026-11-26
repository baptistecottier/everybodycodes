"""
Event: Lord of the Wings
Quest: The Lavairynth
"""

from collections import deque
from collections.abc import Iterator


def preprocessing(puzzle_inputs: dict[int, str]) -> list[list[str]]:
    """
    Parse each input into the lines of its field.
    """
    return [
        field.splitlines() for field in puzzle_inputs.values()
    ]


def solver(lava_fields: list[list[str]]) -> Iterator[int]:
    """
    Yield the length of the path from the top-left to the bottom-right corner
    of the first field, moving from cell to adjacent '#' cells, then twice one
    more than the number of '#' cells of the second field.
    """
    x, y = 0, 0
    queue = deque([(0, 0, 0)])
    lf = lava_fields[0]
    w = len(lf[0]) - 1
    h = len(lf) - 1
    visited = {(0, 0)}
    while queue:
        x, y, d = queue.pop()
        if (x, y) == (w, h):
            yield d
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if (nx, ny) in visited:
                continue
            if not (0 <= nx <= w and 0 <= ny <= h):
                continue
            if lf[ny][nx] == '#':
                queue.appendleft((nx, ny, d + 1))
                visited.add((nx, ny))

    yield 2 * (1 + sum(line.count('#') for line in lava_fields[1]))
