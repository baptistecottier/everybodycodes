"""
Event: The Song of Ducks and Dragons
Quest: When Roots Remember
"""

from typing import Iterator


def preprocessing(puzzle_inputs: dict[int, str]):
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[tuple[list[str], list[int], list[list[int]]]] = []

    for part, puzzle_input in puzzle_inputs.items():
        notes: list[str] = puzzle_input.split("\n\n\n")
        all_plants = notes[0].split("\n\n")
        if len(notes) > 1:
            test_cases = notes[1]
            tests: list[list[int]] = [
                list(map(int, t.split())) for t in test_cases.splitlines()
            ]
        else:
            tests = [[1] * len(all_plants)]

        if part == 3:
            max_energy: list[int] = [
                2 * sum(test[i] for test in tests) // len(tests)
                for i in range(len(tests[0]))
            ]
        else:
            max_energy = [0] * len(tests[0])
        parts_inputs.append((all_plants, max_energy, tests))

    return parts_inputs


def solver(
    plant_connections: list[tuple[list[str], list[int], list[list[int]]]],
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for plants, max_energy, tests in plant_connections:
        sum_last_plant_energy = 0
        max_last_plant_energy: int = last_plant_energy(plants, max_energy)
        for free_thicknesses in tests:
            lpe: int = last_plant_energy(plants, free_thicknesses)
            if lpe != 0:
                sum_last_plant_energy += abs(max_last_plant_energy - lpe)

        yield sum_last_plant_energy


def last_plant_energy(plants: list[str], free_thicknesses: list[int]) -> int:
    """
    Calculate the energy of the last plant based on branch thickness and
    incoming energy from previous plants.
    """
    energy: list[int] = [0]
    free_iter = iter(free_thicknesses)
    for plant in plants:
        branches = plant.splitlines()
        thickness = int(branches[0].split()[-1][:-1])

        if len(branches) > 1 and "free" in branches[1]:
            energy.append(next(free_iter))
            continue

        inc_energy: int = incoming_energy(branches[1:], energy)
        energy.append(inc_energy * (inc_energy >= thickness))
    return energy[-1]


def incoming_energy(branches: list[str], plant_energy: list[int]):
    """
    Calculate the total incoming energy by summing the product of each
    branch's thickness and its corresponding plant's energy.
    """
    inc_energy = 0
    for branch in branches:
        words = branch.split()
        plt = int(words[4])
        tck = int(words[-1])
        inc_energy += tck * plant_energy[plt]
    return inc_energy
