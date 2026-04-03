"""
Event: The Kingdom of Algorithmia
Quest 13: Never Gonna Let You Down
"""

import heapq
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator, TypeAlias

Coord: TypeAlias = tuple[int, int]


@dataclass
class Chamber:
    """
    A Chamber represents a maze structure with entry and exit points.
    Attributes:
        maze (dict[Coord, int]): A dictionary mapping coordinates to their
        corresponding values or states within the maze.
        entries (Coord): The coordinate representing the entry point to the
        chamber.
        exit (Coord): The coordinate representing the exit point from the
        chamber.
    """
    maze: dict[Coord, int]
    exits: set[Coord]
    start: Coord


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[Chamber]:
    """
    Parse the raw input content into per-part structures.
    """
    maps: list[Chamber] = []
    for note in puzzle_input.values():
        doors: dict[Coord, int] = {}
        starts: set[Coord] = set()
        end: Coord = (0, 0)
        lines: list[str] = note.splitlines()
        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                if c.isdigit():
                    doors[(x, y)] = int(c)
                elif c == 'S':
                    starts.add((x, y))
                    doors[(x, y)] = 0
                elif c == 'E':
                    end: tuple[int, int] = (x, y)
                    doors[(x, y)] = 0
        maps.append(Chamber(doors, starts, end))
    return maps


def solver(
    chambers: list[Chamber]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for chamber in chambers:
        start = chamber.start
        exits = chamber.exits
        maze = chamber.maze

        queue: list[tuple[int, Coord]] = []
        heapq.heappush(queue, (0, start))
        visited: defaultdict[Coord, float] = defaultdict(lambda: float('inf'))
        visited[start] = 0
        while queue:
            t, (x, y) = heapq.heappop(queue)

            if (x, y) in exits:
                yield t
                break

            for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0)):
                npos = (x + dx, y + dy)

                if npos not in maze:
                    continue
                nt: int = t + 1 + min(
                    (maze[npos] - maze[(x, y)]) % 10,
                    (maze[(x, y)] - maze[npos]) % 10
                )

                if npos in visited:
                    if visited[npos] <= nt:
                        continue
                heapq.heappush(queue, (nt, npos))
                visited[npos] = nt
