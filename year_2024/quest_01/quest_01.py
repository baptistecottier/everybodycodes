
"""
Docstring for year_2024.quest_01.quest_01
"""


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by --- from quest_01.input
    file.
    """
    filename = "quest_01.test" if test_mode else "quest_01.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_input = f.read()
    return [part.strip() for part in puzzle_input.split("---")]


def count_potions(creatures, level):
    """
    Calculate the total number of potions needed to defeat groups of creatures
    based on their types
    and group level.
    """
    cost = {'A': 0, 'B': 1, 'C': 3, 'D': 5, 'x': 0}
    potions = 0
    for i in range(0, len(creatures), level):
        group = creatures[i: i + level]
        potions += sum(cost[g] for g in group)
        x_count = group.count('x')
        if x_count == level - 3:
            potions += 6
        elif x_count == level - 2:
            potions += 2

    return potions


def solver(test_mode):
    """
    Yield the solution for each part by retrieving inputs with
    get_part_input(test_mode) and applying count_potions to each part's input.
    """
    parts_input = get_part_input(test_mode)
    for part, part_input in enumerate(parts_input, 1):
        yield count_potions(part_input, part)
