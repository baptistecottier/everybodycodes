"""
Docstring for year_2024.quest_02.quest_02
"""


def get_part_input(test_mode: bool):
    """
    Returns puzzle input parts separated by double newlines from quest_02.input
    file.
    """
    filename = "quest_02.test" if test_mode else "quest_02.input"
    parts_input = []
    with open(filename, encoding="utf-8") as f:
        puzzle_input = f.read()
    for _part in puzzle_input.split("\n\n---\n\n"):
        _wrds, _sntcs = _part.split("\n\n")
        wrds = _wrds[6:].split(',')
        sntcs = _sntcs.splitlines()
        parts_input.append((wrds, sntcs))
    return parts_input


def mirrored(lst: list):
    """
    Returns a list with original elements plus their reversed versions
    appended.
    """
    return lst + [item[::-1] for item in lst]


def transpose(sntcs: list[str]):
    """
    Transposes a list of strings by converting rows to columns.
    """
    w = len(sntcs[0])
    if any(len(sentence) != w for sentence in sntcs):
        raise ValueError(
            "All sentences must contain the same number of symbols"
            )
    return ["".join(sentence[i] for sentence in sntcs) for i in range(w)]


def count_words(wrds, sntcs, overlap=False):
    """
    Finds all occurrences of words in a grid of sentences, returning sets of
    coordinates for each
    match.
    """

    runic = []
    grid = [list(s) for s in sntcs]

    for wrd in wrds:
        clamp = 0 if overlap else len(wrd) - 1
        for y, line in enumerate(grid):
            for x in range(len(line) - clamp):
                if all(wrd[i] == line[(x + i) % len(line)]
                       for i in range(len(wrd))):
                    match = set()
                    for i in range(len(wrd)):
                        match.add(((x + i) % len(line), y))
                    runic.append(match)
    return runic


def solver(test_mode):
    """
    Yield the counts of matched word positions for three puzzle parts using
    mirrored, transposed, and overlapping search variations based on input
    data.
    """
    parts_input = get_part_input(test_mode)

    yield len(count_words(*parts_input[0]))

    words, sentences = parts_input[1]
    yield len({
        pos
        for match in count_words(mirrored(words), sentences)
        for pos in match})

    words, sentences = parts_input[2]
    runic_symbols = {  # Start with horizontal matches with overlapping
        pos
        for match in count_words(mirrored(words), sentences, overlap=True)
        for pos in match
    }.union(  # Pursue with the vertical matches without overlapping
        {(y, x)
         for match in count_words(mirrored(words), transpose(sentences))
         for (x, y) in match
         })
    yield len(runic_symbols)
