#!/usr/bin/env python
# pylance: ignore
# mypy: ignore-errors
# pyright: ignore


"""
Runner script for Everybody Codes puzzles.

Usage:
    python ec.py <year> [quest] [-test] [-all]

Examples:
    python ec.py 2024        # Run all quests of 2024 with real input
    python ec.py 2024 01     # Run quest 01 of 2024 with real input
    python ec.py 2024 01 -test # Run quest 01 of 2024 with test input
    python ec.py 2024 01 -all  # Validate all set inputs for quest 01
    python ec.py 2025 15     # Run quest 15 of 2025 with real input
"""

import importlib.util
from importlib.machinery import ModuleSpec, SourceFileLoader
import inspect
import json
import os
import sys
import time
import types
from typing import Any


def normalize_part_input(raw_input) -> dict[int, str]:
    """
    Normalize any supported input shape into a dict keyed by 1, 2, 3.
    """
    if isinstance(raw_input, dict):
        return {
            part: str(raw_input.get(part, raw_input.get(str(part), ""))).rstrip("\n")
            for part in range(1, 4)
        }

    text = str(raw_input)
    separator = "\n\n---\n\n" if "\n\n---\n\n" in text else "---"
    chunks = [chunk.strip("\n") for chunk in text.split(separator)]
    return {
        part: (chunks[part - 1] if part - 1 < len(chunks) else "")
        for part in range(1, 4)
    }


def parts_dict_to_content(parts_input: dict[int, str]) -> str:
    """
    Convert part dictionary input back to the legacy joined content format.
    """
    return "\n\n---\n\n".join(
        [
            str(parts_input.get(1, "")).rstrip("\n"),
            str(parts_input.get(2, "")).rstrip("\n"),
            str(parts_input.get(3, "")).rstrip("\n"),
        ]
    )


def run_quests(
    year,
    event,
    quest,
    test_mode,
    only_part: int | None = None,
    input_case: str | None = None,
) -> None:
    """
    Run the specified quest (or all quests 01–20 if quest is None) for the
    given year by invoking run_single_quest with the module's directory and
    the provided test_mode.
    """
    script_dir: str = os.path.dirname(os.path.abspath(__file__))
    if quest is None:
        # Run all quests (optionally only a specific part)
        for quest_num in range(1, 21):
            q: str = f"{quest_num:02d}"
            run_single_quest(
                script_dir, year, event, q, test_mode, only_part, input_case
            )
    else:
        run_single_quest(
            script_dir, year, event, quest, test_mode, only_part, input_case
        )


def run_single_quest(
    script_dir,
    year,
    event,
    quest,
    test_mode,
    only_part: int | None = None,
    input_case: str | None = None,
) -> None:
    """
    Import and run the solver function from a quest module located under
    script_dir/events/year_{year}/quest_{quest}, printing results for each
    part, skipping missing files and reporting an error if no solver is found.
    """
    if event == "events":
        folder_path = "events/year"
    elif event == "stories":
        folder_path = "stories/story"
    elif event == "gridos":
        folder_path = "gridos/gridos"
        
    year_dir: str = os.path.join(script_dir, f"{folder_path}_{year}")

    # Support two layouts:
    # - legacy: year_dir/quest_<qq>/quest_<qq>.py with inputs alongside
    # - new:    year_dir/solutions/quest_<qq>.py and year_dir/inputs/* for inputs
    old_quest_dir: str = os.path.join(year_dir, f"quest_{quest}")
    old_quest_file: str = os.path.join(old_quest_dir, f"quest_{quest}.py")
    new_solution_file: str = os.path.join(year_dir, "solutions", f"quest_{quest}.py")

    if os.path.exists(new_solution_file):
        quest_file = new_solution_file
        inputs_dir = os.path.join(year_dir, "inputs")
        module_dir = os.path.dirname(quest_file)
    elif os.path.exists(old_quest_file):
        quest_file = old_quest_file
        inputs_dir = old_quest_dir
        module_dir = old_quest_dir
    else:
        return  # Skip if neither layout contains the quest file

    # Import the quest module using helper
    try:
        quest_module: types.ModuleType = load_quest_module(quest_file, quest)
    except Exception:
        print(f"Error: Could not import quest module from {quest_file}")
        return

    # Call the solver function
    if hasattr(quest_module, "solver"):
        # Use the directory that contains the module as the working dir
        os.chdir(module_dir)
        parts_input: dict[int, str] = load_input_content(
            inputs_dir, quest, test_mode, input_case
        )
        adapt_get_part_input(quest_module, parts_input)
        print(f"Year {year} Quest {quest}:")
        results_iter = run_solver(quest_module, test_mode, parts_input)
        if only_part is None:
            for part, result in enumerate(results_iter, 1):
                print(f"  Part {part}: {result}")
        else:
            for part, result in enumerate(results_iter, 1):
                if part == only_part:
                    print(f"  Part {part}: {result}")
                    break
    else:
        print(f"Error: No solver function found in {quest_file}")


