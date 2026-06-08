#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any


def normalize(expected: Any) -> Any:
    if expected is None:
        return []
    if isinstance(expected, list):
        return expected
    if isinstance(expected, str):
        return expected.splitlines() if "\n" in expected else [expected]
    return expected


def normalize_input(data: Any) -> Any:
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, str):
        return data.splitlines()
    return data.splitlines()


def convert_case(case_obj: dict[str, Any], index: int) -> dict[str, Any]:
    case_number = case_obj.get("case", index + 1)
    converted: dict[str, Any] = {
        "case": str(case_obj.get("id", case_number)),
    }

    if "data" in case_obj:
        converted["input"] = normalize(case_obj["data"])
    elif "input" in case_obj:
        converted["input"] = normalize(case_obj["input"])

    if "expected" in case_obj:
        converted["expected"] = normalize(case_obj["expected"])

    for key in case_obj:
        if key in {"startPoints", "validate", "data", "input", "expected", "case", "id"}:
            continue
        converted[key] = case_obj[key]

    return converted


def convert_json(value: Any) -> Any:
    if isinstance(value, dict):
        if "cases" in value and isinstance(value["cases"], list):
            converted = {
                key: convert_json(val) if key != "cases" else [
                    convert_case(case, idx) if isinstance(case, dict) else case
                    for idx, case in enumerate(value["cases"])
                ]
                for key, val in value.items()
            }
            if set(converted.keys()) == {"cases"}:
                return converted["cases"]
            return converted
        return {key: convert_json(val) for key, val in value.items()}
    if isinstance(value, list):
        return [convert_json(item) for item in value]
    return value


def rewrite_file(path: Path, overwrite: bool) -> Path:
    content = json.loads(path.read_text(encoding="utf-8"))
    converted = convert_json(content)

    if overwrite:
        output_path = path
    else:
        output_path = path.with_suffix(path.suffix + ".converted")

    output_path.write_text(json.dumps(converted["cases"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def find_json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.json"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert old GridOS API test case JSON into normalized test_cases format."
    )
    parser.add_argument(
        "path",
        help="Input JSON file or directory containing GridOS API test case files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the original files in place.",
    )
    args = parser.parse_args()

    root_path = Path(args.path)
    if not root_path.exists():
        raise SystemExit(f"Path not found: {root_path}")

    files = find_json_files(root_path)
    if not files:
        raise SystemExit(f"No JSON files found in {root_path}")

    for json_path in files:
        try:
            output_path = rewrite_file(json_path, overwrite=args.overwrite)
            print(f"Converted: {json_path} -> {output_path}")
        except Exception as exc:
            print(f"Skipped {json_path}: {exc}")


if __name__ == "__main__":
    main()
