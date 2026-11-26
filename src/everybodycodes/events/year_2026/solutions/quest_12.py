"""
Event: Lord of the Wings
Quest: The Castastrophe
"""

from collections import defaultdict
from collections.abc import Iterator


def preprocessing(
        puzzle_inputs: dict[int, str]
) -> list[list[list[tuple[int, int]]]]:
    """
    Parse each input into its grid and list the regions of '#' cells it
    contains.
    """
    return [
        get_regions([list(line) for line in grid.splitlines()])
        for grid in puzzle_inputs.values()
    ]


def get_regions(grid: list[list[str]]) -> list[list[tuple[int, int]]]:
    """
    Return the regions of '#' cells of the grid, each one as the sorted list
    of the (x, y) coordinates of its cells. Cells next to each other
    horizontally or vertically belong to the same region. Visited cells are
    replaced with '.' in the grid.
    """
    w = len(grid[0])
    h = len(grid)
    ry = 0
    regions: list[list[tuple[int, int]]] = []
    while ry < h:
        while '#' not in grid[ry]:
            ry += 1
            if ry == h:
                return regions
        rx = grid[ry].index('#')
        region = {(rx, ry)}
        grid[ry][rx] = '.'
        queue = [(rx, ry)]
        while queue:
            x, y = queue.pop(0)
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)):
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if grid[ny][nx] == '#':
                    region.add((nx, ny))
                    grid[ny][nx] = '.'
                    queue.append((nx, ny))
        regions.append(sorted(region))
    return regions


def solver(stacks: list[list[list[tuple[int, int]]]]) -> Iterator[int]:
    """
    Yield, for each grid, the sum over its regions of a score computed from
    the width and the height of the region and from the fewest cells found
    in one of its rows and in one of its columns.
    """
    for regions in stacks:
        spells = 0
        for region in regions:
            w = region[-1][0] - region[0][0] + 1
            max_y = max(y for _, y in region)
            min_y = min(y for _, y in region)
            h = max_y - min_y + 1
            ys: defaultdict[int, int] = defaultdict(int)
            xs: defaultdict[int, int] = defaultdict(int)
            for x, y in region:
                ys[y] += 1
                xs[x] += 1
            dx = w - min(ys.values())
            dy = h - min(xs.values())
            spells += min(w, h, h - dy + w - dx)
        yield spells
