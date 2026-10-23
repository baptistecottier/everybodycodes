"""
Story: The Digital Atelier
"""

from collections import deque
from typing import Iterator, TypeAlias

Position: TypeAlias = tuple[int, int]
LaunchPlan: TypeAlias = tuple[list[Position], list[int]]


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[LaunchPlan]:
    """
    Parse each part into the four places (start, then beacons A, B and C) and
    the list of moves, as beacon indices.
    """
    launch_plans: list[LaunchPlan] = []
    for data in puzzle_input.values():
        lines = data.splitlines()
        places: list[Position] = []
        for line in lines[:4]:
            x, y = map(int, line.split("[")[1][:-1].split(","))
            places.append((x, y))
        moves: list[int] = []
        if len(lines) > 4:
            moves = [ord(p) - 64 for p in lines[-1].split("=")[1]]
        launch_plans.append((places, moves))
    return launch_plans


def solver(
    launch_plans: list[LaunchPlan]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for part, (places, moves) in enumerate(launch_plans):
        x, y = places[0]
        illuminated: set[Position] = {(x, y)}
        for m in moves:
            nx, ny = places[m]
            x = (x + nx) // 2
            y = (y + ny) // 2
            illuminated.add((x, y))
        if len(illuminated) == 1:
            random_moves(illuminated, places)
        fireflies: set[Position] = set()
        for x, y in illuminated:
            fireflies.update(
                {(x - 1, y), (x + 1, y), (x, y), (x, y - 1), (x, y + 1)})
        if part == 0:
            yield len(illuminated)
        else:
            yield len(fireflies) - len(illuminated)


def random_moves(
    illuminated: set[Position],
    places: list[Position]
) -> None:
    """
    Illuminate every position reachable from the start with any sequence of
    moves towards the three beacons.
    """
    queue: deque[Position] = deque([places[0]])
    while queue:
        x, y = queue.pop()
        for nx, ny in places[1:4]:
            target = ((x + nx) // 2, (y + ny) // 2)
            if target not in illuminated:
                illuminated.add(target)
                queue.append(target)
