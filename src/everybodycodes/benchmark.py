#!/usr/bin/env python3

"""
Benchmark every solution against the known answers, store the results in
src/everybodycodes/benchmarks.json and regenerate the scoreboards.

Each quest runs in its own process with a timeout (5 minutes by default). The
measured time covers preprocessing and solving the three parts, not interpreter
start-up or imports. Inputs are the personal ones cached by the Puzzle
Submitter extension; expected answers are the ones it recorded as correct,
completed by the expected answers of the personal case (id 41) of the inputs
JSON files. A part with no known answer cannot be verified.

Examples:
    uv run src/everybodycodes/benchmark.py                    # everything
    uv run src/everybodycodes/benchmark.py 2024               # one event
    uv run src/everybodycodes/benchmark.py story3             # one story
    uv run src/everybodycodes/benchmark.py 2025 --quests 1-5  # some quests
    uv run src/everybodycodes/benchmark.py --changed          # what changed
    uv run src/everybodycodes/benchmark.py --render           # redraw only
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import platform
import re
import signal
import sqlite3
import subprocess
import sys
import threading
import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from urllib.parse import unquote, urlparse

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
RESULTS = PACKAGE / "benchmarks.json"
INPUT_STORE = ROOT / ".puzzle-submitter" / "everybodycodes.json"
EXTENSION = "baptistecottier.puzzle-submitter"
PERSONAL_CASE = "41"
KINDS = ("events", "stories")


# ===========================================================================
# Calendar
# ===========================================================================


def quests_in(kind: str) -> int:
    """Number of quests: 20 for an event, 3 for a story."""
    return 20 if kind == "events" else 3


def event_dir(kind: str, number: int) -> Path:
    """Folder of an event (events/year_2024) or a story (stories/story_01)."""
    return PACKAGE / (
        f"events/year_{number}"
        if kind == "events"
        else f"stories/story_{number:02}"
    )


def solution_path(kind: str, number: int, quest: int) -> Path:
    """Path of the solution file of a quest."""
    return event_dir(kind, number) / "solutions" / f"quest_{quest:02}.py"


def has_solution(kind: str, number: int, quest: int) -> bool:
    """Whether a quest has a solution (an empty file has none)."""
    path = solution_path(kind, number, quest)
    return path.is_file() and bool(path.read_text(encoding="utf-8").strip())


def known_events(inputs: dict) -> list[tuple[str, int]]:
    """Events and stories with a solution or a cached input: (kind, number)."""
    found = set()
    for kind, pattern in (("events", "year_*"), ("stories", "story_*")):
        for folder in (PACKAGE / kind).glob(pattern):
            number = int(folder.name.split("_")[1])
            if any(
                has_solution(kind, number, q)
                for q in range(1, quests_in(kind) + 1)
            ):
                found.add((kind, number))
    for key in inputs:
        found.add(("events" if int(key) >= 2000 else "stories", int(key)))
    return sorted(found)


# ===========================================================================
# Inputs and expected answers
# ===========================================================================


def load_inputs() -> dict:
    """Personal inputs from the store shared with Puzzle Submitter."""
    with open(INPUT_STORE, encoding="utf-8") as f:
        return json.load(f)


def puzzle_input(
    inputs: dict, number: int, quest: int
) -> dict[str, str] | None:
    """Input of each part of a quest without trailing newlines, or None."""
    parts = inputs.get(str(number), {}).get(str(quest))
    if not parts:
        return None
    return {part: str(text).rstrip("\n") for part, text in parts.items()}


def _workspace_storages() -> list[Path]:
    """VS Code's per-workspace storage folders (stable and Insiders)."""
    bases = [
        Path.home() / "Library/Application Support",
        Path.home() / ".config",
        Path(os.environ.get("APPDATA", Path.home())),
    ]
    return [
        base / app / "User/workspaceStorage"
        for base in bases
        for app in ("Code", "Code - Insiders")
    ]


