"""
Docstring for year_2024.quest_10.quest_10
"""

from itertools import product


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by double newlines from quest_10.input
    file.
    """
    filename = "quest_10.test" if test_mode else "quest_10.input"
    with open(filename, encoding="utf-8") as f:
        puzzle_inputs = f.read().split("\n\n---\n\n")
    parts_input = []
    for part, part_input in enumerate(puzzle_inputs, 1):
        samples = extract_samples(part_input, part == 3)
        parts_input.append((samples, 7, 7))
    return parts_input


def solver(test_mode):
    """
    Solver
    """
    parts_input = get_part_input(test_mode)
    total_words = []
    for part_input in parts_input[:2]:
        pos, w, h = part_input
        words = []
        for pos_x, pos_y in pos:
            word = compute_runic_word(pos_x, pos_y, w, h)
            words.append(word)
        total_words.append(words)
    yield total_words[0][0]
    yield sum(sum(i * (ord(c) - 64) for i, c in enumerate(word, 1)) for word in total_words[1])


def extract_samples(note, adjacent=False):
    samples = []
    h = w = 7
    delta = -1 if adjacent else 2
    lines = note.splitlines()
    _samples_row = []
    for d in range(0, len(lines) - 2, h + delta):
        for i in range(0, len(lines[0]) - 2, w + delta):
            _samples_row.append([lines[y][i:i+8] for y in range(d, d+8)])

    for sample in _samples_row:
        pos_x = {y: {sample[y][dx] for dx in [0, 1, 6, 7] if sample[y][dx] != '?'} for y in range(2, 6)}
        pos_y = {x: {sample[dy][x] for dy in [0, 1, 6, 7] if sample[dy][x] != '?'} for x in range(2, 6)}
        samples.append((pos_x, pos_y))
    return samples


def compute_runic_word(pos_x, pos_y, w, h):
    word = ['?'for _ in range(16)]
    for y, x in product(range(2, 6), range(2, 6)):
        for tx in pos_y[x]:
            if tx == '?':
                continue
            if tx in pos_x[y]:
                word[(w - 3) * (y - 2) + x - 2] = tx
                pos_y[x].remove(tx)
                pos_x[y].remove(tx)
                break
    return "".join(word)
