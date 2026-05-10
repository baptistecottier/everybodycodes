"""
Event: The Song of Ducks and Dragons
Quest: Definitely Not a Maze
"""

from heapq import heappop, heappush
from typing import Iterator, TypeAlias

Coord: TypeAlias = tuple[int, int]


def preprocessing(
    puzzle_input: dict[int, str],
) -> list[tuple[set[tuple[int, int]], tuple[int, int]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[tuple[set[Coord], Coord]] = []
    for part, note in puzzle_input.items():
        if part == 3:
            continue
        instructions: list[str] = note.split(",")[::-1]
        walls: set[Coord] = set()
        x = y = 0
        dx = 0
        dy = -1
        while instructions:
            data: str = instructions.pop()
            if data[0] == "R":
                dx, dy = -dy, dx
            else:
                dx, dy = dy, -dx
            for _ in range(int(data[1:])):
                x += dx
                y += dy
                walls.add((x, y))
        walls.remove((x, y))
        parts_inputs.append((walls, (x, y)))
    return parts_inputs


def solver(
    instructions: list[tuple[set[tuple[int, int]], tuple[int, int]]],
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for walls, end in instructions:
        x = y = 0
        seen: set[tuple[int, int]] = set()
        queue: list[tuple[int, int, int]] = [(0, x, y)]
        while queue:
            s, x, y = heappop(queue)
            if (x, y) == end:
                yield s
                break
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx: int = x + dx
                ny: int = y + dy
                if (nx, ny) in walls or (nx, ny) in seen:
                    continue
                heappush(queue, (s + 1, nx, ny))
                seen.add((nx, ny))
