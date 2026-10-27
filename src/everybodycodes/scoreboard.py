#!/usr/bin/env python3

"""
Render the scoreboards from src/everybodycodes/benchmarks.json (written by
benchmark.py): the global one, between the scoreboard markers of README.md, and
one detailed page per event (events/year_YYYY/README.md) and per story
(stories/story_NN/README.md). A result measured on code that differs from the
last commit is marked †, so the published scoreboard never hides it.

    uv run src/everybodycodes/scoreboard.py
"""

import datetime
import json
import re
import subprocess
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
RESULTS = PACKAGE / "benchmarks.json"
README = ROOT / "README.md"
MARKERS = ("<!-- scoreboard:start -->", "<!-- scoreboard:end -->")

FAST = 5  # seconds
NBSP = " "  # keeps strips on one line, and an unsolved quest an empty box
SYMBOLS = {"fast": "█", "slow": "▓", "two": "▒", "one": "░", "unsolved": NBSP}
STATES = ("fast", "slow", "two", "one", "unsolved")
TITLES = {
    "events": {
        2024: "The Kingdom of Algorithmia",
        2025: "The Song of Ducks and Dragons",
        2026: "Lord of the Wings",
    },
    "stories": {
        1: "Echoes of Enigmatus",
        2: "The Entertainment Hub",
        3: "Melody Made of Code",
        4: "The Digital Atelier",
    },
}


# ===========================================================================
# Quest states
# ===========================================================================


def quests_in(kind: str) -> int:
    """Number of quests: 20 for an event, 3 for a story."""
    return 20 if kind == "events" else 3


def folder(kind: str, number: int) -> str:
    """Folder of an event or a story, relative to the package."""
    if kind == "events":
        return f"events/year_{number}"
    return f"stories/story_{number:02}"


def name(kind: str, number: int) -> str:
    """Short name of an event (2025) or a story (Story 3)."""
    return str(number) if kind == "events" else f"Story {number}"


def title(kind: str, number: int) -> str:
    """Title of an event or a story."""
    return TITLES[kind].get(number, "")


def stars(quests: dict, kind: str) -> dict[int, list[str]]:
    """
    Per quest, the state of each part: 'ok', 'unknown' (answer not known
    locally) or 'no'.
    """
    result = {}
    for quest in range(1, quests_in(kind) + 1):
        parts = quests.get(str(quest), {}).get("parts", [])
        result[quest] = [p if p in ("ok", "unknown") else "no" for p in parts]
        result[quest] += ["no"] * (3 - len(result[quest]))
    return result


def state(result: dict | None, quest_stars: list[str]) -> str:
    """One of 'fast', 'slow', 'two', 'one' (parts solved) or 'unsolved'."""
    if result is None:
        return "unsolved"
    if result["status"] == "solved":
        return "fast" if result["time"] < FAST else "slow"
    return {0: "unsolved", 1: "one"}.get(quest_stars.count("ok"), "two")


def format_time(seconds: float) -> str:
    """Human-readable duration: < 1 ms, 12 ms, 3.2 s, 1 min 05 s."""
    if seconds < 0.001:
        return "< 1 ms"
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    if seconds < 60:
        return f"{seconds:.1f} s"
    minutes, seconds = divmod(round(seconds), 60)
    return f"{minutes} min {seconds:02} s" if seconds else f"{minutes} min"


def summary(kind: str, quests: dict) -> dict:
    """Stars, state of every quest and total solving time of an event."""
    event_stars = stars(quests, kind)
    states = [
        state(quests.get(str(quest)), event_stars[quest])
        for quest in range(1, quests_in(kind) + 1)
    ]
    solved = [
        quests[str(quest)]["time"]
        for quest, s in enumerate(states, 1)
        if s in ("fast", "slow")
    ]
    return {
        "stars": sum(p == "ok" for ps in event_stars.values() for p in ps),
        "max": 3 * quests_in(kind),
        "states": states,
        "time": sum(solved),
        "quest_stars": event_stars,
    }


def events(results: dict) -> list[tuple[str, int]]:
    """Every benchmarked event, then every story, the latest first."""
    return [
        (kind, int(number))
        for kind in ("events", "stories")
        for number in sorted(results.get(kind, {}), key=int, reverse=True)
    ]


# ===========================================================================
# Uncommitted code
# ===========================================================================


