# SPDX-License-Identifier: CC-BY-NC-4.0
"""Print the first normalized trajectory row matching a step filter."""

import argparse
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--min-total-steps", type=int, default=5)
    parser.add_argument("--current-step", type=int, default=3)
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as stream:
        data = json.load(stream)

    for item in data:
        if item["totalToolCount"] > args.min_total_steps and item["currentToolCount"] == args.current_step:
            print(json.dumps(item, ensure_ascii=False))
            return
    raise SystemExit("no matching record")


if __name__ == "__main__":
    main()
