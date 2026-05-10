"""
Event: The Song of Ducks and Dragons
Quest: Namegraph
"""

from collections import defaultdict
from typing import Iterator


def preprocessing(
    puzzle_input: dict[int, str],
) -> list[tuple[list[str], dict[str, list[str]]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[tuple[list[str], dict[str, list[str]]]] = []
    for note in puzzle_input.values():
        _names, _rules = note.split("\n\n")
        names: list[str] = _names.split(",")
        rules: defaultdict[str, list[str]] = defaultdict(list)
        for rule in _rules.splitlines():
            lht, rht = rule.split(" > ")
            rules[lht] = rht.split(",")
        parts_inputs.append((names, rules))
    return parts_inputs


def solver(pages: list[tuple[list[str], dict[str, list[str]]]]) -> Iterator[str | int]:
    """
    Solve all puzzle parts for this quest.
    """
    for names, rules in pages[:2]:
        compliants: list[tuple[str, int]] = []
        for idx, name in enumerate(names, 1):
            if all(name[i + 1] in rules[name[i]] for i in range(len(name) - 1)):
                compliants.append((name, idx))
        if len(compliants) == 1:
            yield compliants[0][0]
        else:
            yield sum(idx for _, idx in compliants)
    names, rules = pages[2]
    names = clean_names(names, rules)
    yield sum(count_unique_names(name, rules) for name in clean_names(names, rules))


def count_unique_names(prefix: str, rules: dict[str, list[str]]) -> int:
    """
    Recursively counts unique names of length between 7 and 11 following the
    given rules.
    """
    if len(prefix) == 11:
        return 1
    return sum(count_unique_names(prefix + c, rules) for c in rules[prefix[-1]]) + (
        len(prefix) > 6
    )


def clean_names(names: list[str], rules: dict[str, list[str]]) -> list[str]:
    """
    Filters names to remove invalid ones and those that are substrings of
    others.
    """
    for name in names.copy():
        if any(name[i + 1] not in rules[name[i]] for i in range(len(name) - 1)):
            names.remove(name)
    for name in names.copy():
        if any(n in name and n != name for n in names):
            names.remove(name)
    return names
