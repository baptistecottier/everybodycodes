"""
Event: Lord of the Wings
Quest: The ISOlation
"""

import heapq
import re
from typing import Iterator

type Vote = tuple[str, str]


def preprocessing(
        puzzle_input: dict[int, str]
) -> list[list[Vote]]:
    """
    Parse each input into its list of (base digits, number) ISO pairs.
    """
    results: list[list[Vote]] = [
        re.findall(r'ISO\d?-(\d+) (\d+)', isos)
        for isos in puzzle_input.values()]
    return results


def solver(votes: list[list[Vote]]) -> Iterator[int]:
    """
    Yield the total score of the first two inputs, then the score of the
    ISO pairs of the third input whose number is the smallest one giving
    its score.
    """
    yield sum(compute_final_score(votes[0]))
    yield sum(compute_final_score(votes[1]))
    yield compute_final_score(votes[2])[1]


def compute_final_score(votes: list[Vote]) -> list[int]:
    """
    Return the summed scores of the pairs whose number is not, then is,
    the smallest one giving its score.
    """
    scores = [0, 0]
    for n1, n2 in votes:
        iso_score = compute_score(n1, n2)
        res = is_iso_2(n1, n2, iso_score)
        scores[res] += iso_score
    return scores


def compute_score(n1: str, n2: str) -> int:
    """
    Return the value of n2 where the digit at position i weighs b ** i,
    b being the matching digit of n1 read cyclically from the right.
    """
    score = 0
    length = len(n2)
    for i in range(length):
        a = int(n1[- (i + 1) % len(n1)])
        b = int(n2[- (i + 1)])
        score += b * pow(a, i)
    return score


def is_iso_2(n1: str, n2: str, score: int) -> bool:
    """
    Tell whether n2 is the smallest number whose score with n1 is score.
    """
    n_digits = 1
    temp = 9
    weights = [
        pow(int(n1[-(i + 1) % len(n1)]), i) for i in range(len(n2) + 1)]
    max_pows = [
        sum(9 * weights[i] for i in range(size))
        for size in range(len(n2) + 1)]

    while temp < score:
        temp += 9 * pow(int(n1[-(n_digits + 1) % len(n1)]), n_digits)
        max_pows.append(temp)
        n_digits += 1
    smaller = -1
    while smaller == -1:
        smaller = find_smaller(score, weights, max_pows, n_digits - 1)
        n_digits += 1
    return smaller == int(n2)


def find_smaller(
        score: int, weights: list[int], max_pows: list[int], n_digits: int
) -> int:
    """
    Return the smallest number whose leading digit is at position
    n_digits and whose weighted digits sum to score, or -1 if none.
    """
    low_bound = max(1, (score - max_pows[n_digits]) // weights[n_digits])
    high_bound = min(9, score // weights[n_digits])
    queue = [
        (k, score - k * weights[n_digits], n_digits - 1)
        for k in range(low_bound, high_bound + 1)]
    while queue:
        cand, rem, nd = heapq.heappop(queue)
        if rem < 0:
            continue

        if nd == -1:
            if rem == 0:
                return cand
            continue

        low_bound = max(0, (rem - max_pows[nd]) // weights[nd])
        high_bound = min(9, rem // weights[nd])

        for k in range(low_bound, high_bound + 1):
            heapq.heappush(
                queue, (cand * 10 + k, rem - k * weights[nd], nd - 1))
    return -1
