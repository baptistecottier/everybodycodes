"""
Docstring for year_2024.quest_12.quest_12
"""


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by double newlines from quest_12.input
    file.
    """
    filename = "quest_12.test" if test_mode else "quest_12.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_inputs = f.read().split("\n\n---\n\n")
    parts_input = []
    for note in puzzle_inputs:
        T = []
        lines = note.splitlines()
        if '.' in note:
            for y, line in enumerate(lines[::-1][1:]):
                for x, c in enumerate(line[1:]):
                    if c == 'T':
                        T.append((x, y))
                    if c == 'H':
                        T.append((x, y))
                        T.append((x, y))
        else:
            for coord in lines:
                T.append(tuple(map(int, coord.split())))
        parts_input.append(T)
    return parts_input


def solver(test_mode):
    """
    Solver
    """
    parts_input = get_part_input(test_mode)
    for T in parts_input[:2]:
        ranking_value = 0
        for x, y in T:
            ranking_value += ((x + y) // 3) * (1 + (y + x) % 3)
        yield ranking_value
