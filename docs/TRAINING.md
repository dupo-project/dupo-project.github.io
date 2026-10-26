# Training

## Entry point

Use `deepaction/train_dupo.sh`. `deepaction/train_grpo.sh` is a compatibility alias.

At minimum, provide the processed data directory and model identifier or local model path:

```bash
DATA_DIR=/datasets/planarena \
BASE_MODEL=Qwen/Qwen2.5-3B-Instruct \
bash deepaction/train_dupo.sh
```

The script validates required files before launching and never downloads data implicitly.

Additional positional arguments are appended as Hydra overrides, so advanced users can change settings not exposed as environment variables:

```bash
DATA_DIR=/datasets/planarena \
BASE_MODEL=Qwen/Qwen2.5-3B-Instruct \
bash deepaction/train_dupo.sh \
  trainer.val_before_train=False \
  actor_rollout_ref.rollout.temperature=1.0
```

## Inspect before running

```bash
DATA_DIR=/datasets/planarena \
BASE_MODEL=Qwen/Qwen2.5-3B-Instruct \
DRY_RUN=1 \
bash deepaction/train_dupo.sh
```

`DRY_RUN=1` prints shell-escaped arguments after resolving defaults.

## Main settings

The defaults below are the implementation defaults. They are not the paper appendix configuration.

| Variable | Default | Description |
| --- | ---: | --- |
| `MODEL_FAMILY` | `qwen` | Reward-output parser; supported values are `qwen` and `llama`. |
| `N_GPUS` | `16` | GPUs on one node. |
| `ROLLOUT_TP_SIZE` | `1` | vLLM tensor parallel size. |
| `ROLLOUT_N` | `4` | Rollouts per prompt. |
| `TRAIN_BATCH_SIZE` | `512` | Global training batch size. |
| `VAL_BATCH_SIZE` | `128` | Validation batch size. |
| `PPO_MINI_BATCH_SIZE` | `128` | Actor PPO mini-batch size. |
| `MAX_PROMPT_LENGTH` | `2048` | Maximum prompt tokens. |
| `MAX_RESPONSE_LENGTH` | `1024` | Maximum response tokens. |
| `LEARNING_RATE` | `1e-6` | Actor learning rate. |
| `TOOL_WEIGHT` | `0.7` | TOOL-side reward coefficient exposed as `TOOLWEIGHT`. |
| `PLAN_WEIGHT` | `0.1` | PLAN-side reward coefficient exposed as `GLOBALWEIGHT`. |
| `SFT_DECAY` | `0.01` | SFT anchor decay setting in the current implementation. |
| `DECAY_RATE` | `0.5` | Negative-tool reward decay setting. |
| `AVG_RELEVANCE` | `0.496` | Dataset normalization constant. |
| `TOTAL_EPOCHS` | `20` | Training epochs. |
| `OUTPUT_DIR` | `checkpoints/DeepAction/<experiment>` | Checkpoint directory. |

Run `bash deepaction/train_dupo.sh --help` for the complete list.

## Outputs

By default, checkpoints are written under:

```text
checkpoints/DeepAction/<EXPERIMENT_NAME>/
```

Set `OUTPUT_DIR` to an absolute path for managed storage. The directory is ignored by Git.

For every reported run, preserve:

- repository commit and dirty-worktree status;
- resolved command from a dry run;
- model identifier and immutable revision;
- PlanArena version and file hashes;
- CUDA, PyTorch, vLLM, Ray, and driver versions;
- GPU type/count, seed, and wall-clock duration;
- checkpoints, logs, and evaluation artifacts.

## Paper configuration

The submitted paper reports 8 A100 80 GB GPUs, global batch size 256, 16 rollouts, equal PLAN/TOOL weights, semantic reward weight 0.8, and anchor decay 0.5. Those values differ from the released training entry point, and the code path does not expose every paper mechanism one-to-one. Do not label a run “paper reproduction” by changing environment variables alone. Resolve the implementation checklist in [REPRODUCIBILITY.md](REPRODUCIBILITY.md) first.

## Multi-node training

The current entry point supports a one-node reference configuration. Multi-node launch changes Ray initialization, rendezvous, and storage behavior and has not been verified for this release. Treat multi-node support as future work rather than silently setting `trainer.nnodes`.
