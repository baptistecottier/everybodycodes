# Solutions for [Everybody Codes](https://everybody.codes) challenges

<!-- scoreboard:start -->
## Scoreboard

| Event | Title | Quests | ★ |
| :-- | :-- | :-- | --: |
| [2026](src/everybodycodes/events/year_2026/README.md) | Lord of the Wings | `███  ` `     ` `     ` `     ` | 9/60 |
| [2025](src/everybodycodes/events/year_2025/README.md) | The Song of Ducks and Dragons | `█▓███` `██▓█▒` `▒███▒` `▒ ██░` | 51/60 |
| [2024](src/everybodycodes/events/year_2024/README.md) | The Kingdom of Algorithmia | `█████` `████ ` `█▒██▒` `▒█▒▒░` | 50/60 |
| [Story 4](src/everybodycodes/stories/story_04/README.md) | The Digital Atelier | `███` | 9/9 |
| [Story 3](src/everybodycodes/stories/story_03/README.md) | Melody Made of Code | `███` | 9/9 |
| [Story 2](src/everybodycodes/stories/story_02/README.md) | The Entertainment Hub | `▓██` | 9/9 |
| [Story 1](src/everybodycodes/stories/story_01/README.md) | Echoes of Enigmatus | `███` | 9/9 |
| **Total** | | `█` 39 `▓` 3 `▒` 9 `░` 2 ` ` 19 | **146/216** |

<sub>`█` solved in under 5 s &emsp; `▓` solved in under 5 min &emsp; `▒` two parts only &emsp; `░` one part only &emsp; ` ` not solved<br>Python 3.13.14 · Apple M3 · 29 October 2026</sub>
<!-- scoreboard:end -->

## GridOS

| # | Title | Quests | Detailed scores |
| --: | :-- | :-- | :-- |
| 1 | [GridOS Tournament](./src/everybodycodes/gridos/gridos_01/) | 5/5 | [GridOS](./src/everybodycodes/gridos/README.md) |

## Benchmark

```bash
uv run src/everybodycodes/benchmark.py                    # every event and story
uv run src/everybodycodes/benchmark.py 2024 story3        # some events and stories
uv run src/everybodycodes/benchmark.py 2025 --quests 1-5  # some quests
uv run src/everybodycodes/benchmark.py --changed          # only what changed since its last run
uv run src/everybodycodes/benchmark.py --render           # redraw from benchmarks.json
```

Each quest runs on the personal input in its own process with a 5 minute timeout; the
time covers preprocessing and solving the three parts. Answers are checked against the
ones Puzzle Submitter recorded as correct, completed by the inputs JSON files. Results
are stored in `src/everybodycodes/benchmarks.json`, from which `scoreboard.py` writes
the scoreboard above and one page per event and story.
