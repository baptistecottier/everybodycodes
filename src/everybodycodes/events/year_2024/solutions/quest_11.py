"""
Event: The Kingdom of Algorithmia
Quest: Biological Warfare
"""

from typing import Iterator, TypeAlias

Conversions: TypeAlias = dict[str, list[str]]


def preprocessing(puzzle_input: dict[int, str]) -> list[Conversions]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_input: list[dict[str, list[str]]] = []
    for part_input in puzzle_input.values():
        conversions: dict[str, list[str]] = {}
        for line in part_input.splitlines():
            src, dst = line.split(":")
            conversions[src] = dst.split(",")
        parts_input.append(conversions)
    return parts_input


def solver(conversions: list[Conversions]) -> Iterator[int]:
    """
    Solves termite population puzzles by calculating growth after specified
    days and finding population differences.
    """
    for conversion, start, n_days in zip(conversions[:2], "AZ", [4, 10]):
        yield count_termite_after_n_days(conversion, start, n_days)

    conversion = conversions[2]
    counts: list[int] = sorted(
        count_termite_after_n_days(conversion, start, 20) for start in conversion.keys()
    )
    yield counts[-1] - counts[0]


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
