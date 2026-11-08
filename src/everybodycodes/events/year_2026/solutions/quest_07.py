"""
Event: Lord of the Wings
Quest: The Explouding
"""

import re
from collections import defaultdict
from typing import Iterator


def preprocessing(
        puzzle_inputs: dict[int, str]
) -> list[dict[int, tuple[int, list[int]]]]:
    """
    Parse each input into its clouds, mapping the id of a cloud to its energy
    and to the ids of the clouds it is connected to.
    """
    return [
        {int(cloud_id): (int(energy), list(map(int, connections.split(','))))
         for cloud_id, energy, connections in
         re.findall(r'id=(\d+), energy=(\d+), connections=(\S+)', notes)}
        for notes in puzzle_inputs.values()
    ]


def solver(notes: list[dict[int, tuple[int, list[int]]]]) -> Iterator[int]:
    """
    Yield the total impulse after sending an energy of 5 from the most
    connected cloud of the first notes, then of 10 from the most connected
    cloud of the second notes.
    """
    max_cloud = max(notes[0].keys(), key=lambda x: len(notes[0][x][1]))
    yield sum(propagate_impulse(notes[0], 5, max_cloud).values())

    max_cloud = max(notes[1].keys(), key=lambda x: len(notes[1][x][1]))
    yield sum(propagate_impulse(notes[1], 10, max_cloud).values())


# pylint: disable-next=dangerous-default-value
def propagate_impulse(
        clouds: dict[int, tuple[int, list[int]]],
        energy: int,
        starting_cloud: int,
        exploded: set[int] = set()
) -> dict[int, int]:
    """
    Return the impulse of each cloud once energy has been sent from
    starting_cloud: at each step the energy drops by one and reaches the
    clouds connected to those reached at the step before, except exploded
    ones.
    """
    impulses = {c: clouds[c][0] for c in clouds.keys()}
    connections = {starting_cloud: 1}
    impulses[starting_cloud] += energy
    while energy > 0:
        energy -= 1
        new_connections: defaultdict[int, int] = defaultdict(int)
        for c, n in connections.items():
            for cc in clouds[c][1]:
                if cc in exploded:
                    continue
                new_connections[cc] += n
        for c, n in new_connections.items():
            impulses[c] += energy * n
        connections = new_connections
    return impulses
