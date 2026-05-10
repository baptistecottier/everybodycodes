"""
Event: The Song of Ducks and Dragons
Quest: Dream in Triangles
"""

from collections import defaultdict, deque
from typing import Iterator, TypeAlias

Position: TypeAlias = tuple[int, int]


def preprocessing(puzzle_inputs: dict[int, str]) -> list[list[str]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[str]] = []
    for puzzle_input in puzzle_inputs.values():
        parts_inputs.append(puzzle_input.splitlines())
    return parts_inputs


def solver(map_sections: list[list[str]]) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    neighbours = maze_neighbours(map_sections[0])
    yield sum(len(v) for v in neighbours.values()) // 2

    maze = map_sections[1]
    neighbours = maze_neighbours(maze)
    end = None
    for y, line in enumerate(maze):
        if "E" in line:
            end = (line.index("E"), y)
            break
    start = (maze[-1].index("S"), len(maze) - 1)

    queue = deque([(*start, 0)])
    seen: set[Position] = set()
    while queue:
        x, y, jumps = queue.popleft()
        if (x, y) == end:
            yield jumps
            break
        for nx, ny in neighbours[(x, y)]:
            if (nx, ny) in seen:
                continue
            queue.append((nx, ny, jumps + 1))
            seen.add((nx, ny))


def maze_neighbours(maze: list[str]):
    """
    Build adjacency graph of maze coordinates connected by 'T' tiles.
    """
    neighbours: defaultdict[Position, set[Position]] = defaultdict(set)
    for y, line in enumerate(maze):
        for x, t in enumerate(line):
            if t in ".#":
                continue
            if x < len(line) - 1 and line[x + 1] in "SET":
                neighbours[(x, y)].add((x + 1, y))
                neighbours[(x + 1, y)].add((x, y))
            if y < len(maze) - 1 and ((x + y) % 2 == 1) and maze[y + 1][x] in "SET":
                neighbours[(x, y)].add((x, y + 1))
                neighbours[(x, y + 1)].add((x, y))
    return neighbours
