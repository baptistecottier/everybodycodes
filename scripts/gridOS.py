from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

OutputTapes = list[str]


class GridOSTuringMachine:
    """A Turing machine implementation for grid-based operations.

    This class simulates a multi-head Turing machine that operates on a 2D grid.
    It maintains state, transitions, and head positions to process grid data.
    """

    def __init__(self, instructions_text: str, initial_grid_lines: list[str]):
        self.grid: dict[tuple[int, int], str] = {}
        self.heads: list[list[int]] = []
        self.head_labels: list[str] = []
        self.state = "START"
        self.transitions: list[dict[str, str]] = []
        self.head_order: list[str] = []
        self.grid_height = 0
        self.grid_width = 0
        self.start_pos: list[int] = [0, 0]
        self.last_rule_index: int | None = None
        self.last_move_count = 0

        self._parse_grid(initial_grid_lines)
        self._parse_instructions(instructions_text)

    def _initial_head_positions(self, labels: list[str]) -> list[list[int]]:
        max_row = max(self.grid_height - 1, 0)
        max_col = max(self.grid_width - 1, 0)
        positions = {
            "A": [0, 0],
            "B": [0, max_col],
            "C": [max_row, max_col],
            "D": [max_row, 0],
        }
        return [list(positions.get(label, [0, 0])) for label in labels]

    def _parse_grid(self, lines: list[str]) -> None:
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                if char != " ":
                    self.grid[(r, c)] = char
        self.grid_height = len(lines)
        self.grid_width = max((len(line) for line in lines), default=0)
        self.start_pos = [0, 0]

    def _parse_instructions(self, text: str) -> None:
        lines = [
            l.strip()
            for l in text.strip().split("\n")
            if l.strip() and not l.strip().startswith("#")
        ]

        if not lines:
            self.head_order = []
            return

        if lines[0].startswith("HEADS"):
            parts = lines[0].split()
            if len(parts) >= 2:
                self.head_labels = list(parts[1])
                self.heads = self._initial_head_positions(self.head_labels)
            lines = lines[1:]

        self.head_order = list(self.head_labels)

        for line in lines:
            parts = line.split()
            if len(parts) != 5:
                continue
            self.transitions.append({
                "curr_state": parts[0],
                "read": parts[1],
                "next_state": parts[2],
                "write": parts[3],
                "dirs": parts[4],
            })

    def step(self, verbose: bool = False) -> bool:
        current_reads = "".join(
            self.grid.get(tuple(head_pos), "_") for head_pos in self.heads
        )

        matched_rule = None
        matched_index = None
        for idx, rule in enumerate(self.transitions):
            if rule["curr_state"] != self.state:
                continue

            match = True
            for i, char in enumerate(current_reads):
                rule_char = rule["read"][i]
                if rule_char == "*":
                    continue
                elif rule_char == "!":
                    if char == "_":
                        match = False
                        break
                elif rule_char != char:
                    match = False
                    break

            if match:
                matched_rule = rule
                matched_index = idx
                break

        if not matched_rule:
            self.last_rule_index = None
            self.last_move_count = 0
            if verbose:
                print(
                    f"Halted: No rule found for State: {self.state}. "
                    f"Head positions: {self.heads} (Read: '{current_reads}')"
                )
            return False

        self.last_rule_index = matched_index
        self.last_move_count = 1

        self.state = matched_rule["next_state"]
        for i, pos in enumerate(self.heads):
            write_char = matched_rule["write"][i]
            if write_char != "*":
                self.grid[(pos[0], pos[1])] = write_char

        for i, pos in enumerate(self.heads):
            d = matched_rule["dirs"][i]
            if d == "U":
                pos[0] -= 1
            elif d == "D":
                pos[0] += 1
            elif d == "L":
                pos[1] -= 1
            elif d == "R":
                pos[1] += 1

        return self.state != "STOP"

    def _count_states(self) -> int:
        states = set()
        for rule in self.transitions:
            states.add(rule["curr_state"])
            states.add(rule["next_state"])
        return len(states)

    def run(self, max_steps: int = 50000, verbose: bool = False) -> dict[str, Any]:
        steps = 0
        used_rule_indexes: set[int] = set()
        visited_states = {self.state}

        while steps < max_steps:
            continued = self.step(verbose=verbose)
            if self.last_rule_index is not None:
                used_rule_indexes.add(self.last_rule_index)
            visited_states.add(self.state)
            steps += self.last_move_count

            if self.state == "STOP":
                break

            if not continued:
                break
        return {
            "output": self.get_clean_grid(),
            "heads": len(self.head_order),
            "states": len(visited_states),
            "rules": len(used_rule_indexes),
            "steps": steps,
            "used_rule_indexes": sorted(used_rule_indexes),
        }

    def get_clean_grid(self) -> str:
        if not self.grid:
            return ""
        min_r = min(r for r, c in self.grid.keys())
        max_r = max(r for r, c in self.grid.keys())
        min_c = min(c for r, c in self.grid.keys())
        max_c = max(c for r, c in self.grid.keys())

        output: list[str] = []
        for r in range(min_r, max_r + 1):
            row_str = "".join(
                [self.grid.get((r, c), "_") for c in range(min_c, max_c + 1)]
            )
            output.append(row_str)
        return "\n".join(output)