def run_gridos(
    event: str,
    quest: str,
    part: str,
    year: str | None = None,
    case_id: str | None = None,
) -> None:
    """
    Run a GridOS part using the part-based JSON test data.
    """
    from pathlib import Path

    script_dir: str = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, str(Path(script_dir).resolve().parent))

    try:
        from everybodycodes.gridos.gridOS import (
            load_part_postprocessing,
            run_cases_with_rules,
            _load_callable_from_path,
        )
    except ImportError as exc:
        print(f"Error: could not import GridOS support: {exc}")
        return

    if year is None:
        print("Error: Missing GridOS year information")
        return

    part_map = {"1": "I", "2": "II", "3": "III"}
    part_roman = part_map.get(str(part))
    if part_roman is None:
        print("Error: part must be 1, 2, or 3")
        return

    quest_num = str(int(quest))
    part_number = str(int(part))
    base_dir = Path(script_dir) / "gridos" / f"gridos_{year}"
    test_cases_path = (
        base_dir
        / f"quest_{quest_num}"
        / f"part_{part_roman}"
        / f"test_cases_q{quest_num}p{part_number}.json"
    )
    rules_path = (
        base_dir
        / f"quest_{quest_num}"
        / f"part_{part_roman}"
        / f"q{quest_num}p{part_number}.rules"
    )

    if not test_cases_path.exists():
        print(f"Error: GridOS test cases not found: {test_cases_path}")
        return
    if not rules_path.exists():
        print(f"Error: GridOS rules file not found: {rules_path}")
        return

    cases = json.loads(test_cases_path.read_text(encoding="utf-8"))
    normalized_cases = []
    for case in cases:
        normalized = dict(case)
        if "input" in normalized and "data" not in normalized:
            normalized["data"] = normalized.pop("input")
        if "case" not in normalized and "id" in normalized:
            normalized["case"] = normalized["id"]
        normalized_cases.append(normalized)

    postprocessing = load_part_postprocessing(
        f"part_{part_roman.lower()}", quest=quest, base_dir=Path(script_dir) / "gridos"
    )

    if postprocessing is None:
        quest_dir = base_dir / f"quest_{quest_num}"
        alt_paths = [
            quest_dir / "postprocessing.py",
            quest_dir / f"part_{part_roman}" / "postprocessing.py",
            quest_dir / f"part_{part_roman}" / f"postprocessing_q{quest_num}p{part_number}.py",
        ]
        for alt_path in alt_paths:
            if alt_path.exists():
                postprocessing = _load_callable_from_path(
                    f"gridos_postprocessing_{quest_num}_{part_number}",
                    alt_path,
                )
                if postprocessing is not None:
                    break

    results = run_cases_with_rules(
        {"cases": normalized_cases}, rules_path, postprocessing=postprocessing
    )

    if case_id is not None:
        results = [r for r in results if str(r["case"]) == str(case_id)]
        if not results:
            print(f"Error: case {case_id} not found for gridos quest {quest} part {part}")
            return

    total = len(results)
    failures = [r for r in results if not _gridos_result_matches(r)]
    total_steps = sum(r.get("steps", 0) for r in results)
    total_rules = sum(r.get("rules", 0) for r in results)
    total_states = sum(r.get("states", 0) for r in results)
    total_heads = max((r.get("heads", 0) for r in results), default=0)

    print(f"GridOS quest {quest} part {part} cases: {total}")
    if failures:
        print(f"  Failed: {len(failures)} / {total}")
    else:
        print(f"  Passed: {total} / {total}")
    print(
        f"  Heads: {total_heads}  States: {total_states}  Rules: {total_rules}  Steps: {total_steps}"
    )

    if failures and case_id is None:
        print("Failed cases:")
        for result in failures:
            print(
                f"  Case {result['case']}: output={result['output']} expected={result.get('expected')}"
            )
            if result.get("processed") is not None:
                print(
                    f"    processed={result['processed']} "
                    f"expected_processed={result.get('expected_processed')}"
                )

    if case_id is not None:
        for result in results:
            print(f"Case {result['case']} result:")
            print(f"  input = {result['input']}")
            print(f"  output = {result['output']}")
            print(f"  expected = {result.get('expected')}")
            print(
                f"  steps = {result.get('steps', 0)}, rules = {result.get('rules', 0)}, "
                f"states = {result.get('states', 0)}"
            )
            if result.get("processed") is not None:
                print(f"  processed = {result['processed']}")
                print(f"  expected_processed = {result.get('expected_processed')}")


