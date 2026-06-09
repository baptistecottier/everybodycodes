"""
Event: The Song of Ducks and Dragons
Quest: Encoded in the Scales
"""

from itertools import combinations
from typing import Iterator


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[list[tuple[int, str]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[tuple[int, str]]] = []

    for note in puzzle_input.values():
        adns: list[tuple[int, str]] = []
        for line in note.splitlines():
            i, adn = line.split(":")
            adns.append((int(i), adn))
        parts_inputs.append(adns)

    return parts_inputs


def solver(
    scales_adns: list[list[tuple[int, str]]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for part, adns in enumerate(scales_adns, 1):
        families = extract_families(adns)
        similarities: int = 0
        for family in families:
            parents = None
            min_similarity: float = float("inf")
            for (i, ma), (j, mb) in combinations(family, 2):
                if similarity(ma, mb) < min_similarity:
                    min_similarity = similarity(ma, mb)
                    parents = ((i, ma), (j, mb))
            if parents is None:
                continue
            similarities += sum(
                similarity(parents[0][1], c) * similarity(parents[1][1], c)
                for i, c in family
                if (i, c) not in parents
            )
        if part != 3:
            yield similarities
        else:
            yield sum(i for i, _ in max(families, key=len))


def extract_families(
    adns: list[tuple[int, str]]
) -> list[set[tuple[int, str]]]:
    """
    Extract families of related ADN sequences based on similarity threshold.
    """
    families: list[set[tuple[int, str]]] = []
    while adns:
        i, adn = adns.pop()
        family: set[tuple[int, str]] = set()
        to_add: set[tuple[int, str]] = {(i, adn)}
        while to_add != set():
            family.update(to_add)
            to_add = set()
            for j, ma in adns.copy():
                if any((similarity(ma, mb) > 0.45 * len(ma))
                       for _, mb in family):
                    to_add.add((j, ma))
                    adns.remove((j, ma))
        families.append(family)
    return families


def similarity(
    adn_a: str,
    adn_b: str
) -> int:
    """
    Count matching positions between two sequences.
    """
    score = sum(symb_a == symb_b for symb_a, symb_b in zip(adn_a, adn_b))
    return score
