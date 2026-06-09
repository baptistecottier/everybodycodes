"""
Event: The Song of Ducks and Dragons
Quest: The Scout Duck Protocol
"""

from typing import Iterator


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[list[int]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[int]] = []
    for puzzle_input in puzzle_inputs.values():
        parts_inputs.append(list(map(int, puzzle_input.splitlines())))
    return parts_inputs


def solver(
    ducks: list[list[int]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    yield run_simulations(ducks[0], max_rounds=10)
    yield run_simulations(ducks[1])


def run_simulations(
    ducks: list[int],
    max_rounds: float = float("inf")
) -> int:
    """
    Simulate duck movements until they stabilize or max rounds is reached.
    """
    r = 0
    t = 1
    while r < max_rounds:
        new_ducks = ducks[::]
        for i in range(len(ducks) - 1):
            if new_ducks[i] == new_ducks[i + 1]:
                continue
            if (new_ducks[i] > new_ducks[i + 1]) == t:
                new_ducks[i + (1 - t)] -= 1
                new_ducks[i + t] += 1
        if all(d == ducks[0] for d in ducks):
            return r
        if new_ducks == ducks:
            t = 1 - t
            continue
        r += 1
        ducks = new_ducks[::]
    return sum(n * d for n, d in enumerate(ducks, 1))