def load_cases(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_callable_from_path(
    module_name: str,
    module_path: Path,
) -> Callable[[OutputTapes], Any] | None:
    if not module_path.exists():
        return None

    module = _load_module_from_path(module_name, module_path)
    if hasattr(module, "postprocessing"):
        return getattr(module, "postprocessing")
    return None


def _part_metadata(part_name: str, quest: str) -> tuple[str, str, str]:
    part_roman = {
        "part_i": "I",
        "part_ii": "II",
        "part_iii": "III",
    }.get(part_name)
    if part_roman is None:
        raise ValueError(f"Invalid part name: {part_name}")
    part_number = {"I": "1", "II": "2", "III": "3"}[part_roman]
    quest_num = str(int(quest))
    quest_id = f"{int(quest):02d}"
    return quest_num, quest_id, part_number


def load_part_rules(
    part_name: str,
    quest: str | None = None,
    base_dir: Path | None = None,
) -> Path:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent

    if quest is not None:
        quest_num, quest_id, part_number = _part_metadata(part_name, quest)
        part_roman = {
            "part_i": "I",
            "part_ii": "II",
            "part_iii": "III",
        }[part_name]
        quest_part_dir = (
            base_dir
            / "gridos_tournament"
            / f"quest_{quest_num}"
            / f"part_{part_roman}"
        )

        legacy_path = quest_part_dir / f"q{quest_num}p{part_number}.rules"
        if legacy_path.exists():
            return legacy_path

    raise FileNotFoundError(
        f"GridOS rule file not found for quest {quest} part {part_name}"
    )


def load_part_postprocessing(
    part_name: str,
    quest: str | None = None,
    base_dir: Path | None = None,
) -> Callable[[OutputTapes], Any] | None:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent

    if quest is not None:
        quest_num, quest_id, part_number = _part_metadata(part_name, quest)
        part_roman = {
            "part_i": "I",
            "part_ii": "II",
            "part_iii": "III",
        }[part_name]
        quest_dir = base_dir / "gridos_tournament" / f"quest_{quest_num}"

        module = _load_callable_from_path(
            f"postprocessing_q{quest_num}",
            quest_dir / "postprocessing.py",
        )
        if module is not None:
            return module

        module = _load_callable_from_path(
            f"postprocessing_q{quest_num}p{part_number}",
            quest_dir / f"part_{part_roman}" / "postprocessing.py",
        )
        if module is not None:
            return module

        module = _load_callable_from_path(
            f"postprocessing_q{quest_num}p{part_number}",
            quest_dir
            / f"part_{part_roman}"
            / f"postprocessing_q{quest_num}p{part_number}.py",
        )
        if module is not None:
            return module
    return None


def _get_input_symbols(cases: list[dict[str, Any]]) -> set[str]:
    symbols: set[str] = set()
    for case in cases['cases']:
        symbols.update(str(case['data']))
    return symbols


def count_effective_heads(rules_text: str) -> int:
    lines = [
        line.strip()
        for line in rules_text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    for line in lines:
        if line.split()[0] == "HEADS":
            return len(line.split()[1])

    return 0


def _normalize_grid_output(output_text: str) -> OutputTapes:
    if not output_text:
        return [""]

    lines = output_text.splitlines()
    if len(lines) == 1:
        return [lines[0].rstrip()]

    return lines


def _normalize_expected_output(expected: Any) -> OutputTapes:
    if expected is None:
        return [""]
    if isinstance(expected, list):
        return [str(line) for line in expected]
    return _normalize_grid_output(str(expected))


def _count_visible_symbols(output_tapes: OutputTapes | None) -> int | None:
    if output_tapes is None:
        return None
    return sum(sum(1 for char in tape if char != " ") for tape in output_tapes)


def run_cases_with_rules(
    cases: list[dict[str, Any]],
    rules_path: Path,
    postprocessing: Callable[[OutputTapes], Any] | None = None,
    max_steps: int = 50000,
) -> list[dict[str, Any]]:
    rules_text = rules_path.read_text(encoding="utf-8")
    results: list[dict[str, Any]] = []

    input_symbols = _get_input_symbols(cases)
    effective_heads = count_effective_heads(rules_text, input_symbols)

    for case in cases['cases']:
        input_values = case.get("data", [])
        grid_lines = [str(value) for value in input_values]
        interpreter = GridOSTuringMachine(rules_text, grid_lines)
        run_result = interpreter.run(max_steps=max_steps)

        output_text = run_result.get("output", "") or ""
        output_tapes = _normalize_grid_output(output_text)
        processed = (
            postprocessing(output_tapes) if postprocessing is not None else None
        )

        expected_tapes = _normalize_expected_output(case.get("expected"))
        expected_processed = (
            postprocessing(expected_tapes)
            if postprocessing is not None
            else _count_visible_symbols(expected_tapes)
        )
        results.append(
            {
                "case": case.get("case"),
                "input": grid_lines,
                "expected": case.get("expected"),
                "expected_processed": expected_processed,
                "output": output_tapes,
                "processed": processed,
                "steps": run_result.get("steps", 0),
                "rules": run_result.get("rules", 0),
                "states": run_result.get("states", 0),
                "heads": effective_heads,
                "used_rule_indexes": run_result.get("used_rule_indexes", []),
            }
        )

    return results


def count_symbol(output_tapes: OutputTapes, symbol: str = "P") -> int:
    return sum(tape.count(symbol) for tape in output_tapes)


def apply_output_processor(output_tapes: OutputTapes, processor: Callable[[OutputTapes], Any]) -> Any:
    return processor(output_tapes)


def load_part_cases(
    part_name: str,
    quest: str | None = None,
    base_dir: Path | None = None,
) -> list[dict[str, Any]]:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent

    if quest is not None:
        quest_id = f"{int(quest):02d}"
        legacy_path = base_dir / f"quest_{quest_id}_{part_name}.json"
        if legacy_path.exists():
            return load_cases(legacy_path)

        part_roman = {
            "part_i": "I",
            "part_ii": "II",
            "part_iii": "III",
        }.get(part_name)
        if part_roman is not None:
            part_number = {"I": "1", "II": "2", "III": "3"}[part_roman]
            quest_num = str(int(quest))
            alt_path = base_dir / "gridos_tournament" / f"quest_{quest_num}" / f"part_{part_roman}" / f"test_cases_q{quest_num}p{part_number}.json"
            if alt_path.exists():
                return load_cases(alt_path)

    path = base_dir / f"quest_01_{part_name}.json"
    return load_cases(path)
