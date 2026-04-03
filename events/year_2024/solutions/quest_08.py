"""
Event: The Kingdom of Algorithmia
Quest 8: A Shrine for Nullpointer
"""

from collections import defaultdict
from typing import Iterator, TypeAlias

Config: TypeAlias = tuple[int, int, int, bool, bool]


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[Config]:
    """
    Parse the raw input content into per-part structures.
    """
    nullptr = [0, int(puzzle_input[2]), int(puzzle_input[3])]
    avail = [int(puzzle_input[1]), 20240000, 202400000]
    acol = [1, 1111, 10]
    dyn_thick = [False, True, True]
    empty_spaces = [False, False, True]
    configs: list[Config] = list(
        zip(avail, nullptr, acol, dyn_thick, empty_spaces)
        )
    return configs


def solver(
    n_blocks: list[list[int]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    yield build_tower(*n_blocks[0])
    yield build_tower(*n_blocks[1])
    yield build_tower(*n_blocks[2])


def build_tower(
    avail: int,
    nullptr: int,
    acol: int,
    dyn_thick: int = False,
    empty_spaces: int = False
) -> int:
    """
    Return the computed surplus (or deficit) of blocks after constructing a
    layered tower based on available blocks, optional dynamic thickness,
    empty-space tracking, and modular adjustments.
    """
    blocks = 0
    half_width = width = -1
    thickness = 1
    columns_size: defaultdict[int, int] = defaultdict(int)
    margin: int = acol if empty_spaces else 0

    while blocks < avail:
        half_width += 1
        width: int = 2 * half_width + 1
        blocks += width * thickness

        if empty_spaces:
            for x in range(-half_width, half_width + 1):
                columns_size[x] += thickness
        if dyn_thick:
            thickness: int = (thickness * nullptr) % acol + margin

    empty: int = (nullptr * width) * columns_size[0] % acol
    for x in range(1, half_width):
        empty += 2 * (nullptr * width) * columns_size[x] % acol

    coeff: int = 1 if empty_spaces else width
    return (blocks - empty - avail) * coeff
