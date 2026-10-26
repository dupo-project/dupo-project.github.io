# Data format

## Expected files

`deepaction/train_dupo.sh` expects a directory containing:

```text
DATA_DIR/
  train.parquet
  test.parquet
```

Each Parquet row follows the verl RL dataset contract below.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `data_source` | string | yes | Must be `rlla` for the bundled DUPO reward path. |
| `prompt` | list of messages | yes | System and user messages supplied to the policy. |
| `ability` | string | yes | Retained compatibility field; the bundled pipeline uses `math`. |
| `reward_model` | object | yes | Contains `style` and the reference `ground_truth` action. |
| `extra_info` | object | yes | Step, trajectory, and negative-tool metadata used by the reward. |

`extra_info` must contain:

| Field | Type | Meaning |
| --- | --- | --- |
| `trajectoryID` | string or integer | Stable identifier for the original trajectory. |
| `currentToolCount` | integer | One-based step index used by position weighting. |
| `totalToolCount` | integer | Total number of tool-use steps in the trajectory. |
| `finalAnswer` | boolean or string | Whether this row is the final agent action. |
| `negative` | JSON string | List of non-reference tools and relevance scores. Use `[]` when absent. |
| `split` | string | `train` or `test`. |
| `index` | integer | Row index inside the split. |

The reference action uses explicit tags:

```text
<plan> Retrieve the current weather for the requested city. </plan>
<tool_call>
{"name": "get_weather", "parameters": {"city": "Paris"}}
</tool_call>
```

A final textual response can be appended as:

```text
<response> It is currently 18 degrees Celsius in Paris. </response>
```

## Preparing Parquet files

The release utility accepts a JSON array whose records contain:

```json
{
  "instruction": "System prompt with tool definitions",
  "input": "User request and trajectory history",
  "output": "<plan>...</plan>\n<tool_call>...</tool_call>",
  "trajectoryID": "trajectory-001",
  "currentToolCount": 1,
  "totalToolCount": 2,
  "finalAnswer": false,
  "negative": []
}
```

Convert and validate:

```bash
python scripts/prepare_data.py \
  --input /path/to/records.json \
  --output-dir /path/to/processed \
  --validation-ratio 0.02
```

The split is deterministic and preserves input order: the last validation rows become `test.parquet`. Use `--shuffle --seed 31415` only when you intentionally want a seeded shuffle.

## PlanArena release requirements

The full PlanArena dataset is not included. A reproducible PlanArena release should provide:

1. A stable public download URL and immutable version identifier.
2. File hashes and row counts for every released split.
3. The data statement and annotation guidelines.
4. A license file consistent with the paper's CC BY-NC 4.0 statement.
5. A provenance note confirming that proprietary API responses and private user data are excluded.
6. A script that reproduces the exact paper train/test splits from the released artifact.

The records under `examples/` are synthetic pipeline fixtures only. They must not be counted as PlanArena or used for result claims.
