"""
Story: The Entertainment Hub
Quest: The Pocket-Money Popper
"""

from collections import deque
from typing import Iterator


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[list[int]]:
    """
    Parse the raw input content into per-part structures.
    """
    mapping: dict[str, int] = {"R": 0, "G": 1, "B": 2}
    parts_inputs: list[list[int]] = [
        [mapping[b] for b in balloons]
        for balloons in puzzle_inputs.values()
    ]
    return parts_inputs


def solver(
    balloons: list[list[int]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for line, rep_front, rep_back in zip(
        balloons, (1, 50, 50_000), (0, 50, 50_000)
    ):
        yield pop_balloons(line, rep_front, rep_back)


def pop_balloons(
    balloons: list[int],
    rep_front: int,
    rep_back: int
) -> int:
    """
    Simulates popping balloons based on fluffbolt counter matching balloon
    values with specified repetitions.
    """
    fluffbolt = 0
    balloons_front = deque(balloons * rep_front)
    balloons_back = deque(balloons * rep_back)
    while balloons_front:
        b = balloons_front.popleft()
        while fluffbolt % 3 == b:
            if rep_back == 0:
                b = balloons_front.popleft()
                if len(balloons_front) == 0:
                    break
            else:
                if len(balloons_front) + 1 == len(balloons_back):
                    balloons_back.popleft()
                break

        if len(balloons_back) > len(balloons_front):
            balloons_front.append(balloons_back.popleft())

        fluffbolt += 1

    return fluffbolt
