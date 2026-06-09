"""
Event: The Kingdom of Algorithmia
Quest: Galactic Geometry
"""

from math import prod
from typing import Iterator, TypeAlias

Coordinates: TypeAlias = tuple[int, int]


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[set[tuple[int, int]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[set[Coordinates]] = []
    for pi in puzzle_input.values():
        stars: set[Coordinates] = set()
        for y, line in enumerate(pi.splitlines()):
            for x, c in enumerate(line):
                if c == "*":
                    stars.add((x, y))
        parts_inputs.append(stars)

    return parts_inputs


def solver(
    sky_fragments: list[set[Coordinates]]
) -> Iterator[int]:
    """
    Execute solver for quest 17, yielding the product of the first three
    results for each part with distance constraints."""
    for part, stars in enumerate(sky_fragments, 1):
        max_d: float = 6 if part == 3 else float("inf")
        results: list[int] = cluster(stars, max_d)
        yield prod(results[:3])


def cluster(
    stars: set[Coordinates],
    max_dist: float
) -> list[int]:
    """
    Cluster stars under the distance limit and return basin scores.
    """
    stars_list: list[Coordinates] = list(stars)

    distances: list[tuple[int, Coordinates, Coordinates]] = []
    for i, s1 in enumerate(stars_list):
        for s2 in stars_list[i + 1:]:
            d = abs(s1[0] - s2[0]) + abs(s1[1] - s2[1])
            if d < max_dist:
                distances.append((d, s1, s2))
    distances.sort()

    centers = {s: s for s in stars_list}
    size = {s: 1 for s in stars_list}
    edge_sum = {s: 0 for s in stars_list}

    for d, s1, s2 in distances:
        center1 = find(centers, s1)
        center2 = find(centers, s2)
        if center1 != center2:
            if size[center1] < size[center2]:
                center1, center2 = center2, center1
            centers[center2] = center1
            size[center1] += size[center2]
            edge_sum[center1] += edge_sum[center2] + d

    results: list[int] = [
        edge_sum[s] + size[s]
        for s in stars_list if centers[s] == s
    ]
    results.sort(reverse=True)
    return results


def find(
    parents: dict[Coordinates, Coordinates],
    star: Coordinates
) -> Coordinates:
    """
    Return the representative for a node in the disjoint-set structure.
    """
    if parents[star] == star:
        return star
    parents[star] = find(parents, parents[star])
    return parents[star]
