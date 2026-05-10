"""
Event: The Kingdom of Algorithmia
Quest: From the Herbalist's Diary
"""

from typing import Iterator, TypeAlias

Coords: TypeAlias = tuple[int, int]
Herbs: TypeAlias = dict[Coords, str]


def preprocessing(puzzle_input: dict[int, str]) -> list[tuple[set[Coords], Herbs]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_input: list[tuple[set[Coords], Herbs]] = []
    for note in puzzle_input.values():
        terrain: set[Coords] = set()
        herbs: Herbs = {}
        for y, line in enumerate(note.splitlines()):
            for x, c in enumerate(line):
                if c == ".":
                    terrain.add((x, y))
                if c.isalpha():
                    herbs[(x, y)] = c
                    terrain.add((x, y))
        parts_input.append((terrain, herbs))
    return parts_input


def solver(herb_maps: list[tuple[set[Coords], Herbs]]) -> Iterator[int]:
    """
    Solves the puzzle by finding entry point and collecting herbs from each
    terrain.
    """
    for terrain, herbs in herb_maps[:2]:
        entry = {(x, y) for (x, y) in terrain if y == 0}.pop()
        yield collect_herbs(terrain, herbs, entry, entry)
    yield len(herb_maps)


def collect_herbs(
    terrain: set[Coords], herbs: Herbs, start: Coords, end: Coords
) -> int:
    """
    Find the shortest path from start to end while collecting all required
    herbs.
    """
    collected: str = "".join(set(herbs.values()))
    visited: set[tuple[str, int, int]] = set()
    queue = [(0, collected, start)]
    while queue:
        (d, c, (x, y)) = queue.pop(0)
        if (x, y) in herbs:
            c = c.replace(herbs[(x, y)], "", 1)
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x + dx, y + dy
            if (nx, ny) == end and c == "":
                return d + 1
            if (c, nx, ny) in visited or (nx, ny) not in terrain:
                continue
            queue.append((d + 1, c, (nx, ny)))
            visited.add((c, nx, ny))
    return -1
