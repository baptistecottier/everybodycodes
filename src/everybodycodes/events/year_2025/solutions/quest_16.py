"""
Event: The Song of Ducks and Dragons
Quest: Harmonics of Stone
"""

from math import prod
from typing import Any, Generator


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[list[int]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[int]] = [
        list(map(int, note.split(","))) for note in puzzle_inputs.values()
    ]
    return parts_inputs


def solver(
    pattern_charm_spells: list[list[int]]
) -> Generator[int, Any, None]:
    """
    Solve all puzzle parts for this quest.
    """
    yield sum(build_wall(pattern_charm_spells[0], 90))
    wall: list[int] = pattern_charm_spells[1]
    spells: list[int] = []
    for i, w in enumerate(wall, 1):
        if w != 0:
            for j in range(i - 1, len(wall), i):
                wall[j] -= 1
            spells.append(i)
    yield prod(spells)

    # wall: list[int] = pattern_charm_spells[2]
    # spells = []
    # for i, w in enumerate(wall, 1):
    #     if w != 0:
    #         for j in range(i - 1, len(wall), i):
    #             wall[j] -= 1
    #         spells.append(i)
    # print(spells)
    # cycle_length: int = lcm(*spells)
    # print(len(wall), cycle_length)
    # cycle_wall: list[int] = wall[:cycle_length]
    # cycle_blocks: int = sum(cycle_wall)
    # available = 202_520_252_025_000

    # n_cycle: int = available // cycle_blocks
    # n_columns: int = cycle_length * n_cycle
    # available -= cycle_blocks * n_cycle

    # while available > 0:
    #     available -= cycle_wall.pop(0)
    #     n_columns += 1
    # yield n_columns - 1


def build_wall(
    spell: list[int],
    length: int
) -> list[int]:
    """
    Build a wall by counting divisibility of spell numbers for each position.
    """
    walls: list[int] = [
        sum((n + 1) % s == 0 for s in spell)
        for n in range(length)]
    return walls
