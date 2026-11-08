"""
Event: Lord of the Wings
Quest: The Entgineering
"""

from math import inf
from typing import Iterator


def preprocessing(
        puzzle_inputs: dict[int, str]
) -> list[dict[tuple[float, int], int]]:
    """
    Parse each input into a grid mapping the position of each digit to its
    height, two consecutive characters being half a unit apart.
    """
    grids: list[dict[tuple[float, int], int]] = []
    for notes in puzzle_inputs.values():
        heights: dict[tuple[float, int], int] = {}
        for y, line in enumerate(notes.splitlines()):
            for k, h in enumerate(line):
                if h != '.':
                    heights[(k * .5, y)] = int(h)
        grids.append(heights)

    return grids


def solver(grids: list[dict[tuple[float, int], int]]) -> Iterator[int]:
    """
    Yield the energy gathered in 1 round on the first grid and in 6 rounds on
    the second, then on the third grid, where hit cells grow, until 100,000
    cells have reached a height of 10.
    """
    yield count_energy(grids[0], rounds=1)
    yield count_energy(grids[1], rounds=6)
    yield count_energy(grids[2], warriors=100_000)


def count_energy(
        grid: dict[tuple[float, int], int],
        rounds: float = inf,
        warriors: float = inf
) -> int:
    """
    Return the energy gathered in rounds rounds, or until warriors cells have
    reached a height of 10. Each round, a line starts from every cell on one
    edge of the grid, in the direction r % 6, and gathers one energy from
    every cell at least as high as the height it carries, which drops by one
    at each step and is raised by higher cells. Cells below 1 grow by one
    instead. With a number of warriors, every hit cell grows by one, and a
    cell reaching 10 falls back to -2.
    """
    grow = int(warriors != inf)
    energy = 0
    direction = [(.5, 1), (-.5, 1), (-1, 0), (-.5, -1), (.5, -1), (1, 0)]
    r = 0
    while r < rounds and warriors > 0:
        dx, dy = direction[r % 6]
        entry_points = set(grid.keys())
        for x, y in entry_points.copy():
            if (x - dx, y - dy) in grid.keys():
                entry_points.remove((x, y))

        for (x, y) in entry_points:
            if grid[(x, y)] > 0:
                energy += 1

            h = grid[(x, y)]
            grid[(x, y)] += grow
            if grid[(x, y)] == 10:
                grid[(x, y)] = -2
                warriors -= 1

            while (x + dx, y + dy) in grid:
                x += dx
                y += dy
                temp = grid[(x, y)]

                if grid[(x, y)] < 1:
                    grid[(x, y)] += 1

                elif grid[(x, y)] > h - 1:
                    energy += 1
                    grid[(x, y)] += grow
                    if grid[(x, y)] == 10:
                        grid[(x, y)] = -2
                        warriors -= 1
                h = max(h - 1, temp)
        r += 1
    return energy
