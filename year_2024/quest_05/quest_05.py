"""
Docstring for year_2024.quest_05.quest_05
"""


from collections import defaultdict


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by double newlines from quest_05.input
    file.
    """
    filename = "quest_05.test" if test_mode else "quest_05.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_input = f.read()
    parts_input = puzzle_input.split("\n\n---\n\n")
    lines = []
    for part_input in parts_input:
        chests = list(map(int, part_input.split()))
        lines.append([chests[i::4] for i in range(4)])
    return lines


def play(columns, max_rounds=0, n_shouts=0):
    """
    Simulate a four-column dancer rotation, tracking seen states and shout
    frequencies, and return either the most frequent shout upon cycle
    detection, the shout at a specified round, or the product of a shout and
    its round when it reaches n_shouts depending on max_rounds and n_shouts.
    """
    positions = set()
    shouts = defaultdict(int)
    rnd = 0

    while True:
        x_idx = (rnd + 1) % 4
        clmn_size = len(columns[x_idx])

        dancer = columns[rnd % 4].pop(0)
        y_idx = (dancer - 1) % (2 * clmn_size)
        if y_idx > clmn_size:
            y_idx = 2 * clmn_size - y_idx

        columns[x_idx].insert(y_idx, dancer)
        shout = int("".join(str(columns[i][0]) for i in range(4)))

        if max_rounds == n_shouts == 0:
            state = f"{"".join(str(c) for clmn in columns for c in clmn)}"
            if state in positions:
                return max(shouts.keys())
            positions.add(state)

        if (rnd := rnd + 1) == max_rounds:
            return shout

        shouts[shout] += 1
        if shouts[shout] == n_shouts:
            return shout * rnd


def solver(test_mode):
    """
    Yield solutions for each puzzle part by fetching inputs for the given
    test_mode and invoking play with the corresponding parameters.
    """
    parts_input = get_part_input(test_mode)
    for part_input, kwargs in zip(
            parts_input,
            ({"max_rounds": 10}, {"n_shouts": 2024}, {})):
        yield play(part_input, **kwargs)
