"""
Story: Melody Made of Code
Quest: Scales, Bags and a Bit of a Mess
"""

from typing import Iterator


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[list[list[int]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[list[int]]] = []
    for puzzle_input in puzzle_inputs.values():
        scales = [
            scale.split(" ")
            for scale in puzzle_input.replace(":", " ").splitlines()
        ]
        part_inputs: list[list[int]] = []
        for scale in scales:
            values: list[int] = [int(scale[0])] + [
                int("".join(str(int(c.isupper())) for c in value), 2)
                for value in scale[1:]
            ]
            part_inputs.append(values)
        parts_inputs.append(part_inputs)
    return parts_inputs


def solver(
    components: list[list[list[int]]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    yield sum(values[0] for values in components[0]
              if values.pop(2) > max(values[1:]))

    yield min(
        components[1],
        key=lambda colors: (-colors[1:][-1], sum(colors[1:][:-1]))
    )[0]

    largest_group: list[int] = max(group(components[2]), key=len)
    yield sum(largest_group)


def group(
    scales: list[list[int]]
) -> list[list[int]]:
    """
    Groups scales by their maximum color index and shine level.
    """
    groups: list[list[int]] = [[] for _ in range(6)]
    for colors in scales:
        shine = colors.pop()
        if colors.count(max(colors[1:])) != 1 or 30 < shine < 33:
            continue
        groups[
            3 * (shine > 30) + colors[1:].index(max(colors[1:]))
            ].append(colors[0])
    return groups
