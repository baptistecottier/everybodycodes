"""
Docstring for year_2024.quest_07.quest_07
"""

from sympy.utilities.iterables import multiset_permutations


def get_part_input(test_mode: bool):
    """
    Read the test or real input file based on test_mode and return a list of
    (plans, track) tuples where plans map names to tuples of action integers
    and tracks are parsed via get_track.
    """
    filename = "quest_07.test" if test_mode else "quest_07.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_inputs = f.read().split("\n\n---\n\n")
    act_map = {'+': 1, '-': -1, '=': 0, 'S': 0}
    part_inputs = []

    for pi in puzzle_inputs:
        plans = {}
        data = pi.split('\n\n')

        for plan in data[0].splitlines():
            name, actions = plan.split(':')
            plans[name] = tuple(act_map[act] for act in actions.split(','))

        track = get_track(
            "S====\n=====" if len(data) == 1 else data[1])
        part_inputs.append((plans, track))
    return part_inputs


def race(plans, track, max_segment=1_000_000, n_laps=1_000_000):
    """
    Simulate each participant's progression across a circular track by
    applying track modifiers or action plans per segment, accumulating
    'essence' until reaching max_segment steps or n_laps laps, and return a
    dict mapping participants to their total essence.
    """
    ranks = {}
    for p, actions in plans.items():
        power = 10
        essence = lap = seg = 0
        while seg < max_segment and lap < n_laps:
            if track and track[seg % len(track)] != 0:
                power += track[seg % len(track)]
            else:
                power += actions[seg % len(actions)]
            essence += power

            if (seg := seg + 1) % len(track) == 0:
                lap += 1
        ranks[p] = essence
    return ranks


def solver(test_mode):
    """
    Run race simulations from inputs and yield two sorted ranking strings
    followed by the count of winning permutations for the final scenario.
    """
    parts_input = get_part_input(test_mode)

    ranks = race(*parts_input[0], max_segment=10)
    yield "".join(sorted(ranks, reverse=True, key=lambda r: ranks[r]))
    ranks = race(*parts_input[1], n_laps=10)
    yield "".join(sorted(ranks, reverse=True, key=lambda r: ranks[r]))

    # 2024 = len(plan) * 187, so the result after 2024 laps is the same as the
    # one after len(plan) laps
    plans, track = parts_input[2]
    adv_score = race(plans, track, n_laps=11)['A']
    winning = 0
    for plan in multiset_permutations(plans['A']):
        winning += race({'B': plan}, track, n_laps=11)['B'] > adv_score
    yield winning


def get_track(data):
    """
    Return a tuple of integers representing the sequence of actions
    obtained by traversing the ASCII grid in data from the initial position to
    the 'S' cell, where '+' maps to 1, '-' maps to -1, and '='/'S' map to 0.
    """
    grid = [list(d) for d in data.splitlines()]
    act_map = {'+': 1, '-': -1, '=': 0, 'S': 0}
    x, y = 1, 0
    px, py = 0, 0
    track = []
    while grid[y][x] != 'S':
        track.append(act_map[grid[y][x]])
        for tx, ty in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= ty < len(grid) and 0 <= tx < len(grid[ty]):
                if grid[ty][tx] != ' ' and (tx, ty) != (px, py):
                    px, py = x, y
                    x, y = tx, ty
                    break
    track.append(0)  # Corresponding to the action of 'S'
    return tuple(track)
