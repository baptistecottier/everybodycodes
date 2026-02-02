"""
Docstring for year_2024.quest_11.quest_11
"""


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by double newlines from quest_11.input
    file.
    """
    filename = "quest_11.test" if test_mode else "quest_11.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_inputs = f.read().split("\n\n---\n\n")
    parts_input = []
    for part_input in puzzle_inputs:
        notes = {}
        for line in part_input.splitlines():
            src, dst = line.split(':')
            notes[src] = dst.split(',')
        parts_input.append(notes)
    return parts_input


def solver(test_mode):
    """
    Solves termite population puzzles by calculating growth after specified
    days and finding population differences.
    """
    parts_input = get_part_input(test_mode)
    for conversion, start, n_days in zip(parts_input[:2], 'AZ', [4, 10]):
        yield count_termite_after_n_days(conversion, start, n_days)

    conversion = parts_input[2]
    counts = sorted(count_termite_after_n_days(conversion, start, 20)
                    for start in conversion.keys())
    yield counts[-1] - counts[0]


def count_termite_after_n_days(conversion, start, n_days):
    population = {termite: int(termite == start) for termite in conversion}
    for _ in range(n_days):
        new_population = {termite: 0 for termite in population}
        for k, v in conversion.items():
            for t in v:
                new_population[t] += population[k]
        population = new_population
    return sum(population.values())