def committed_blobs() -> dict[str, str] | None:
    """Git object id of every file of the last commit, by path."""
    try:
        listing = subprocess.run(
            ["git", "ls-tree", "-r", "-z", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    entries = (entry.split("\t", 1) for entry in listing.split("\0") if entry)
    return {path: meta.split()[2] for meta, path in entries}


def uncommitted(results: dict) -> set[tuple[str, str, str]]:
    """(kind, number, quest) of the results measured on uncommitted code."""
    blobs = committed_blobs()
    if blobs is None:
        return set()
    flagged = set()
    for kind, number in events(results):
        for quest, entry in results[kind][str(number)].items():
            path = (
                PACKAGE
                / folder(kind, number)
                / "solutions"
                / f"quest_{int(quest):02}.py"
            )
            if entry.get("code") != blobs.get(
                path.relative_to(ROOT).as_posix()
            ):
                flagged.add((kind, str(number), quest))
    return flagged


# ===========================================================================
# Pages
# ===========================================================================


def symbol(quest_state: str) -> str:
    """Symbol of a quest state, always in the code font, so that it looks the
    same as in the strips: block characters differ a lot between fonts."""
    return f"`{SYMBOLS[quest_state]}`"


def strip(states: list[str]) -> str:
    """One symbol per quest, as one code span per block of five quests."""
    symbols = "".join(SYMBOLS[s] for s in states)
    return NBSP.join(
        f"`{symbols[i : i + 5]}`" for i in range(0, len(symbols), 5)
    )


def labels(timeout: float) -> dict[str, str]:
    """Meaning of each quest state."""
    return {
        "fast": f"solved in under {FAST} s",
        "slow": f"solved in under {format_time(timeout)}",
        "two": "two parts only",
        "one": "one part only",
        "unsolved": "not solved",
    }


def legend(timeout: float) -> str:
    """Meaning of the quest symbols, on one line."""
    return " &emsp; ".join(
        f"{symbol(s)} {label}" for s, label in labels(timeout).items()
    )


def environment(meta: dict) -> str:
    """Where and when the benchmark ran."""
    parts = []
    if meta.get("python"):
        parts.append(f"Python {meta['python']}")
    if meta.get("machine"):
        parts.append(meta["machine"])
    if meta.get("date"):
        date = datetime.date.fromisoformat(meta["date"])
        parts.append(date.strftime("%-d %B %Y"))
    return " · ".join(parts)


def homepage(results: dict, flagged: set) -> str:
    """Global scoreboard: one row per event and per story."""
    lines = [
        "| Event | Title | Quests | ★ |",
        "| :-- | :-- | :-- | --: |",
    ]
    total = {"stars": 0, "max": 0, "states": []}
    for kind, number in events(results):
        s = summary(kind, results[kind][str(number)])
        page = f"src/everybodycodes/{folder(kind, number)}/README.md"
        lines.append(
            f"| [{name(kind, number)}]({page}) | {title(kind, number)} "
            f"| {strip(s['states'])} | {s['stars']}/{s['max']} |"
        )
        for key in ("stars", "max", "states"):
            total[key] += s[key]
    counts = " ".join(
        f"{symbol(s)} {total['states'].count(s)}" for s in STATES
    )
    lines.append(
        f"| **Total** | | {counts} | **{total['stars']}/{total['max']}** |"
    )

    timeout = results["meta"].get("timeout", 300)
    notes = [legend(timeout)]
    if flagged:
        notes.append(
            f"{len(flagged)} result(s) measured on uncommitted code, "
            "marked † on the event pages"
        )
    notes.append(environment(results["meta"]))
    return "\n".join(
        [
            "## Scoreboard",
            "",
            *lines,
            "",
            f"<sub>{'<br>'.join(notes)}</sub>",
        ]
    )


def stars_cell(quest_stars: list[str]) -> str:
    """★ earned, ☆ not earned, ? answer unknown locally (cannot be checked)."""
    return "".join(
        {"ok": "★", "no": "☆", "unknown": "?"}[part] for part in quest_stars
    )


def time_cell(result: dict, timeout: float) -> str:
    """Solving time, or why there is none."""
    if result["status"] == "timeout":
        return f"> {format_time(timeout)}"
    if result["time"] is None:
        return "error"
    return format_time(result["time"])


def navigation(kind: str, number: int, numbers: list[int]) -> str:
    """Links to the previous event, the scoreboard and the next event."""
    links = []
    if number - 1 in numbers:
        previous = Path(folder(kind, number - 1)).name
        links.append(f"[← {name(kind, number - 1)}](../{previous}/README.md)")
    links.append("[Scoreboard](../../../../README.md#scoreboard)")
    if number + 1 in numbers:
        following = Path(folder(kind, number + 1)).name
        links.append(f"[{name(kind, number + 1)} →](../{following}/README.md)")
    return " · ".join(links)


def summary_table(s: dict, timeout: float) -> list[str]:
    """Stars, number of quests in each state and solving time."""
    lines = [f"| Stars | {s['stars']}/{s['max']} |", "| :-- | --: |"]
    lines += [
        f"| {symbol(key)} {label} | {s['states'].count(key)} |"
        for key, label in labels(timeout).items()
    ]
    time = format_time(s["time"]) if s["time"] else "–"
    return lines + [f"| Time of solved quests | {time} |"]


def quest_url(kind: str, number: int, quest: int) -> str:
    """Page of a quest on everybody.codes."""
    path = "event" if kind == "events" else "story"
    return f"https://everybody.codes/{path}/{number}/quests/{quest}"


def quest_table(
    kind: str, number: int, quests: dict, s: dict, timeout: float, flagged: set
) -> list[str]:
    """One row per quest: title, symbol, stars and time."""
    lines = [
        "| Quest | Puzzle | Solution | Time |",
        "| --: | :-- | :-- | --: |",
    ]
    for quest in range(1, quests_in(kind) + 1):
        entry = quests.get(str(quest))
        puzzle = (entry or {}).get("title") or f"Quest {quest}"
        cells = [str(quest), f"[{puzzle}]({quest_url(kind, number, quest)})"]
        quest_symbol = symbol(s["states"][quest - 1])
        quest_stars = stars_cell(s["quest_stars"][quest])
        if entry is None:  # no solution: nothing to link or time
            cells += [f"{quest_symbol} {quest_stars}", ""]
        else:
            flag = (kind, str(number), str(quest)) in flagged
            cells += [
                f"{quest_symbol} [{quest_stars}]"
                f"(solutions/quest_{quest:02}.py)",
                time_cell(entry, timeout) + (" †" if flag else ""),
            ]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def event_page(results: dict, kind: str, number: int, flagged: set) -> str:
    """Detailed page of an event: summary, then one row per quest."""
    quests = results[kind][str(number)]
    s = summary(kind, quests)
    timeout = results["meta"].get("timeout", 300)
    numbers = [int(n) for n in results[kind]]

    notes = [legend(timeout)]
    if any("unknown" in parts for parts in s["quest_stars"].values()):
        notes.append("? no answer known locally, so it cannot be verified")
    if any(key[:2] == (kind, str(number)) for key in flagged):
        notes.append("† measured on code that differs from the last commit")
    notes.append(environment(results["meta"]))

    heading = f"{name(kind, number)}: {title(kind, number)}".rstrip(": ")
    return "\n".join(
        [
            f"# Everybody Codes {heading}",
            "",
            navigation(kind, number, numbers),
            "",
            *summary_table(s, timeout),
            "",
            *quest_table(kind, number, quests, s, timeout, flagged),
            "",
            f"<sub>{'<br>'.join(notes)}</sub>",
            "",
        ]
    )


# ===========================================================================
# Output
# ===========================================================================


def render() -> None:
    """Write the global scoreboard and every event page."""
    with open(RESULTS, encoding="utf-8") as f:
        results = json.load(f)
    flagged = uncommitted(results)

    text = README.read_text(encoding="utf-8")
    start, end = MARKERS
    block = f"{start}\n{homepage(results, flagged)}\n{end}"
    pattern = re.compile(re.escape(start) + ".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"README.md has no {start} … {end} block to fill")
    README.write_text(pattern.sub(lambda _: block, text), encoding="utf-8")

    pages = events(results)
    for kind, number in pages:
        page = PACKAGE / folder(kind, number) / "README.md"
        page.write_text(
            event_page(results, kind, number, flagged), encoding="utf-8"
        )
    print(f"Scoreboards written: README.md and {len(pages)} event page(s)")


if __name__ == "__main__":
    render()
