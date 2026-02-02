"""
Docstring for year_2024.quest_03.quest_03
"""

from collections import defaultdict


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by double newlines from quest_03.input
    file.
    """
    filename = "quest_03.test" if test_mode else "quest_03.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_input = f.read()
    parts = []
    for _landscape in puzzle_input.split("\n\n---\n\n"):
        _depths = defaultdict(set)
        for _y, _row in enumerate(_landscape.splitlines()):
            for _x, _c in enumerate(_row):
                _depths[int(_c == '#')].add((_x, _y))
        parts.append(_depths)
    return parts


def dig(depths, diagonal: bool = False):
    """
    Simulate moving positions from each depth to the next when all required
    adjacent neighbors are present (optionally including diagonals) and return
    the total weighted depth sum.
    """
    neighbours = {(0, 1), (0, -1), (1, 0), (-1, 0)}
    if diagonal:
        neighbours.update({(1, 1), (1, -1), (-1, 1), (-1, -1)})
    depth = len(depths) - 1
    deeper = True
    while deeper:
        deeper = False
        for (x, y) in depths[depth].copy():
            if all((x + dx, y + dy) in depths[depth].union(depths[depth + 1])
                    for (dx, dy) in neighbours):
                depths[depth].remove((x, y))
                depths[depth + 1].add((x, y))
                deeper = True
        depth += 1
    return sum(k * len(v) for k, v in depths.items())


def solver(test_mode):
    """
    Yield the three part solutions by fetching inputs with
    get_part_input(test_mode) and applying dig to each part (the third part
    uses True).
    """
    parts_input = get_part_input(test_mode)
    yield dig(parts_input[0], False)
    yield dig(parts_input[1], False)
    yield dig(parts_input[2], True)
