"""
Event: The Kingdom of Algorithmia
Quest 14: The House of Palms
"""

from typing import Iterator, TypeAlias

Coordinates: TypeAlias = tuple[int, int, int]
Moves: TypeAlias = list[tuple[int, Coordinates]]
GrowthPlan: TypeAlias = list[Moves]


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[GrowthPlan]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_input: list[GrowthPlan] = []
    for part_note in puzzle_input.values():
        part_input: list[Moves] = []
        for line in part_note.splitlines():
            steps: Moves = []
            for step in line.split(','):
                n = int(step[1:])
                match step[0]:
                    case 'R': steps.append((n, (1, 0, 0)))
                    case 'L': steps.append((n, (-1, 0, 0)))
                    case 'F': steps.append((n, (0, 0, 1)))
                    case 'B': steps.append((n, (0, 0, -1)))
                    case 'U': steps.append((n, (0, 1, 0)))
                    case 'D': steps.append((n, (0, -1, 0)))
                    case _: raise ValueError("Invalid input")
            part_input.append(steps)
        parts_input.append(part_input)
    return parts_input


def solver(
    growth_plans: list[GrowthPlan]
) -> Iterator[int]:
    """
    Solves a 3D path-tracing puzzle by tracking visited coordinates and leaf
    positions across multiple input parts.
    """
    segments: list[list[set[Coordinates]]] = []
    for growth_plan in growth_plans:
        visited: set[Coordinates] = set()
        leaves: set[Coordinates] = set()
        for plant in growth_plan:
            x = y = z = 0
            for n, (dx, dy, dz) in plant:
                for _ in range(n):
                    x, y, z = x + dx, y + dy, z + dz
                    visited.add((x, y, z))
            leaves.add((x, y, z))
        segments.append([visited, leaves])
    yield max(y for _, y, _ in segments[0][0])
    yield len(segments[1][0])
    yield min(sum(distance(leaf, (x, y, z), segments[2][0])
                  for leaf in segments[2][1])                        # leaves
              for (x, y, z) in segments[2][0] if x == 0 and z == 0)  # trunk


def distance(
    start: Coordinates,
    end: Coordinates,
    segments: set[Coordinates]
) -> int:
    """
    Calculate the shortest path distance between two points in a 3D grid using
    BFS.
    """
    queue = []
    queue = [(0, start)]
    visited = {start}
    while queue:
        d, (x, y, z) = queue.pop(0)
        if (x, y, z) == end:
            return d
        for tx, ty, tz in ((0, 0, 1), (0, 0, -1), (1, 0, 0),
                           (-1, 0, 0), (0, 1, 0), (0, -1, 0)):
            nx, ny, nz = x + tx, y + ty, z + tz
            if (nx, ny, nz) in visited or (nx, ny, nz) not in segments:
                continue
            queue.append((d + 1, (nx, ny, nz)))
            visited.add((nx, ny, nz))
    raise ValueError("nope")
