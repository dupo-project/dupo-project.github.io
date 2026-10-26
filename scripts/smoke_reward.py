#!/usr/bin/env python3
"""CPU-only smoke test for the DUPO reward path."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import math
import os
from pathlib import Path


def load_reward_module():
    reward_path = Path(__file__).resolve().parents[1] / "verl" / "verl" / "utils" / "reward_score" / "rlla.py"
    spec = importlib.util.spec_from_file_location("dupo_reward_smoke", reward_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load reward module from {reward_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    reward_module = load_reward_module()
    settings = {
        "EXPERIMENT_NAME": "dupo-smoke-qwen",
        "SCHEDULEREWARD": "0",
        "TOOLWEIGHT": "0.7",
        "GLOBALWEIGHT": "0.1",
        "TIMEWEIGHTMODE": "0",
        "ENABLENEGATIVE": "0",
        "WITHLENGTH": "0",
    }
    os.environ.update(settings)

    action = (
        '<plan> Retrieve the current weather for Paris. </plan>\n'
        '<tool_call>\n'
        '{"name": "get_weather", "parameters": {"city": "Paris"}}\n'
        '</tool_call>'
    )
    solution = f"<|im_start|>assistant\n{action}<|im_end|>"
    extra_info = {
        "currentToolCount": 1,
        "totalToolCount": 2,
        "negative": "[]",
    }

    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        result = reward_module.compute_score(solution, action, extra_info, step=0)

    expected_keys = {"score", "fomrat_score", "correct_score", "length_score"}
    if set(result) != expected_keys:
        raise AssertionError(f"unexpected reward keys: {sorted(result)}")
    if not all(math.isfinite(float(value)) for value in result.values()):
        raise AssertionError(f"non-finite reward result: {result}")
    if not math.isclose(reward_module.timed_reward_function_dynamic_k(1, 2), 1.0):
        raise AssertionError("unexpected first-step position weight")

    print("reward smoke test passed")
    print("result", result)


if __name__ == "__main__":
    main()
