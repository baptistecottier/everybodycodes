"""
Event: The Kingdom of Algorithmia
Quest: The Ring
"""

from dataclasses import dataclass
from typing import Iterator, TypeAlias

Position: TypeAlias = tuple[int, int]
Coordinates: TypeAlias = set[Position]


@dataclass
class PalmFarm:
    """
    Represents a palm farm with water channels and palm tree locations.
    """
    channel: Coordinates
    palms: Coordinates
    w: int
    h: int

    def values(
        self
    ) -> tuple[Coordinates, Coordinates, int, int]:
        """
        Return the palm farm's channel, palms, width, and height.
        """
        return (self.channel, self.palms, self.w, self.h)


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[PalmFarm]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[PalmFarm] = []
    for note in puzzle_input.values():
        channel: Coordinates = set()
        palms: Coordinates = set()
        x = y = 0
        for y, line in enumerate(note.splitlines()):
            for x, c in enumerate(line):
                if c == ".":
                    channel.add((x, y))
                if c == "P":
                    channel.add((x, y))
                    palms.add((x, y))
        parts_inputs.append(PalmFarm(channel, palms, x, y))
    return parts_inputs


def solver(
    palmfarms: list[PalmFarm]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for palmfarm in palmfarms[:2]:
        yield int(max(fill(palmfarm).values()))


def fill(
    palmfarm: PalmFarm
) -> dict[Position, float]:
    """
    Spread water through the channel and record when each palm is reached.
    """
    channel, palms, w, h = palmfarm.values()
    starts: list[Coordinates] = [
        {(x, y) for (x, y) in channel if (x in (0, w) or y in (0, h))}
    ]
    if starts == [set()]:
        starts = [
            {(x, y)}
            for (px, py) in palms
            for (x, y) in get_neighbours(px, py, channel)
        ]

    mint: dict[Position, float] = {(-1, -1): float("inf")}
    for reached in starts:
        times: dict[Position, float] = {}
        t = 0
        while not palms < reached:
            t += 1
            new = {
                (x, y)
                for pos in reached
                for (x, y) in get_neighbours(*pos, channel)
                if (x, y) not in reached
            }
            for x, y in new:
                if (x, y) in palms:
                    times[(x, y)] = t
            reached.update(new)
        mint = min(mint, times, key=lambda d: sum(d.values()))
    return mint


def get_neighbours(
    x: int,
    y: int,
    channel: Coordinates
) -> Coordinates:
    """
    Return orthogonal channel neighbours for one position.
    """
    neighbours: Coordinates = set()
    for tx, ty in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nx, ny = x + tx, y + ty
        if (nx, ny) in channel:
            neighbours.add((nx, ny))
    return neighbours
