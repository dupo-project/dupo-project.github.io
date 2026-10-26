# DUPO: Dual-Mode Unified Policy Optimization for Tool-Using Agents

[中文说明](README_zh.md) | [Installation](docs/INSTALLATION.md) | [Data](docs/DATA.md) | [Training](docs/TRAINING.md) | [Evaluation](docs/EVALUATION.md) | [Reproducibility](docs/REPRODUCIBILITY.md)

DUPO is a training recipe for tool-using language-model agents. It represents each action as a natural-language `<plan>` span followed by an executable `<tool_call>` span, then optimizes tool-use trajectories with step-aware rewards and a continuation schedule built on [verl](https://github.com/volcengine/verl).

<p align="center">
  <img src="assets/dupo-framework.png" alt="DUPO framework: dual-mode decomposition, chain-aware decoupled rewards, and stable optimization" width="100%">
</p>

<p align="center"><em>Figure 4. Illustration of the proposed Dual-Mode Unified Policy Optimization (DUPO) framework.</em></p>

DUPO separates every trajectory step into PLAN and TOOL modes, assigns mode-specific credit through chain-aware decoupled rewards, and stabilizes the transition from supervised learning to reinforcement learning with SFT anchoring and adaptive clipping.

## What is included

- A configurable training entry point in `deepaction/train_dupo.sh`.
- A vendored verl-based training core with the DUPO reward, continuation, and clipping changes.
- Data preparation and schema validation for PLAN-TOOL trajectories.
- CPU-only repository and reward smoke checks.
- Evaluation guidance for BFCL v3, API-Bank, and Tau2.

The full PlanArena dataset and pretrained checkpoints are not bundled. The synthetic records under `examples/` are provided only to validate the data and reward pipeline; see [Data](docs/DATA.md) for the supported schema.

## Quick start

### 1. Create the environment

The reference stack uses Linux, Python 3.10, CUDA 12.1+, PyTorch 2.6, and vLLM 0.8.2/0.8.3. A CUDA-capable machine is required for training; the paper experiments used NVIDIA A100 80 GB GPUs.

```bash
conda create -n dupo python=3.10 -y
conda activate dupo
python -m pip install -e './verl[vllm]'
python -m pip install flash-attn --no-build-isolation
```

For environment details and a container option, see [docs/INSTALLATION.md](docs/INSTALLATION.md).

### 2. Run the CPU-only smoke checks

```bash
python scripts/check_release.py
PYTHONPATH="$PWD/verl" python scripts/smoke_reward.py
```

These checks verify repository hygiene and the DUPO reward path. They do not train a model.

### 3. Prepare a dataset

```bash
python scripts/prepare_data.py \
  --input examples/mini_planarena.json \
  --output-dir data/mini
```

This creates `data/mini/train.parquet` and `data/mini/test.parquet`. The bundled records are only for pipeline validation, not for meaningful training or benchmarking. See [docs/DATA.md](docs/DATA.md) for the full schema.

### 4. Inspect the training command

```bash
DATA_DIR="$PWD/data/mini" \
BASE_MODEL="Qwen/Qwen2.5-3B-Instruct" \
DRY_RUN=1 \
bash deepaction/train_dupo.sh
```

Remove `DRY_RUN=1` on a configured GPU machine to start training. All important settings can be overridden with environment variables; see [docs/TRAINING.md](docs/TRAINING.md).

## Repository layout

```text
deepaction/              Configurable DUPO training entry points
docs/                    Installation, data, training, evaluation, and reproducibility docs
examples/                Tiny schema-valid sample data
scripts/                 Preparation, validation, and smoke-check utilities
verl/                    Vendored verl 0.3.1.dev training core with DUPO changes
```

## Reproducibility

The released implementation preserves its documented training behavior and defaults. Paper configurations, implementation mappings, and known reproduction limitations are documented in [Algorithm](docs/ALGORITHM.md) and [Reproducibility](docs/REPRODUCIBILITY.md).

## Citation

If you use DUPO in your work, please cite the paper and software using the metadata in [CITATION.cff](CITATION.cff).

## License

DUPO-specific materials are available under CC BY-NC 4.0, which permits sharing and adaptation for noncommercial use with attribution. The vendored `verl/` subtree remains under Apache-2.0. See [LICENSE](LICENSE), [verl/LICENSE](verl/LICENSE), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) for development checks and [SECURITY.md](SECURITY.md) for private vulnerability reporting guidance.
