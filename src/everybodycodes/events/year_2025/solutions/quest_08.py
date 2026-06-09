"""
Event: The Song of Ducks and Dragons
Quest: The Art of Connection
"""

from collections import defaultdict
from typing import Iterator


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[list[int]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[int]] = [
        list(map(int, note.split(","))) for note in puzzle_input.values()
    ]
    return parts_inputs


def solver(
    nails_sequences: list[list[int]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for part, sequence in enumerate(nails_sequences, 1):
        n_nails: int = max(sequence)
        cnt = 0
        if part == 1:
            for i, n in enumerate(sequence[:-1]):
                if abs(n - sequence[i + 1]) == n_nails // 2:
                    cnt += 1
            yield cnt
        if part == 2:
            yield count_knots(sequence, 0)
        if part == 3:
            yield count_knots(sequence, 1)


def count_knots(
    sequence: list[int],
    mode: int
) -> int:
    """
    Count knots formed by threads on nails.
    """
    n_nails = max(sequence)
    threads: defaultdict[tuple[int, int], int] = defaultdict(int)
    cnt = 0
    for i, start in enumerate(sequence[:-1]):
        end = sequence[i + 1]
        start, end = min(start, end), max(start, end)
        for s, e in threads:
            if end > e > start > s or e > end > s > start:
                cnt += 1
        threads[(start, end)] += 1
    if mode == 0:
        return cnt

    maxt = 0
    for start in range(1, n_nails):
        for end in range(start + 1, n_nails + 1):
            if (start, end) in threads:
                temp: int = threads[(start, end)]
            else:
                temp = 0
            for (s, e), n in threads.items():
                if end > e > start > s or e > end > s > start:
                    temp += n
            maxt = max(maxt, temp)
    return maxt
