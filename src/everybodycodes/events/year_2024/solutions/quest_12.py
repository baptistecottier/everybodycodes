"""
Event: The Kingdom of Algorithmia
Quest: Desert Shower
"""

from typing import Iterator, TypeAlias

Targets: TypeAlias = list[tuple[int, int]]


def preprocessing(puzzle_input: dict[int, str]) -> list[Targets]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_input: list[Targets] = []
    for note in puzzle_input.values():
        list_targets: Targets = []
        lines: list[str] = note.splitlines()
        if "." in note:
            for y, line in enumerate(lines[::-1][1:]):
                for x, c in enumerate(line[1:]):
                    if c == "T":
                        list_targets.append((x, y))
                    if c == "H":
                        list_targets.append((x, y))
                        list_targets.append((x, y))
        else:
            for _coord in lines:
                coord = _coord.split()
                list_targets.append((int(coord[0]), int(coord[1])))
        parts_input.append(list_targets)
    return parts_input


def solver(list_targets: list[Targets]) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for targets in list_targets[:2]:
        ranking_value = 0
        for x, y in targets:
            ranking_value += ((x + y) // 3) * (1 + (y + x) % 3)
        yield ranking_value
