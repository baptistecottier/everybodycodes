"""
Event: The Song of Ducks and Dragons
Quest: Mentorship Matrix
"""

from typing import Iterator


def preprocessing(puzzle_input: dict[int, str]) -> list[str]:
    """
    Parse the raw input content into per-part structures.
    """
    knights: list[str] = list(puzzle_input.values())
    return knights


def solver(knights: list[str]) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    seg1: str = knights[0]
    yield count_pairs(seg1, len(seg1), to_skip="bc")
    seg2: str = knights[1]
    yield count_pairs(seg2, len(seg2))
    seg3: str = knights[2]
    yield count_pairs(seg3, 1000, 1000, rep=1000)


def count_pairs(
    segment: str, back_dist: int, front_dist: int = 0, to_skip: str = "", rep: int = 1
) -> int:
    """
    Count matching lower and upper case pairs within the scan window.
    """
    pairs = 0
    for i, c in enumerate(segment):
        if c.isupper() or c in to_skip:
            continue
        for j in range(i - back_dist, i + front_dist + 1):
            if segment[j % len(segment)] == c.upper():
                pairs += rep
                if j >= len(segment) or j < 0:
                    pairs -= 1
    return pairs