def _gridos_result_matches(result: dict[str, Any]) -> bool:
    if result.get("processed") is not None:
        return result.get("processed") == result.get("expected_processed")
    return result["output"] == result["expected"]


def load_input_content(
    quest_dir, quest, test_mode, input_case: str | None = None
) -> dict[int, str]:
    """
    Load the raw input file content for a quest.
    """
    if test_mode:
        # If a specific case id was requested, prefer it over the generic 'test'
        case_id = input_case if input_case is not None else "test"
        parts_input: None | dict[int, str] = load_unified_case_content(
            quest_dir,
            quest,
            case_id,
        )
        if parts_input is not None:
            return parts_input
        # If user asked for a specific case and it wasn't found, raise
        if input_case is not None:
            raise FileNotFoundError(
                f"Case {input_case} not found in unified inputs for quest {quest}"
            )
        # Fallback to .test file if no id=test case exists in JSON
        file_path: str = os.path.join(quest_dir, f"quest_{quest}.test")
        with open(file_path, encoding="utf-8") as f:
            return normalize_part_input(f.read())

    # If a specific case id was specified, try unified JSON first, then per-part files
    if input_case is not None:
        unified_case: None | dict[int, str] = load_unified_case_content(
            quest_dir,
            quest,
            str(input_case),
        )
        if unified_case is not None:
            return unified_case
        # try per-part input files under year_dir/input/<part>/<case_id>
        year_dir = os.path.dirname(quest_dir)
        try:
            return load_input_set_case_content(year_dir, str(input_case))
        except FileNotFoundError:
            raise FileNotFoundError(f"Case {input_case} not found for quest {quest}")

    # Prefer personal input (id 41) from unified inputs when available.
    unified_case_zero: None | dict[int, str] = load_unified_case_content(
        quest_dir,
        quest,
        "41",
    )
    if unified_case_zero is not None:
        return unified_case_zero

    # Prefer centralized per-part input sets when available.
    input_sets_content: None | dict[int, str] = load_input_sets_content(
        quest_dir, quest
    )
    if input_sets_content is not None:
        return input_sets_content

    file_path: str = os.path.join(quest_dir, f"quest_{quest}.input")
    with open(file_path, encoding="utf-8") as f:
        return normalize_part_input(f.read())


