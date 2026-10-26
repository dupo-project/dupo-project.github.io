#!/usr/bin/env python3
"""Convert normalized PLAN-TOOL JSON records to verl-compatible Parquet files."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "instruction",
    "input",
    "output",
    "trajectoryID",
    "currentToolCount",
    "totalToolCount",
    "finalAnswer",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSON array of normalized PLAN-TOOL records")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for train.parquet and test.parquet")
    parser.add_argument("--validation-ratio", type=float, default=0.02, help="Fraction assigned to the test split")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle records before splitting")
    parser.add_argument("--seed", type=int, default=31415, help="Shuffle seed")
    return parser.parse_args()


def normalize_negative(value: Any) -> str:
    if value is None:
        return "[]"
    if isinstance(value, str):
        parsed = json.loads(value)
        if not isinstance(parsed, list):
            raise ValueError("negative must encode a JSON list")
        return json.dumps(parsed, ensure_ascii=False)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    raise ValueError("negative must be a list, JSON-list string, or null")


def validate_action(action: str, index: int) -> None:
    if "<plan>" not in action or "</plan>" not in action:
        raise ValueError(f"record {index}: output must contain one <plan> span")
    has_tool = "<tool_call>" in action and "</tool_call>" in action
    has_response = "<response>" in action and "</response>" in action
    if not has_tool and not has_response:
        raise ValueError(f"record {index}: output needs a <tool_call> or <response> span")
    if has_tool:
        payload = action.split("<tool_call>", 1)[1].split("</tool_call>", 1)[0].strip()
        for line_number, line in enumerate(payload.splitlines(), start=1):
            if not line.strip():
                continue
            tool = json.loads(line)
            if not isinstance(tool, dict) or "name" not in tool or "parameters" not in tool:
                raise ValueError(f"record {index}, tool line {line_number}: expected name and parameters")


def to_verl_record(example: dict[str, Any], index: int, split: str) -> dict[str, Any]:
    missing = sorted(REQUIRED_FIELDS - example.keys())
    if missing:
        raise ValueError(f"record {index}: missing fields: {', '.join(missing)}")

    current_step = int(example["currentToolCount"])
    total_steps = int(example["totalToolCount"])
    if current_step < 1 or total_steps < 1 or current_step > total_steps:
        raise ValueError(f"record {index}: require 1 <= currentToolCount <= totalToolCount")

    output = str(example["output"])
    validate_action(output, index)

    return {
        "data_source": "rlla",
        "prompt": [
            {"role": "system", "content": str(example["instruction"])},
            {"role": "user", "content": str(example["input"])},
        ],
        "ability": "math",
        "reward_model": {"style": "rule", "ground_truth": output},
        "extra_info": {
            "split": split,
            "index": index,
            "instruction": str(example["instruction"]),
            "input": str(example["input"]),
            "output": output,
            "trajectoryID": example["trajectoryID"],
            "currentToolCount": current_step,
            "totalToolCount": total_steps,
            "finalAnswer": example["finalAnswer"],
            "negative": normalize_negative(example.get("negative")),
        },
    }


def main() -> None:
    args = parse_args()
    if not 0 < args.validation_ratio < 1:
        raise SystemExit("--validation-ratio must be between 0 and 1")

    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("pandas and pyarrow are required; install the vendored verl package first") from exc

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or len(raw) < 2:
        raise SystemExit("input must be a JSON array with at least two records")

    records = list(raw)
    if args.shuffle:
        random.Random(args.seed).shuffle(records)

    test_count = max(1, int(len(records) * args.validation_ratio))
    test_count = min(test_count, len(records) - 1)
    train_raw = records[:-test_count]
    test_raw = records[-test_count:]

    train = [to_verl_record(item, index, "train") for index, item in enumerate(train_raw)]
    test = [to_verl_record(item, index, "test") for index, item in enumerate(test_raw)]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_path = args.output_dir / "train.parquet"
    test_path = args.output_dir / "test.parquet"
    pd.DataFrame(train).to_parquet(train_path, index=False)
    pd.DataFrame(test).to_parquet(test_path, index=False)

    print(f"wrote {len(train)} training rows to {train_path}")
    print(f"wrote {len(test)} validation rows to {test_path}")


if __name__ == "__main__":
    main()
