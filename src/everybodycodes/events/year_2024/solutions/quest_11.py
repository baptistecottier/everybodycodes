"""
Event: The Kingdom of Algorithmia
Quest: Biological Warfare
"""

from collections import defaultdict
from typing import Iterator, TypeAlias

Conversions: TypeAlias = dict[str, list[str]]


def preprocessing(puzzle_input: dict[int, str]) -> list[Conversions]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_input: list[dict[str, list[str]]] = []
    for part_input in puzzle_input.values():
        conversions: defaultdict[str, list[str]] = defaultdict(list)
        for line in part_input.splitlines():
            src, dst = line.split(":")
            conversions[src] = dst.split(",")
        parts_input.append(conversions)
    return parts_input


def solver(convs: list[Conversions]) -> Iterator[int]:
    """
    Solves termite population puzzles by calculating growth after specified
    days and finding population differences.
    """
    conversions: list[Conversions] = convs[:2] + [convs[2]] * len(convs[2])
    starts: list[str] = ['A', 'Z'] + list(convs[2].keys())
    durations: list[int] = [4, 10] + [20] * len(convs[2])

    counts = [
        count_termite_after_n_days(conversion, start, n_days)
        for conversion, start, n_days in zip(conversions, starts, durations)
    ]

    yield counts.pop(0)
    yield counts.pop(0)
    yield max(counts) - min(counts)


def count_termite_after_n_days(
    conversions: Conversions, start: str, n_days: int
) -> int:
    """
    Simulate termite conversions for a fixed number of days.
    """
    population = {termite: int(termite == start) for termite in conversions}
    for _ in range(n_days):
        new_population = {termite: 0 for termite in population}
        for k, v in conversions.items():
            for t in v:
                new_population[t] += population[k]
        population = new_population
    return sum(population.values())
