"""
Event: The Kingdom of Algorithmia
Quest: Gliding Finale
"""

from heapq import heappop, heappush
from collections import defaultdict
from typing import Iterator, TypeAlias

State: TypeAlias = tuple[int, int, int, int, int]


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[list[list[int]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[list[int]]] = []
    converter = {
        "+": 1, "-": -2, ".": -1, "#": 0, "S": -1, "A": -1, "B": -1, "C": -1}
    for puzzle_input in puzzle_inputs.values():
        grid: list[list[int]] = [
            [converter[c] for c in line]
            for line in puzzle_input.splitlines()
        ]
        parts_inputs.append(grid)
    return parts_inputs


def solver(
    training_maps: list[list[list[int]]]
) -> Iterator[float]:
    """
    Search each sky grid for the maximum score reachable in 100 moves.
    """
    for tm in training_maps[:2]:
        queue: list[tuple[int, int, int, int, int, int]] = []
        heappush(queue, (-1000, 0, len(tm[0]) // 2, 0, len(tm[0]) // 2, -1))

        best: defaultdict[State, float] = defaultdict(lambda: float("-inf"))
        best_result = float("-inf")

        while queue:
            alt, m, x, y, px, py = heappop(queue)
            state = (m, x, y, px, py)

            if -alt <= best[state]:
                continue
            best[state] = -alt

            if m == 100:
                best_result = max(best_result, -alt)
                continue

            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (
                    (nx, ny) == (px, py)
                    or not (0 <= nx < len(tm[0]) and 0 <= ny < len(tm))
                    or tm[ny][nx] == 0
                ):
                    continue

                heappush(queue, (alt - tm[ny][nx], m + 1, nx, ny, x, y))

        yield best_result
