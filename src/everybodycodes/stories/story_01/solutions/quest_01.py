"""
Story: Echoes of Enigmatus
Quest: EniCode
"""

from typing import Iterator, TypeVar

T = TypeVar("T", int, str)


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[list[list[int]]]:
    """
    Reads and parses puzzle input files, returning a nested list of integers
    for each part.
    """
    parts_inputs: list[list[list[int]]] = []
    for puzzle_input in puzzle_inputs.values():
        params: list[list[int]] = []
        for line in puzzle_input.splitlines():
            params.append([int(item[2:]) for item in line.split()])
        parts_inputs.append(params)
    return parts_inputs


def solver(
    parameters_sets: list[list[list[int]]]
) -> Iterator[int]:
    """
    Yields the highest score for each part based on input parameters and a
    scoring formula.
    """
    yield find_high_score(parameters_sets[0], 0, str)
    yield find_high_score(parameters_sets[1], -5, str)
    yield find_high_score(parameters_sets[2], 0, int)


def find_high_score(
    parameters_set: list[list[int]],
    exp_start: int,
    fmt: type[T]
) -> int:
    """
    Finds the highest score from a set of parameters using the eni function.
    """
    high_score = 0
    for parameters in parameters_set:
        score = 0
        mod = parameters[6]
        for n, exp_end in zip(parameters[:3], parameters[3:6]):
            score += eni(n, mod, exp_start % exp_end, exp_end, fmt)
        high_score = max(high_score, score)
    return high_score


def eni(
    n: int,
    mod: int,
    exp_start: int,
    exp_end: int,
    fmt: type[T]
) -> int:
    """
    Computes a score by summing formatted cycle elements between exp_start and
    exp_end based on the cycle of n modulo mod.
    """
    start, cycle = get_cycle(n, mod)
    score: T = fmt()

    # Elements before the cyclic part
    for i in range(exp_start, min(len(start), exp_end)):
        score = fmt(start[-i - 1]) + score
    exp_start = max(exp_start, len(start))

    # Elements in the cyclic part
    loops = (exp_end - exp_start) // len(cycle)
    if loops > 0:
        sum_cycle: T = fmt()
        for j in range(len(cycle), 0, -1):
            idx = (len(start) - (j + exp_start)) % len(cycle)
            sum_cycle = sum_cycle + fmt(cycle[idx])

        score = sum_cycle * loops + score
        exp_start += loops * len(cycle)

    # Elements after the cyclic part
    for i in range(exp_start, exp_end):
        score = fmt(cycle[(-i - 1 + len(start)) % len(cycle)]) + score

    return int(score)


def get_cycle(
    n: int,
    mod: int
) -> tuple[list[int], list[int]]:
    """
    Computes the cycle of remainders when repeatedly multiplying n modulo mod.
    Returns a tuple of (start, cycle) where start is the non-cyclic part and
    cycle is the repeating part.
    """
    remainders: list[int] = []
    visited: set[int] = set()
    score: int = 1

    while True:
        score = (score * n) % mod
        if score in visited:
            break
        remainders.append(score)
        visited.add(score)

    remainders = remainders[::-1]
    cycle_start = remainders.index(score)

    start = remainders[cycle_start + 1:]
    cycle = remainders[:cycle_start + 1]

    return (start, cycle)
