# SPDX-License-Identifier: CC-BY-NC-4.0
"""Convert normalized DeepAction JSON data to verl-compatible Parquet files."""

import argparse
import json
import os

import pandas as pd


def process_fn(example, idx, split):
    instruction = example["instruction"]
    input_text = example["input"]
    output = example["output"]
    negative = example.get("negative", json.dumps([]))

    return {
        "data_source": "rlla",
        "prompt": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": input_text},
        ],
        "ability": "math",
        "reward_model": {"style": "rule", "ground_truth": output},
        "extra_info": {
            "split": split,
            "index": idx,
            "instruction": instruction,
            "input": input_text,
            "output": output,
            "trajectoryID": example["trajectoryID"],
            "currentToolCount": example["currentToolCount"],
            "totalToolCount": example["totalToolCount"],
            "finalAnswer": example["finalAnswer"],
            "negative": negative,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", required=True, help="Normalized JSON array")
    parser.add_argument("--local-dir", required=True, help="Output directory")
    parser.add_argument("--validation-ratio", type=float, default=0.02)
    args = parser.parse_args()

    if not 0 < args.validation_ratio < 1:
        raise ValueError("--validation-ratio must be between 0 and 1")

    with open(args.input_file, "r", encoding="utf-8") as stream:
        dataset = json.load(stream)
    if len(dataset) < 2:
        raise ValueError("at least two records are required")

    test_num = max(1, int(len(dataset) * args.validation_ratio))
    test_num = min(test_num, len(dataset) - 1)
    train_dataset = dataset[:-test_num]
    test_dataset = dataset[-test_num:]

    train_dataset = [process_fn(row, idx, "train") for idx, row in enumerate(train_dataset)]
    test_dataset = [process_fn(row, idx, "test") for idx, row in enumerate(test_dataset)]

    os.makedirs(args.local_dir, exist_ok=True)
    pd.DataFrame(train_dataset).to_parquet(os.path.join(args.local_dir, "train.parquet"), index=False)
    pd.DataFrame(test_dataset).to_parquet(os.path.join(args.local_dir, "test.parquet"), index=False)
    print(f"Saved {len(train_dataset)} train and {len(test_dataset)} test records to {args.local_dir}")


if __name__ == "__main__":
    main()
