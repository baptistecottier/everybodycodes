#!/usr/bin/env python
"""
Runner script for Everybody Codes puzzles.

Usage:
    python ec.py <year> [quest|test] [test]

Examples:
    python ec.py 2024        # Run all quests of 2024 with real input
    python ec.py 2024 test   # Run all quests of 2024 with test input
    python ec.py 2024 01     # Run quest 01 of 2024 with real input
    python ec.py 2024 01 test # Run quest 01 of 2024 with test input
    python ec.py 2025 15     # Run quest 15 of 2025 with real input
"""

import importlib.util
from importlib.machinery import SourceFileLoader
import os
import sys


def run_quests(year, quest, test_mode):
    """
    Run the specified quest (or all quests 01–20 if quest is None) for the
    given year by invoking run_single_quest with the module's directory and
    the provided test_mode.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if quest is None:
        # Run all quests
        for quest_num in range(1, 21):
            q = f"{quest_num:02d}"
            run_single_quest(script_dir, year, q, test_mode)
    else:
        run_single_quest(script_dir, year, quest, test_mode)


def run_single_quest(script_dir, year, quest, test_mode):
    """
    Import and run the solver function from a quest module located under
    script_dir/year_{year}/quest_{quest}, printing results for each part,
    skipping missing files and reporting an error if no solver is found.
    """
    quest_dir = os.path.join(script_dir, f"year_{year}", f"quest_{quest}")
    quest_file = os.path.join(quest_dir, f"quest_{quest}.py")

    if not os.path.exists(quest_file):
        return  # Skip if quest file does not exist

    # Import the quest module
    spec = importlib.util.spec_from_file_location(f"quest_{quest}", quest_file)
    if spec is None or spec.loader is None:
        # Fallback to SourceFileLoader when spec or loader is missing
        loader = SourceFileLoader(f"quest_{quest}", quest_file)
        spec = importlib.util.spec_from_loader(f"quest_{quest}", loader)
        assert spec is not None
        quest_module = importlib.util.module_from_spec(spec)
        loader.exec_module(quest_module)
    else:
        assert spec is not None and spec.loader is not None
        quest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(quest_module)

    # Call the solver function
    if hasattr(quest_module, 'solver'):
        os.chdir(quest_dir)
        print(f"Year {year} Quest {quest}:")
        for part, result in enumerate(quest_module.solver(test_mode), 1):
            print(f"  Part {part}: {result}")
    else:
        print(f"Error: No solver function found in {quest_file}")


def main():
    """
    Entry point that validates CLI arguments, loads and executes the specified
    quest solver module (optionally in test mode), and prints each part's
    result.
    """
    if len(sys.argv) < 2:
        print("Usage: python ec.py <year> [quest|test] [test]")
        print("Examples:")
        print(("  python ec.py 2024        "
               "# Run all quests of 2024 with real input"))
        print(("  python ec.py 2024 test   "
               "# Run all quests of 2024 with test input"))
        print(("  python ec.py 2024 01     "
               "# Run quest 01 of 2024 with real input"))
        print(("  python ec.py 2024 01 test "
               "# Run quest 01 of 2024 with test input"))
        sys.exit(1)

    year = sys.argv[1]

    if len(sys.argv) == 2:
        # Run all quests with real input
        run_quests(year, None, False)
    elif len(sys.argv) == 3:
        if sys.argv[2] == "test":
            # Run all quests with test input
            run_quests(year, None, True)
        else:
            # Run single quest with real input
            quest = sys.argv[2].zfill(2)
            run_quests(year, quest, False)
    elif len(sys.argv) == 4:
        quest = sys.argv[2].zfill(2)
        test_mode = sys.argv[3] == "test"
        run_quests(year, quest, test_mode)
    else:
        print("Too many arguments")
        sys.exit(1)


if __name__ == "__main__":
    main()
