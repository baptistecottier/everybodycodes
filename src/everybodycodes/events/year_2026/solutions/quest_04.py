"""
Event: Lord of the Wings
Quest: The Rankening
"""

from collections import defaultdict
from dataclasses import dataclass
import re
from typing import Callable, Iterator


@dataclass
class Quest:
    """
    Cumulated times of a runner at the end of each part of a quest.
    """
    time_after_p1: int | None
    time_after_p2: int | None
    time_after_p3: int | None
    completed_parts: int

    def __init__(self):
        self.time_after_p1 = None
        self.time_after_p2 = None
        self.time_after_p3 = None
        self.completed_parts = 0

    def total_time(self) -> int:
        """
        Return the cumulated time of the completed parts.
        """
        cp = self.completed_parts
        if cp == 0:
            return 0
        return getattr(self, f"time_after_p{cp}")

    def set_time_after_part(self, time: int, part: int) -> None:
        """
        Record part as completed, in time after the previous part.
        """
        if part > 1:
            time += getattr(self, f"time_after_p{part - 1}")
        setattr(self, f"time_after_p{part}", time)
        self.completed_parts += 1


type Runners = dict[int, list[Quest]]


def preprocessing(puzzle_input: dict[int, str]) -> list[Runners]:
    """
    Parse each input into the quests of each runner id.
    """
    timesheets: list[Runners] = []
    for notes in puzzle_input.values():
        times = [
            list(map(int, re.findall(r'(\d+)', line)))
            for line in notes.splitlines()]
        sorted_times = sorted(times, key=lambda x: (x[1], x[2]))

        runners: Runners = defaultdict(list)
        for r_id, r_q, r_p, r_t in sorted_times:
            while len(runners[r_id]) < r_q:
                runners[r_id].append(Quest())
            runners[r_id][r_q - 1].set_time_after_part(r_t, r_p)
        timesheets.append(runners)
    return timesheets


def solver(notes: list[Runners]) -> Iterator[int]:
    """
    Yield the checksum of the ranking by time of the first input, by
    completed parts of the second one and by points of the third one.
    """
    yield compute_checksum(notes[0], sorted_by_time)
    yield compute_checksum(notes[1], sorted_by_completed_parts)
    yield compute_checksum(notes[2], sorted_by_points)


def compute_checksum(
        runners: Runners, ranking_function: Callable[[Runners], list[int]]
) -> int:
    """
    Return the sum of rank * value of the ranked values, read from the
    last one, equal values sharing their rank.
    """
    values = ranking_function(runners)
    checksum = 0
    rank = 0
    ties = 1
    last_value = None
    while values:
        value = values.pop()
        if value == last_value:
            ties += 1
        else:
            rank += ties
            ties = 1
            last_value = value
        checksum += rank * value
    return checksum


def sorted_by_time(runners: Runners) -> list[int]:
    """
    Return the total time of each runner, the slowest first.
    """
    scores = [sum(quest.total_time() for quest in runner)
              for runner in runners.values()]
    return sorted(scores, reverse=True)


def sorted_by_completed_parts(runners: Runners) -> list[int]:
    """
    Return the total time of each runner, the fewest completed parts
    first and the slowest first among equals.
    """
    scores: list[tuple[int, int]] = []
    for runner in runners.values():
        completed_parts = sum(quest.completed_parts for quest in runner)
        total_times = sum(quest.total_time() for quest in runner)
        scores.append((-completed_parts, total_times))
    return [times for _, times in sorted(scores, reverse=True)]


def sorted_by_points(runners: Runners) -> list[int]:
    """
    Return the total points of each runner over all the quests parts, in
    increasing order.
    """
    total_points: dict[int, int] = defaultdict(int)
    n_quests = max(len(quests) for quests in runners.values())
    for quest in range(n_quests):
        for part in range(1, 4):
            part_runners = {
                runner: quests
                for runner, quests in runners.items()
                if (
                    len(quests) > quest
                    and getattr(quests[quest], f"time_after_p{part}"))}
            if not part_runners:
                continue
            ranking = sorted((
                (getattr(quests[quest], f"time_after_p{part}"), r_id)
                for r_id, quests in part_runners.items()),
                reverse=True)

            # Points attribution
            points = 50 * part
            ties = 0
            last_time = None
            while points > 0 and ranking:
                time, p_id = ranking.pop()
                if time == last_time:
                    ties += 1
                else:
                    points = max(0, points - ties)
                    ties = 1
                    last_time = time
                total_points[p_id] += points
    return sorted(total_points.values())
