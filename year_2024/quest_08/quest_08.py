"""
Docstring for year_2024.quest_08.quest_08
"""

from collections import defaultdict


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by double newlines from quest_08.input
    file.
    """
    filename = "quest_08.test" if test_mode else "quest_08.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_inputs = f.read().split("\n\n---\n\n")
    return [list(map(int, pi.split(','))) for pi in puzzle_inputs]


def solver(test_mode):
    """
    Solver
    """
    parts_input = get_part_input(test_mode)
    yield build_tower(parts_input[0][0])
    yield build_tower(*parts_input[1], dyn_thick=True)
    yield build_tower(*parts_input[2], dyn_thick=True, empty_spaces=True)


def build_tower(avail, nullptr=0, acol=1, dyn_thick=False, empty_spaces=False):
    """
    Return the computed surplus (or deficit) of blocks after constructing a
    layered tower based on available blocks, optional dynamic thickness,
    empty-space tracking, and modular adjustments.
    """
    blocks = 0
    half_width = width = -1
    thickness = 1
    columns_size = defaultdict(int)
    margin = acol if empty_spaces else 0

    while blocks < avail:
        half_width += 1
        width = 2 * half_width + 1
        blocks += width * thickness

        if empty_spaces:
            for x in range(-half_width, half_width + 1):
                columns_size[x] += thickness
        if dyn_thick:
            thickness = (thickness * nullptr) % acol + margin

    empty = (nullptr * width) * columns_size[0] % acol
    for x in range(1, half_width):
        empty += 2 * (nullptr * width) * columns_size[x] % acol

    coeff = 1 if empty_spaces else width
    return (blocks - empty - avail) * coeff
