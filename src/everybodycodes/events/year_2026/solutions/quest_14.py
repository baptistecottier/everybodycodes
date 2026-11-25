"""
Everybody Codes - 2026 - Quest 14
https://everybody.codes/event/2026/quests
"""


from typing import Iterator


def preprocessing(puzzle_inputs: dict[int, str]) -> list[list[str]]:
    """
    Parse each input into the lines of its grid.
    """
    return [
        note.splitlines() for note in puzzle_inputs.values()
    ]


def solver(notes: list[list[str]]) -> Iterator[int]:
    """
    Yield, for each grid, the number of bindings needed to bind every pair
    of adjacent pieces and the outer edges of the grid.
    """
    for grid in notes:
        w = len(grid[0])
        h = len(grid)
        bindings = 2 * (w + h)
        for x in range(w):
            for y in range(h - 1):
                bindings += grid[y][x] != grid[y + 1][x]

        for y in range(h):
            for x in range(w - 1):
                bindings += grid[y][x] != grid[y][x + 1]

        yield bindings