def load_unified_case_content(quest_dir, quest, case_id) -> None | dict[int, str]:
    """
    Load and combine part inputs for a given case id from
    inputs_{quest_id}.json.
    """
    quest_id = f"{int(quest):02d}"
    all_inputs_file: str = os.path.join(quest_dir, f"inputs_{quest_id}.json")
    if not os.path.exists(all_inputs_file):
        # Backward compatibility with older unified file name.
        all_inputs_file = os.path.join(quest_dir, "inputs.json")
    if not os.path.exists(all_inputs_file):
        return None

    with open(all_inputs_file, encoding="utf-8") as f:
        all_inputs = json.load(f)

    for case in all_inputs.get("cases", []):
        if str(case.get("id", "")).strip() != case_id:
            continue

        case_input = case.get("input", {})
        return normalize_part_input(case_input)

    return None


def load_extra_content(quest_dir, quest) -> dict:
    """
    Load the 'extra' block from inputs_{quest}.json, or an empty dict if
    the file or key does not exist.
    """
    quest_id = f"{int(quest):02d}"
    all_inputs_file: str = os.path.join(quest_dir, f"inputs_{quest_id}.json")
    if not os.path.exists(all_inputs_file):
        all_inputs_file = os.path.join(quest_dir, "inputs.json")
    if not os.path.exists(all_inputs_file):
        return {}
    with open(all_inputs_file, encoding="utf-8") as f:
        return json.load(f).get("extra", {})


def load_input_sets_content(quest_dir, quest) -> None | dict[int, str]:
    """
    Build a combined content string from part-specific input sets
    located at events/year_<year>/input/{1,2,3}/<quest_number>.
    """
    year_dir = os.path.dirname(quest_dir)
    input_dir: str = os.path.join(year_dir, "input")
    quest_number = str(int(quest))
    part_paths: list[str] = [
        os.path.join(input_dir, str(part), quest_number) for part in range(1, 4)
    ]

    if not all(os.path.exists(path) for path in part_paths):
        return None

    part_contents = []
    for path in part_paths:
        with open(path, encoding="utf-8") as f:
            part_contents.append(f.read().rstrip("\n"))

    return {part: part_contents[part - 1] for part in range(1, 4)}


