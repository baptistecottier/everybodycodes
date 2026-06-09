"""
Event: The Kingdom of Algorithmia
Quest: The Runes of Power
"""

from collections.abc import Iterator
from typing import TypeAlias

Coords: TypeAlias = set[tuple[int, int]]
Inscription: TypeAlias = tuple[list[str], list[str]]


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[Inscription]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_input: list[Inscription] = []
    for _part in puzzle_input.values():
        _wrds, _sntcs = _part.split("\n\n")
        wrds: list[str] = _wrds[6:].split(",")
        sntcs: list[str] = _sntcs.splitlines()
        parts_input.append((wrds, sntcs))
    return parts_input


def solver(
    inscriptions: list[Inscription]
) -> Iterator[int]:
    """
    Yield the counts of matched word positions for three puzzle parts using
    mirrored, transposed, and overlapping search variations based on input
    data.
    """
    yield len(count_words(*inscriptions[0]))

    words, sentences = inscriptions[1]
    yield len(
        {pos for match in count_words(mirrored(words), sentences)
         for pos in match}
    )

    words, sentences = inscriptions[2]
    runic_symbols = {  # Start with horizontal matches with overlapping
        pos
        for match in count_words(mirrored(words), sentences, overlap=True)
        for pos in match
    }.union(  # Pursue with the vertical matches without overlapping
        {
            (y, x)
            for match in count_words(mirrored(words), transpose(sentences))
            for (x, y) in match
        }
    )
    yield len(runic_symbols)


def mirrored(
    lst: list[str]
) -> list[str]:
    """
    Returns a list with original elements plus their reversed versions
    appended.
    """
    return lst + [item[::-1] for item in lst]


def transpose(
    sntcs: list[str]
) -> list[str]:
    """
    Transposes a list of strings by converting rows to columns.
    """
    w: int = len(sntcs[0])
    if any(len(sentence) != w for sentence in sntcs):
        raise ValueError(
            "All sentences must contain the same number of symbols")
    return ["".join(sentence[i] for sentence in sntcs) for i in range(w)]


def count_words(
    wrds: list[str],
    grid: list[str],
    overlap: bool = False
) -> list[Coords]:
    """
    Finds all occurrences of words in a grid of sentences, returning sets of
    coordinates for each
    match.
    """
    runic: list[Coords] = []

    for wrd in wrds:
        for y, line in enumerate(grid):
            line_length: int = len(line)
            search_limit: int = line_length
            if not overlap:
                search_limit -= len(wrd) - 1

            for x in range(search_limit):
                if line[x] != wrd[0]:
                    continue

                ok = True
                for i, w in enumerate(wrd):
                    if w != line[(x + i) % len(line)]:
                        ok = False
                        break
                if ok:
                    match: Coords = set()
                    for i in range(len(wrd)):
                        match.add(((x + i) % len(line), y))
                    runic.append(match)

    return runic
