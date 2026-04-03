"""
Event: The Kingdom of Algorithmia
Quest: Not Fast but Furious
"""

from typing import Iterator, TypeAlias
from sympy.utilities.iterables import multiset_permutations  # type: ignore

Plans: TypeAlias = dict[str, tuple[int, ...]]
Track: TypeAlias = tuple[int, ...]


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[tuple[Plans, Track]]:
    """
    Parse the provided input content and return a list of (plans, track)
    tuples where plans map names to tuples of action integers and tracks are
    parsed via get_track.
    """
    raw_tracks = ["""
S====
=====
""", """
S-=++=-==++=++=-=+=-=+=+=--=-=++=-==++=-+=-=+=-=+=+=++=-+==++=++=-=-=--
-                                                                     -
=                                                                     =
+                                                                     +
=                                                                     +
+                                                                     =
=                                                                     =
-                                                                     -
--==++++==+=+++-=+=-=+=-+-=+-=+-=+=-=+=--=+++=++=+++==++==--=+=++==+++-
""", """
S+= +=-== +=++=     =+=+=--=    =-= ++=     +=-  =+=++=-+==+ =++=-=-=--
- + +   + =   =     =      =   == = - -     - =  =         =-=        -
= + + +-- =-= ==-==-= --++ +  == == = +     - =  =    ==++=    =++=-=++
+ + + =     +         =  + + == == ++ =     = =  ==   =   = =++=
= = + + +== +==     =++ == =+=  =  +  +==-=++ =   =++ --= + =
+ ==- = + =   = =+= =   =       ++--          +     =   = = =--= ==++==
=     ==- ==+-- = = = ++= +=--      ==+ ==--= +--+=-= ==- ==   =+=    =
-               = = = =   +  +  ==+ = = +   =        ++    =          -
-               = + + =   +  -  = + = = +   =        +     =          -
--==++++==+=+++-= =-= =-+-=  =+-= =-= =--   +=++=+++==     -=+=++==+++-"""]

    act_map: dict[str, int] = {"+": 1, "-": -1, "=": 0, "S": 0}
    part_inputs: list[tuple[Plans, Track]] = []

    for part, pi in puzzle_input.items():
        plans: Plans = {}
        data: list[str] = pi.split("\n\n")

        for plan in data[0].splitlines():
            name, actions = plan.split(":")
            plans[name] = tuple(act_map[act] for act in actions.split(","))

        track = get_track(raw_tracks[part - 1][1:])
        part_inputs.append((plans, track))
    return part_inputs


def solver(
    race_infos: list[tuple[Plans, Track]]
) -> Iterator[str]:
    """
    Run race simulations from inputs and yield two sorted ranking strings
    followed by the count of winning permutations for the final scenario.
    """
    ranks = race(*race_infos[0], max_segment=10)
    yield "".join(sorted(ranks, reverse=True, key=lambda r: ranks[r]))
    ranks = race(*race_infos[1], n_laps=10)
    yield "".join(sorted(ranks, reverse=True, key=lambda r: ranks[r]))

    # 2024 = len(plan) * 187, so the result after 2024 laps is the same as the
    # one after len(plan) laps
    plans, track = race_infos[2]
    adv_score = race(plans, track, n_laps=11)["A"]
    winning = 0
    for plan in multiset_permutations(plans["A"]):
        winning += race({"B": tuple(plan)}, track, n_laps=11)["B"] > adv_score
    yield str(winning)


def race(
    plans: Plans,
    track: Track,
    max_segment: int = 1_000_000,
    n_laps: int = 1_000_000
) -> dict[str, int]:
    """
    Simulate each participant's progression across a circular track by
    applying track modifiers or action plans per segment, accumulating
    'essence' until reaching max_segment steps or n_laps laps, and return a
    dict mapping participants to their total essence.
    """
    ranks: dict[str, int] = {}
    for p, actions in plans.items():
        power = 10
        essence = lap = seg = 0
        while seg < max_segment and lap < n_laps:
            if track and track[seg % len(track)] != 0:
                power += track[seg % len(track)]
            else:
                power += actions[seg % len(actions)]
            essence += power

            if (seg := seg + 1) % len(track) == 0:
                lap += 1
        ranks[p] = essence
    return ranks


def get_track(
    raw_track: str
) -> Track:
    """
    Return a tuple of integers representing the sequence of actions
    obtained by traversing the ASCII grid in data from the initial position to
    the 'S' cell, where '+' maps to 1, '-' maps to -1, and '='/'S' map to 0.
    """
    grid: list[list[str]] = [list(d) for d in raw_track.splitlines()]
    act_map: dict[str, int] = {"+": 1, "-": -1, "=": 0, "S": 0}
    x, y = 1, 0
    px, py = 0, 0
    track: list[int] = []
    while grid[y][x] != "S":
        track.append(act_map[grid[y][x]])
        for tx, ty in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= ty < len(grid) and 0 <= tx < len(grid[ty]):
                if grid[ty][tx] != " " and (tx, ty) != (px, py):
                    px, py = x, y
                    x, y = tx, ty
                    break
    track.append(0)  # Corresponding to the action of 'S'
    return tuple(track)