def _expects_test_mode(func) -> bool:
    """
    Heuristically determine whether a single-argument function expects a
    boolean test_mode argument.
    """
    try:
        sig: inspect.Signature = inspect.signature(func)
    except (TypeError, ValueError):
        return False

    params: list[inspect.Parameter] = list(sig.parameters.values())
    positional_params: list[inspect.Parameter] = [
        p
        for p in params
        if p.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    if len(positional_params) != 1:
        return False

    param: inspect.Parameter = positional_params[0]
    if param.annotation is bool:
        return True

    return "test" in param.name.lower()


def adapt_get_part_input(quest_module, parts_input) -> None:
    """
    Adapt get_part_input so content-based implementations also work when
    legacy solver code still passes a boolean test_mode value.
    """
    if not hasattr(quest_module, "get_part_input"):
        return

    original_get_part_input = quest_module.get_part_input
    if _expects_test_mode(original_get_part_input):
        return

    def _wrapped_get_part_input(arg):
        """
        Bridge legacy boolean callers to content-based get_part_input
        implementations.
        """
        if isinstance(arg, bool):
            return original_get_part_input(parts_input)
        if isinstance(arg, dict):
            try:
                return original_get_part_input(arg)
            except (TypeError, AttributeError):
                return original_get_part_input(parts_dict_to_content(arg))
        return original_get_part_input(arg)

    quest_module.get_part_input = _wrapped_get_part_input


def run_solver(quest_module, test_mode, parts_input):
    """
    Run solver using preprocessing output as solver input when available,
    while remaining compatible with existing test_mode/content-based solvers.
    """
    solver = quest_module.solver
    if _expects_test_mode(solver):
        return solver(test_mode)

    solver_input = parts_input
    preprocessing = getattr(quest_module, "preprocessing", None)
    if callable(preprocessing) and not _expects_test_mode(preprocessing):
        try:
            solver_input = preprocessing(parts_input)
        except (TypeError, AttributeError):
            solver_input = preprocessing(parts_dict_to_content(parts_input))

    try:
        return solver(solver_input)
    except TypeError:
        return solver(parts_input)


def load_input_set_case_content(year_dir, case_id) -> dict[int, str]:
    """
    Load and combine the three part-specific input files for one case id.
    """
    part_paths: list[str] = [
        os.path.join(year_dir, "input", str(part), str(case_id)) for part in range(1, 4)
    ]
    if not all(os.path.exists(path) for path in part_paths):
        raise FileNotFoundError(f"Missing input files for case {case_id}")

    parts = []
    for path in part_paths:
        with open(path, encoding="utf-8") as f:
            parts.append(f.read().rstrip("\n"))
    return {part: parts[part - 1] for part in range(1, 4)}


def build_inputs_json_from_everybody_codes(year_dir: str, quest: str) -> str:
    """
    Convert a legacy everybody_codes_e<year>_q<quest> folder into a unified
    inputs_{quest}.json file used by load_unified_case_content.

    This supports both older per-quest folder layouts and the new
    year-level layout. It searches `year_dir` for the legacy
    `everybody_codes_e<year>_q<quest>` folder, reads its `input/{1,2,3}`
    files and `answers.json`, and writes the unified `inputs_{qq}.json`
    into `year_dir/inputs/` when possible (creates the folder if needed),
    otherwise into `year_dir`.
    """
    year_name = os.path.basename(year_dir)
    if year_name.startswith("year_"):
        year = year_name.split("year_", 1)[1]
    else:
        year = year_name

    quest_num_padded = f"{int(quest):02d}"

    target_folder_name = f"everybody_codes_e{year}_q{quest_num_padded}"

    # Search for the legacy folder inside year_dir
    found_old = None
    for root, dirs, files in os.walk(year_dir):
        if target_folder_name in dirs:
            found_old = os.path.join(root, target_folder_name)
            break

    if not found_old:
        # Also accept the legacy folder directly under year_dir
        cand = os.path.join(year_dir, target_folder_name)
        if os.path.isdir(cand):
            found_old = cand

    if not found_old:
        raise FileNotFoundError(
            f"Missing legacy everybody_codes folder: {target_folder_name} under {year_dir}"
        )

    old_folder = found_old
    answers_file = os.path.join(old_folder, "answers.json")
    if not os.path.exists(answers_file):
        raise FileNotFoundError(f"Missing answers.json in {old_folder}")

    with open(answers_file, encoding="utf-8") as f:
        answers = json.load(f)

    expected_p1 = answers.get("p1", {}) or {}
    expected_p2 = answers.get("p2", {}) or {}
    expected_p3 = answers.get("p3", {}) or {}

    input_root = os.path.join(old_folder, "input")
    if not os.path.isdir(input_root):
        raise FileNotFoundError(f"Missing input folder in {old_folder}")

    ids = set()
    for part in range(1, 4):
        part_dir = os.path.join(input_root, str(part))
        if os.path.isdir(part_dir):
            ids.update(
                [name for name in os.listdir(part_dir) if not name.startswith(".")]
            )

    def sort_key(case_id: str):
        if case_id.isdigit():
            return (0, int(case_id))
        return (1, case_id)

    sorted_ids = sorted(ids, key=sort_key)

    cases = []

    # Test case from any existing quest_{quest}.test file under year_dir
    test_file_candidates = [
        os.path.join(year_dir, f"quest_{quest_num_padded}.test"),
        os.path.join(year_dir, "inputs", f"quest_{quest_num_padded}.test"),
    ]
    for test_file in test_file_candidates:
        if os.path.exists(test_file):
            with open(test_file, encoding="utf-8") as f:
                test_input = normalize_part_input(f.read())
            cases.append(
                {
                    "id": "test",
                    "input": {str(p): test_input.get(p, "") for p in range(1, 4)},
                }
            )
            break

    for case_id in sorted_ids:
        case_input = {}
        for part in range(1, 4):
            part_path = os.path.join(input_root, str(part), case_id)
            if os.path.exists(part_path):
                with open(part_path, encoding="utf-8") as f:
                    case_input[str(part)] = f.read().rstrip("\n")
            else:
                case_input[str(part)] = ""
        expected = {
            "1": str(
                expected_p1.get(
                    str(case_id),
                    expected_p1.get(int(case_id) if case_id.isdigit() else case_id, ""),
                )
            ),
            "2": str(
                expected_p2.get(
                    str(case_id),
                    expected_p2.get(int(case_id) if case_id.isdigit() else case_id, ""),
                )
            ),
            "3": str(
                expected_p3.get(
                    str(case_id),
                    expected_p3.get(int(case_id) if case_id.isdigit() else case_id, ""),
                )
            ),
        }

        cases.append(
            {
                "id": str(case_id),
                "input": case_input,
                "expected": expected,
            }
        )

    output = {
        "event": str(year),
        "quest": str(int(quest_num_padded)),
        "source": {
            "answers": "answers.json",
            "inputs": "input/{1,2,3}/<id>",
        },
        "cases": cases,
    }

    # Prefer writing into year_dir/inputs/
    inputs_dir = os.path.join(year_dir, "inputs")
    if not os.path.isdir(inputs_dir):
        try:
            os.makedirs(inputs_dir, exist_ok=True)
        except Exception:
            inputs_dir = year_dir

    output_file = os.path.join(inputs_dir, f"inputs_{quest_num_padded}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return output_file


def load_quest_module(quest_file, quest) -> types.ModuleType:
    """
    Import and return a quest module from the given file path.
    """
    spec: ModuleSpec | None = importlib.util.spec_from_file_location(
        f"quest_{quest}", quest_file
    )
    if spec is None or spec.loader is None:
        loader = SourceFileLoader(f"quest_{quest}", quest_file)
        spec: ModuleSpec | None = importlib.util.spec_from_loader(
            f"quest_{quest}", loader
        )
        assert spec is not None
        quest_module: types.ModuleType = importlib.util.module_from_spec(spec)
        loader.exec_module(quest_module)
    else:
        assert spec is not None and spec.loader is not None
        quest_module: types.ModuleType = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(quest_module)
    return quest_module


def run_all_inputs(
    script_dir,
    year,
    event,
    quest_override,
    only_part: int | None = None,
    input_case: str | None = None,
):
    """
    Validate all cases from unified inputs.json.
    """
    if event != "events":
        print("-all is currently supported for events only")
        return
    year_dir: str = os.path.join(script_dir, f"events/year_{year}")
    quest = (quest_override or "01").zfill(2)
    if not quest:
        print("Error: Could not determine quest for -all run")
        return

    # Candidates for unified inputs (support legacy per-quest folder and
    # new year-level inputs/ folder)
    quest_dir_old: str = os.path.join(year_dir, f"quest_{quest}")
    candidates = [
        os.path.join(quest_dir_old, f"inputs_{quest}.json"),
        os.path.join(year_dir, f"inputs_{quest}.json"),
        os.path.join(year_dir, "inputs", f"inputs_{quest}.json"),
        os.path.join(quest_dir_old, "inputs.json"),
        os.path.join(year_dir, "inputs.json"),
    ]

    all_inputs_file = next((p for p in candidates if os.path.exists(p)), None)
    if all_inputs_file is None:
        print(f"Error: Missing unified file for quest {quest} (checked {candidates})")
        return

    with open(all_inputs_file, encoding="utf-8") as f:
        all_inputs = json.load(f)

    # Locate the quest module in either the new solutions/ layout or legacy
    quest_file_candidates = [
        os.path.join(year_dir, "solutions", f"quest_{quest}.py"),
        os.path.join(quest_dir_old, f"quest_{quest}.py"),
    ]
    quest_file = next((p for p in quest_file_candidates if os.path.exists(p)), None)
    if quest_file is None:
        print(f"Error: Missing quest file (checked {quest_file_candidates})")
        return

    mode_note = "(-all"
    if only_part is not None:
        mode_note += f" part{only_part}"
    if input_case is not None:
        mode_note += f" input={input_case}"
    mode_note += ")"
    print(f"Year {year} Quest {quest} {mode_note}:")

    if input_case is not None:
        cases = [
            case
            for case in all_inputs.get("cases", [])
            if str(case.get("id", "")).strip() == str(input_case)
        ]
        if not cases:
            print(f"Error: case {input_case} not found in {all_inputs_file}")
            return
    else:
        cases: list[Any] = [
            case
            for case in all_inputs.get("cases", [])
            if str(case.get("id", "")).strip() not in ("", "test")
        ]
    total_cases: int = len(cases)

    total = 0
    passed = 0
    case_times: list[float] = []

    for case_num, case in enumerate(cases, 1):
        case_id: str = str(case.get("id", "")).strip()
        expected = case.get("expected", {})

        total += 1
        start = time.perf_counter()
        got = ""
        expected_val = ""
        try:
            case_input = case.get("input", {})
            parts_input: dict[int, str] = normalize_part_input(case_input)
            quest_module: types.ModuleType = load_quest_module(quest_file, quest)
            adapt_get_part_input(quest_module, parts_input)
            results: list[str] = [
                str(r)
                for r in run_solver(
                    quest_module,
                    False,
                    parts_input,
                )
            ]
            expected_parts: list[str] = [
                str(expected.get("1", "")),
                str(expected.get("2", "")),
                str(expected.get("3", "")),
            ]
            if only_part is None:
                ok: bool = results[:3] == expected_parts
            else:
                idx = only_part - 1
                got = results[idx] if idx < len(results) else ""
                expected_val = expected_parts[idx]
                ok = str(got) == str(expected_val)
        except Exception as exc:  # pylint: disable=broad-except
            ok = False
            print(exc)
            results: list[str] = [f"ERROR: {exc}"]
            expected_parts: list[str] = [
                str(expected.get("1", "")),
                str(expected.get("2", "")),
                str(expected.get("3", "")),
            ]
            if only_part is not None:
                idx = only_part - 1
                got = results[0]
                expected_val = expected_parts[idx] if idx < len(expected_parts) else ""
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            case_times.append(elapsed_ms)

        if ok:
            passed += 1
        else:
            print()
            if only_part is None:
                print(
                    (
                        f"  Case {case_id}: FAIL "
                        f"got={results} expected={expected_parts} "
                        f"({elapsed_ms:.2f} ms)"
                    )
                )
            else:
                print(
                    (
                        f"  Case {case_id}: FAIL "
                        f"got_part{only_part}={got} expected={expected_val} "
                        f"({elapsed_ms:.2f} ms)"
                    )
                )

        if total_cases:
            progress_percent = int(case_num * 100 / total_cases)
            print(
                f"\r  Progress: {case_num}/{total_cases} ({progress_percent}%)",
                end="",
                flush=True,
            )

    if total_cases:
        print()

    print(f"  Summary: {passed}/{total} passed")
    if case_times:
        mean_ms = sum(case_times) / len(case_times)
        print(f"  Mean time per input: {mean_ms:.2f} ms")


def main() -> None:
    """
    Entry point that validates CLI arguments, loads and executes the specified
    quest solver module (optionally in test mode), and prints each part's
    result.
    """
    if len(sys.argv) < 2:
        print("Usage: python ec.py <year> [quest] [-test] [-all] [-case <id>]")
        print("Examples:")
        print(("  python ec.py 2024        # Run all quests of 2024 with real input"))
        print(
            (
                "  python ec.py 2024 -all   "
                "# Validate all set inputs for the configured quest"
            )
        )
        print(("  python ec.py 2024 01     # Run quest 01 of 2024 with real input"))
        print(("  python ec.py 2024 01 -all # Validate all set inputs for quest 01"))
        print(("  python ec.py 2024 01 -test # Run quest 01 of 2024 with test input"))
        print(("  python ec.py 2024 01 -case 1 # Run quest 01 with input case id 1"))
        print(("  python ec.py 3001 1 1   # Run GridOS quest 1 part 1 for event 3001"))
        sys.exit(1)

    year: str = sys.argv[1]
    print("year: ", year)
    if len(year) <= 2:
        event = "stories"
        year = year.zfill(2)
    elif year.startswith('3') and len(year) == 4:
        event = "gridos"
        year = year[2:]
    else:
        event = "events"

    args: list[str] = sys.argv[2:]
    # parse -input / -case <id> first and remove it from args to keep positional parsing clean
    input_case: str | None = None
    for case_flag in ("-input", "-case"):
        if case_flag in args:
            try:
                idx = args.index(case_flag)
                input_case = args[idx + 1]
                del args[idx : idx + 2]
            except Exception:
                print(f"Error: {case_flag} requires a case id argument")
                sys.exit(1)
            break

    # detect -all1/-all2/-all3 to allow validating a single part across all cases
    only_all_part: int | None = None
    for pflag in ("-all1", "-all2", "-all3"):
        if pflag in args:
            only_all_part = int(pflag[-1])
            break
    test_mode: bool = "-test" in args
    all_mode: bool = ("-all" in args) or (only_all_part is not None)
    positional: list[str] = [a for a in args if not a.startswith("-")]

    if all_mode and test_mode:
        print("Error: -all and -test cannot be combined")
        sys.exit(1)

    build_mode: bool = "-build-inputs" in args
    script_dir: str = os.path.dirname(os.path.abspath(__file__))

    if build_mode:
        quest: str = positional[0].zfill(2) if positional else "01"
        year_dir: str = os.path.join(script_dir, f"events/year_{year}")

        try:
            output_file = build_inputs_json_from_everybody_codes(year_dir, quest)
            print(f"Built: {output_file}")
        except Exception as exc:
            print(f"Error building inputs: {exc}")
            sys.exit(1)
        return

    if event == "gridos":
        if all_mode:
            print("Error: -all is not supported for gridos mode")
            sys.exit(1)
        if not positional:
            print("Usage: python ec.py 3001 <quest> [part]")
            sys.exit(1)

        quest: str = positional[0].zfill(2)
        if len(positional) >= 2:
            part_arg = positional[1]
            if not part_arg.isdigit() or int(part_arg) not in (1, 2, 3):
                print("Error: Gridos part must be 1, 2, or 3")
                sys.exit(1)
            run_gridos(event, quest, str(int(part_arg)), year, case_id=input_case)
            return

        # If part is omitted, run all three parts for the given quest.
        for part_arg in ("1", "2", "3"):
            run_gridos(event, quest, part_arg, year, case_id=input_case)
        return

    if all_mode:
        quest: str | None = positional[0].zfill(2) if positional else None
        run_all_inputs(
            script_dir,
            year,
            event,
            quest,
            only_part=only_all_part,
            input_case=input_case,
        )
    elif positional and positional[0].lower() in ("all1", "all2", "all3"):
        # Support shorthand to run a single part across all quests: all1/all2/all3
        qflag = positional[0].lower()
        part_num = int(qflag[-1])
        run_quests(
            year, event, None, test_mode, only_part=part_num, input_case=input_case
        )
    elif positional:
        quest: str = positional[0].zfill(2)
        run_quests(year, event, quest, test_mode, input_case=input_case)
    else:
        run_quests(year, event, None, test_mode, input_case=input_case)


if __name__ == "__main__":
    main()