def load_answers() -> dict[tuple[int, int], dict]:
    """
    Answers recorded as correct by Puzzle Submitter for this repository, as
    {(event, quest): {"1": answer, "2": answer, "3": answer}}. They live in the
    extension's workspace state, inside the VS Code workspace storage of this
    repository.
    """
    answers: dict[tuple[int, int], dict] = {}
    for storage in _workspace_storages():
        for workspace in storage.glob("*/workspace.json"):
            try:
                folder = json.loads(workspace.read_text(encoding="utf-8")).get(
                    "folder", ""
                )
            except (OSError, json.JSONDecodeError):
                continue
            if unquote(urlparse(folder).path).rstrip("/") != str(ROOT):
                continue
            database = workspace.with_name("state.vscdb").as_uri() + "?mode=ro"
            try:
                with closing(
                    sqlite3.connect(database, uri=True)
                ) as connection:
                    row = connection.execute(
                        "SELECT value FROM ItemTable WHERE key = ?",
                        (EXTENSION,),
                    ).fetchone()
            except sqlite3.Error:
                continue
            state = json.loads(row[0]) if row else {}
            for key, recorded in state.items():
                match = re.fullmatch(
                    r"puzzleSubmitter\.progress\.everybodycodes\.(\d+)\.(\d+)",
                    key,
                )
                if match and isinstance(recorded, dict):
                    answers.setdefault(
                        (int(match[1]), int(match[2])), {}
                    ).update(recorded)
    return answers


def case_answers(kind: str, number: int, quest: int) -> dict:
    """Expected answers of the personal case in the inputs JSON of a quest."""
    path = event_dir(kind, number) / "inputs" / f"inputs_{quest:02}.json"
    try:
        cases = json.loads(path.read_text(encoding="utf-8")).get("cases", [])
    except (OSError, json.JSONDecodeError):
        return {}
    return next(
        (
            case.get("expected", {})
            for case in cases
            if str(case.get("id")) == PERSONAL_CASE
        ),
        {},
    )


def expected_answers(
    answers: dict, kind: str, number: int, quest: int
) -> list[str | None]:
    """
    Known answer of each part: recorded by Puzzle Submitter, else from the
    inputs JSON.
    """
    recorded = answers.get((number, quest), {})
    cases = case_answers(kind, number, quest)
    expected = []
    for part in ("1", "2", "3"):
        answer = recorded.get(part) or cases.get(part)
        expected.append(
            str(answer).strip() if answer not in (None, "", []) else None
        )
    return expected


def quest_title(kind: str, number: int, quest: int) -> str | None:
    """Title of a quest, from the 'Quest:' line of its solution's docstring."""
    try:
        text = solution_path(kind, number, quest).read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r'^\s*"""(.*?)"""', text, re.DOTALL)
    title = (
        re.search(r"^Quest:\s*(.+?)\s*$", match[1], re.MULTILINE)
        if match
        else None
    )
    return title[1] if title else None


