"""
Event: Lord of the Wings
Quest: The Phantasmagorithm
"""

from dataclasses import dataclass
from math import inf
from typing import Iterator


@dataclass(unsafe_hash=True)
class Ghost:
    """
    A ghost: its id, position, direction and number of collisions.
    """
    gid: int
    x: int
    y: int
    dx: int
    dy: int
    collisions: int


def preprocessing(
        puzzle_inputs: dict[int, str]
) -> list[tuple[set[tuple[int, int]], set[Ghost]]]:
    """
    Parse each input into a cave: the positions of its walls, and its ghosts,
    numbered in reading order and heading where their arrow points.
    """
    caves: list[tuple[set[tuple[int, int]], set[Ghost]]] = []
    chr_to_dir = {'<': (-1, 0), '^': (0, -1), '>': (1, 0), 'v': (0, 1)}
    for notes in puzzle_inputs.values():
        walls: set[tuple[int, int]] = set()
        ghosts: set[Ghost] = set()
        gid = 1
        for y, line in enumerate(notes.splitlines()):
            for x, c in enumerate(line):
                if c == '#':
                    walls.add((x, y))
                elif c != '.':
                    ghosts.add(Ghost(gid, x, y, *chr_to_dir[c], 0))
                    gid += 1
        caves.append((walls, ghosts))
    return caves


def solver(
        caves: list[tuple[set[tuple[int, int]], set[Ghost]]]
) -> Iterator[int]:
    """
    Yield the total number of collisions of the ghosts of the first cave after
    10 rounds, then the number of rounds before every ghost of the second cave
    has collided 10,000 times.
    """
    _, ghosts = simulate_time(*caves[0], 10)
    yield sum(g.collisions for g in ghosts)
    yield simulate_time(*caves[1])[0]


def simulate_time(
        walls: set[tuple[int, int]], ghosts: set[Ghost], rounds: float = inf
) -> tuple[int, set[Ghost]]:
    """
    Run rounds rounds, or until no ghost is left, and return the number of
    rounds run and the remaining ghosts. Each round, a ghost facing a wall
    turns right, otherwise it moves forward; then ghosts sharing a cell turn
    back. Each turn is a collision, and a ghost leaves at its 10,000th.
    """
    r = 0
    while ghosts and r < rounds:
        for g in ghosts.copy():
            # Move or turn
            nx, ny = (g.x + g.dx, g.y + g.dy)
            if (nx, ny) in walls:
                if g.collisions == 9_999:
                    ghosts.discard(g)
                    continue
                g.collisions += 1
                g.dx, g.dy = -g.dy, g.dx
            else:
                g.x = nx
                g.y = ny
        for g in ghosts:
            if any((g.x, g.y) == (t.x, t.y) for t in ghosts if t != g):
                g.dx *= -1
                g.dy *= -1
                g.collisions += 1
        ghosts = {g for g in ghosts if g.collisions < 10_000}
        r += 1
    return r, ghosts
