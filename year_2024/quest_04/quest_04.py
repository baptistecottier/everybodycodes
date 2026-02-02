"""
Docstring for year_2024.quest_04.quest_04
"""

from statistics import median


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by --- from quest_04.input
    file.
    """
    filename = "quest_04.test" if test_mode else "quest_04.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_input = f.read()
    return [list(map(int, _nails.strip().splitlines()))
            for _nails in puzzle_input.split("---")]


def hammer_strikes(nails, f):
    """
    Return the total number of strikes required to move each nail to the
    integer target produced by applying f to the nails.
    """
    target = int(f(nails))
    return sum(abs(nail - target) for nail in nails)


def solver(test_mode):
    """
    Yield three aggregated hammer_strikes results for the input parts,
    using min for the first two parts and median for the third.
    """
    parts_input = get_part_input(test_mode)
    for part_input, f in zip(parts_input, (min, min, median)):
        yield hammer_strikes(part_input, f)