def fingerprint(path: Path) -> str | None:
    """Git object id of a file as in the working tree, None if missing."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# ===========================================================================
# Running a solution
# ===========================================================================


def _normalise(answer) -> str:
    """String form of an answer, as it would be submitted."""
    if isinstance(answer, float) and answer.is_integer():
        answer = int(answer)
    return str(answer).strip()


def child(path: str) -> None:
    """
    Run one solution on the parts read from stdin as JSON, the way Puzzle
    Submitter does: preprocessing({1: ..., 2: ..., 3: ...}), then solver() on
    its result. Each answer is written to stdout as a JSON line as soon as it
    is known, so that a timeout keeps the parts already solved. Everything the
    solution prints is discarded.
    """
    out = os.fdopen(os.dup(1), "w", encoding="utf-8")
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 1)
    os.dup2(devnull, 2)

    def emit(**message):
        out.write(json.dumps(message) + "\n")
        out.flush()

    data = {
        int(part): text for part, text in json.loads(sys.stdin.read()).items()
    }
    sys.path.insert(0, str(ROOT))
    try:
        spec = importlib.util.spec_from_file_location(
            "benchmarked_solution", path
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        start = time.perf_counter()
        args = (
            module.preprocessing(data)
            if hasattr(module, "preprocessing")
            else data
        )
        result = module.solver(args)
        if not isinstance(result, Iterable) or isinstance(
            result, (str, bytes, dict)
        ):
            result = (result,)
        for item in result:
            emit(answer=_normalise(item), time=time.perf_counter() - start)
        emit(done=time.perf_counter() - start)
    except BaseException as exc:  # pylint: disable=broad-except
        emit(error=f"{type(exc).__name__}: {str(exc)[:200]}")
    out.close()
    os._exit(
        0
    )  # do not wait for threads or processes left behind by the solution


def run(path: Path, data: dict[str, str], timeout: float) -> dict:
    """Run one solution in its own process and collect its answers."""
    command = [sys.executable, __file__, "--child", str(path)]
    with subprocess.Popen(
        command,
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        start_new_session=True,
    ) as process:
        try:
            output, _ = process.communicate(json.dumps(data), timeout=timeout)
            timed_out = False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            output, _ = process.communicate()
            timed_out = True
        _kill_group(process.pid)

    answers, total, error = [], None, None
    for line in output.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "answer" in message:
            answers.append(message["answer"])
        elif "done" in message:
            total = message["done"]
        elif "error" in message:
            error = message["error"]
    if (
        total is not None
    ):  # answered in time, only a leftover process was still running
        timed_out = False
    if not timed_out and total is None and error is None:
        error = f"exited with code {process.returncode}"
    return {
        "answers": answers,
        "time": total,
        "timeout": timed_out,
        "error": error,
    }


def _kill_group(pgid: int) -> None:
    """Kill whatever a solution left behind in its process group."""
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


# ===========================================================================
# Benchmark
# ===========================================================================


def grade(run_result: dict, expected: list[str | None]) -> dict:
    """Compare a run with the expected answers, keep what the board needs."""
    parts = []
    for index, answer in enumerate(expected):
        given = (
            run_result["answers"][index]
            if index < len(run_result["answers"])
            else None
        )
        if given is None:
            parts.append("missing")
        elif answer is None:
            parts.append("unknown")
        else:
            parts.append("ok" if given == answer else "wrong")
    if run_result["timeout"]:
        status = "timeout"
    elif all(part == "ok" for part in parts):
        status = "solved"
    elif run_result["error"]:
        status = "error"
    else:
        status = "wrong"
    result = {
        "status": status,
        "parts": parts,
        "time": round(run_result["time"], 4)
        if run_result["time"] is not None
        else None,
        "date": datetime.date.today().isoformat(),
    }
    if run_result["error"]:
        result["error"] = run_result["error"]
    return result


def load_results() -> dict:
    """Previous results, so that a partial run only updates what it ran."""
    if RESULTS.is_file():
        with open(RESULTS, encoding="utf-8") as f:
            return json.load(f)
    return {"meta": {}, **{kind: {} for kind in KINDS}}


def save_results(results: dict) -> None:
    """Write the results, sorted, one line per quest so diffs stay readable."""
    blocks = []
    for kind in KINDS:
        events = []
        for number, quests in sorted(
            results.get(kind, {}).items(), key=lambda e: int(e[0])
        ):
            lines = [
                f'      "{quest}": {json.dumps(entry, ensure_ascii=False)}'
                for quest, entry in sorted(
                    quests.items(), key=lambda q: int(q[0])
                )
            ]
            events.append(
                f'    "{number}": {{\n' + ",\n".join(lines) + "\n    }"
            )
        blocks.append(f'  "{kind}": {{\n' + ",\n".join(events) + "\n  }")
    with open(RESULTS, "w", encoding="utf-8") as f:
        f.write(
            '{\n  "meta": '
            + json.dumps(results["meta"], ensure_ascii=False)
            + ",\n"
        )
        f.write(",\n".join(blocks) + "\n}\n")


def describe(result: dict) -> str:
    """One-line summary of a result for the console."""
    stars = "".join("★" if part == "ok" else "☆" for part in result["parts"])
    if result["status"] == "timeout":
        return f"{stars} timeout"
    if result["time"] is None:
        return f"{stars} {result.get('error', result['status'])}"
    return f"{stars} {result['time']:.3f}s {result['status']}"


def machine() -> str:
    """Short description of the machine running the benchmark."""
    try:
        return subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return platform.processor() or platform.machine()


def outdated(
    result: dict | None, code: str | None, expected: list[str | None]
) -> bool:
    """
    Whether a result needs a new run: never measured, measured on other code,
    or with an answer that could not be verified then but can be now.
    """
    if result is None or result.get("code") != code:
        return True
    return any(
        part == "unknown" and answer is not None
        for part, answer in zip(result["parts"], expected)
    )


def benchmark(
    targets: list[tuple[str, int]],
    quests: list[int] | None,
    timeout: float,
    jobs: int,
    changed: bool = False,
) -> None:
    """
    Run the selected solutions and merge their results into benchmarks.json.
    With changed, only the outdated results are run again.
    """
    results = load_results()
    inputs = load_inputs()
    answers = load_answers()
    if not answers:
        print(
            "No answer recorded by Puzzle Submitter: "
            "only the inputs JSON files are used."
        )
    lock = threading.Lock()

    tasks = []
    for kind, number in targets or known_events(inputs):
        for quest in quests or range(1, quests_in(kind) + 1):
            if quest > quests_in(kind):
                continue
            entries = results.setdefault(kind, {}).setdefault(str(number), {})
            if not has_solution(kind, number, quest):
                entries.pop(str(quest), None)
                continue
            path = solution_path(kind, number, quest)
            code = fingerprint(path)
            expected = expected_answers(answers, kind, number, quest)
            if changed and not outdated(
                entries.get(str(quest)), code, expected
            ):
                continue
            tasks.append((kind, number, quest, path, code, expected))
    if not tasks:
        print("Every result is up to date.")
        save_results(results)
        return

    print(
        f"Benchmarking {len(tasks)} solution(s), "
        f"timeout {timeout:g}s, {jobs} job(s)",
        flush=True,
    )

    def task(item):
        kind, number, quest, path, code, expected = item
        data = puzzle_input(inputs, number, quest)
        if data is None:
            run_result = {
                "answers": [],
                "time": None,
                "timeout": False,
                "error": "no input",
            }
        else:
            run_result = run(path, data, timeout)
        with lock:
            result = grade(run_result, expected) | {"code": code}
            title = quest_title(kind, number, quest)
            if title:
                result = {"title": title} | result
            results[kind][str(number)][str(quest)] = result
            save_results(results)
            name = f"{number}" if kind == "events" else f"story {number}"
            print(
                f"  {name:>7} quest {quest:>2} {describe(result)}", flush=True
            )

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(task, tasks))

    results["meta"] = {
        "timeout": timeout,
        "machine": machine(),
        "date": datetime.date.today().isoformat(),
        "python": platform.python_version(),
    }
    save_results(results)


def parse_target(text: str) -> tuple[str, int]:
    """'2024' is an event, 'story3' (or 's3') a story."""
    match = re.fullmatch(r"(?:story|s)_?(\d+)", text.lower())
    if match:
        return ("stories", int(match[1]))
    if text.isdigit() and int(text) >= 2000:
        return ("events", int(text))
    raise argparse.ArgumentTypeError(f"{text!r} is neither a year nor storyN")


def parse_quests(text: str) -> list[int]:
    """Parse '1-5', '1,3,5' or '1-3,7' into a sorted list of quests."""
    quests = set()
    for chunk in text.split(","):
        start, _, end = chunk.strip().partition("-")
        quests.update(range(int(start), int(end or start) + 1))
    return sorted(quests)


def main():
    """Entry point."""
    if len(sys.argv) == 3 and sys.argv[1] == "--child":
        child(sys.argv[2])

    parser = argparse.ArgumentParser(
        description="Benchmark Everybody Codes solutions"
    )
    parser.add_argument(
        "targets",
        type=parse_target,
        nargs="*",
        help="events (2024) and stories (story3) to run (default: all)",
    )
    parser.add_argument(
        "--quests",
        type=parse_quests,
        help='quests to run, e.g. "1-5" or "1,3"',
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=300,
        help="timeout per quest in seconds (default: 300)",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="solutions run in parallel (default: 1, the most accurate)",
    )
    parser.add_argument(
        "--changed",
        action="store_true",
        help="only run solutions whose code changed since their last run, "
        "new ones, and ones that can now be verified",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="only regenerate the scoreboards from the stored results",
    )
    args = parser.parse_args()

    if not args.render:
        benchmark(
            args.targets, args.quests, args.timeout, args.jobs, args.changed
        )

    sys.path.insert(0, str(PACKAGE.parent))
    from everybodycodes.scoreboard import render  # noqa: PLC0415

    render()


if __name__ == "__main__":
    main()
