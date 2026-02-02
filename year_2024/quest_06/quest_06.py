"""
Docstring for year_2024.quest_06.quest_06
"""

from collections import defaultdict, deque


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by double newlines from quest_06.input
    file.`
    """
    filename = "quest_06.test" if test_mode else "quest_06.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_inputs = f.read().split("\n\n---\n\n")

    trees = []
    for pi in puzzle_inputs:
        tree = defaultdict(set)
        for line in pi.splitlines():
            parent, children = line.split(':')
            tree[parent] = set(children.split(','))
        trees.append(tree)
    return trees


def solver(test_mode):
    """
    Solver
    """
    parts_input = get_part_input(test_mode)
    yield "".join(most_powerful_fruit(parts_input[0]))
    for part in [2, 3]:
        yield "".join(f[0] for f in most_powerful_fruit(parts_input[part - 1]))


def most_powerful_fruit(tree):
    """
    Return the unique path (as a list of node labels) starting from 'RR' that
    terminates at '@' while ignoring 'BUG' and 'ANT' children, or return an
    empty string if no such unique-length path exists.
    """
    branch_length = defaultdict(list)
    start = 'RR'
    queue = deque([[start]])
    while queue:
        branch = queue.popleft()
        fruit = branch[-1]
        if fruit == '@':
            branch_length[len(branch)].append(branch)
        for child in tree[fruit]:
            if child not in ['BUG', 'ANT']:
                queue.append(branch + [child])
    for _, branches in branch_length.items():
        if len(branches) == 1:
            return branches[0]
    return ""
