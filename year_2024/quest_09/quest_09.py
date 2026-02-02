"""
Docstring for year_2024.quest_09.quest_09
"""


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by double newlines from quest_09.input
    file.
    """
    filename = "quest_09.test" if test_mode else "quest_09.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_inputs = f.read().split("\n\n---\n\n")
    return [list(map(int, part.splitlines())) for part in puzzle_inputs]


def solver(test_mode):
    """
    Solver
    """
    dots = [1, 3, 5, 10, 15, 16, 20, 24, 25, 30,
            37, 38, 49, 50, 74, 75, 100, 101]
    parts_input = get_part_input(test_mode)
    for part, sbs in enumerate(parts_input):
        yield get_min_beetles(sbs, dots[:[4, 10, 18][part]])


def get_min_beetles(sparkballs, dots):
    """
    Calculate the minimum number of beetles needed to collect exactly
    sparkballs using dynamic programming.
    """
    max_sb = max(sparkballs)

    beetles = [float('inf')] * (max_sb + 1)
    beetles[0] = 0

    for i in range(1, max_sb + 1):
        beetles[i] = min(1 + beetles[i - dot] for dot in dots if i >= dot)

    total_beetles = 0
    for sb in sparkballs:

        if sb > 50_000:
            min_beetles = sb
            for delta in range(0, 51):
                lhs = sb // 2 - delta + sb % 2
                rhs = sb - lhs
                min_beetles = min(
                    beetles[lhs] + beetles[rhs], min_beetles)
            total_beetles += min_beetles

        else:
            total_beetles += beetles[sb]

    return total_beetles
