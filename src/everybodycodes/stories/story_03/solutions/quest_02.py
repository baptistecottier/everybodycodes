"""
Story: Melody Made of Code
Quest: How Quack Echoes Back
"""

from collections import deque
from typing import Iterator, TypeAlias

Position: TypeAlias = tuple[int, int]


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[tuple[Position, set[Position]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[tuple[Position, set[Position]]] = []
    for pi in puzzle_inputs.values():
        start: tuple[int, int] = (-1, -1)
        obstacles: set[Position] = set()
        for y, line in enumerate(pi.splitlines()):
            for x, c in enumerate(line):
                if c == "#":
                    obstacles.add((x, y))
                if c == "@":
                    start = (x, y)
        expand_obstacles(deque(obstacles.copy()), obstacles)
        parts_inputs.append((start, obstacles))
    return parts_inputs


def solver(
    flight_maps: list[tuple[Position, set[Position]]]
) -> Iterator[int]:
    """
    Solves each part by propagating an air stream through obstacles and
    yielding the visited positions.
    """
    # for start, obstacles in flight_maps:
    yield air_stream_propagation(set(), *flight_maps[0], 1)

    start, obstacles = flight_maps[1]
    yield air_stream_propagation(obstacles, start, neighbours(obstacles), 1)

    start, obstacles = flight_maps[2]
    yield air_stream_propagation(obstacles, start, neighbours(obstacles), 3)


def neighbours(
    points: set[Position]
) -> set[tuple[int, int]]:
    """
    Return the set of all orthogonal neighbors for each point in the input set.
    """
    return {
        (x + dx, y + dy)
        for (x, y) in points
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
    }


def air_stream_propagation(
    obstacles: set[Position],
    start: Position,
    to_reach: set[Position],
    rep: int
) -> int:
    """
    Simulates air stream propagation from a starting point, expanding
    obstacles and counting steps until all target positions are reached.
    """
    x, y = start
    obstacles.add((x, y))
    steps = 0
    sequence = (
        ((0, -1),) * rep + ((1, 0),) * rep +
        ((0, 1),) * rep + ((-1, 0),) * rep
    )
    x, y = start
    i = -1

    while not to_reach <= obstacles:
        i = (i + 1) % len(sequence)
        dx, dy = sequence[i]
        while (x + dx, y + dy) in obstacles:
            i = (i + 1) % len(sequence)
            dx, dy = sequence[i]
        x, y = x + dx, y + dy
        obstacles.add((x, y))
        expand_obstacles(deque([(x, y)]), obstacles)
        steps += 1

    return steps


def expand_obstacles(
    to_expand: deque[Position],
    obstacles: set[Position]
) -> None:
    """
    Expands a region by exploring adjacent cells and filling enclosed areas,
    updating obstacles as new boundaries are discovered.
    """
    seen = obstacles.copy()
    while to_expand:
        (x, y) = to_expand.popleft()
        for ux, uy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if (x + ux, y + uy) in seen:
                continue
            seen.add((x + ux, y + uy))
            surronded, new_obstacles = fill((x + ux, y + uy), obstacles.copy())
            if surronded:
                for pos in new_obstacles - obstacles:
                    if pos not in seen:
                        to_expand.append(pos)
                obstacles.update(new_obstacles)


def fill(
    pos: Position,
    seen: set[Position]
):
    """
    Performs a flood fill from a starting position, expanding up to 200
    cells and returning whether the region is smaller than the limit.
    """
    x, y = pos
    queue = deque(set([pos]))
    init: int = len(seen)
    seen.add((x, y))
    while queue and (len(seen) < init + 200):
        (x, y) = queue.popleft()
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if (x + dx, y + dy) in seen:
                continue
            seen.add((x + dx, y + dy))
            queue.append((x + dx, y + dy))
    return (len(seen) - init) < 200, seen
