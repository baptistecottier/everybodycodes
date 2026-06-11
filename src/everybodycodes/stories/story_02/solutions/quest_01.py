"""
Story: The Entertainment Hub
Quest: Nail Down Your Luck
"""

from itertools import permutations
from typing import Iterator


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[tuple[list[list[bool]], list[list[int]]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[tuple[list[list[bool]], list[list[int]]]] = []

    for note in puzzle_inputs.values():
        _pattern, _token = note.split("\n\n")
        pattern: list[list[bool]] = [
            [c == "*" for c in line] for line in _pattern.splitlines()
        ]
        tokens: list[list[int]] = [
            [{"L": -1, "R": 1}[c] for c in line]
            for line in _token.splitlines()
        ]
        parts_inputs.append((pattern, tokens))
    return parts_inputs


def solver(
    parts_inputs: list[tuple[list[list[bool]], list[list[int]]]]
) -> Iterator[int | str]:
    """
    Solve all puzzle parts for this quest.
    """
    scores = compute_scores(*parts_inputs[0])

    yield sum(max(0, s[i]) for i, s in enumerate(scores))
    scores = compute_scores(*parts_inputs[1])
    yield sum(max(s) for s in scores)
    scores = compute_scores(*parts_inputs[2])

    slots_count = len(scores[0])
    tokens_count = len(scores)
    mins = float("inf")
    maxs = 0
    for perm in permutations(range(slots_count), tokens_count):
        score: int = sum(s[i] for s, i in zip(scores, perm))
        mins = min(mins, score)
        maxs = max(maxs, score)
    yield f"{mins} {maxs}"


def compute_scores(
    pattern: list[list[bool]],
    tokens: list[list[int]]
) -> list[list[int]]:
    """
    Compute scores for tokens falling through a pattern grid based on their
    final positions.
    """
    w: int = len(pattern[0])
    h: int = len(pattern)
    scores: list[list[int]] = []
    for token in tokens:
        token_score: list[int] = []
        for x in range(0, w, 2):
            tkn_idx = 0
            toss_slot: int = x // 2 + 1
            y = -1
            while y < h:
                if pattern[y][x] == 1:
                    t = token[tkn_idx]
                    tkn_idx += 1
                    if x + t > w - 1:
                        x = x - 1
                    elif x + t < 0:
                        x += 1
                    else:
                        x += t
                    y += 1
                else:
                    y += 1
            final_slot = x // 2 + 1
            token_score.append(max(0, final_slot * 2 - toss_slot))
        scores.append(token_score)
    return scores
