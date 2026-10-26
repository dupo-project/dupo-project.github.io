# Reproducibility

This repository provides the DUPO training implementation and vendors verl `0.3.1.dev`. Documentation, examples, and release tooling are included to make the code easier to inspect and run; they do not change the training objective.

The table below records differences between the paper configuration and the defaults or behavior currently exposed by the released implementation. These differences matter when interpreting experimental results.

## Paper and implementation alignment

| Item | Paper configuration | Released implementation | Status |
| --- | --- | --- | --- |
| Training GPUs | 8×A100 80 GB | entry default `N_GPUS=16` | mismatch |
| Group rollouts | `G=16` | `rollout.n=4` | mismatch |
| Global batch | 256 | 512 | mismatch |
| PLAN/TOOL weights | `0.5 / 0.5` | `GLOBALWEIGHT=0.1`, `TOOLWEIGHT=0.7` | mismatch |
| Semantic reward | Qwen3-Embedding-0.6B cosine, `lambda_sem=0.8` | direct string equality/overlap; no encoder load in reward path | implementation mismatch |
| Mode-separated policy ratios | separate PLAN and TOOL masks/ratios | one response mask and one policy-loss call | implementation mismatch |
| Upstream anchor | exponential `eta(n)` over normalized step advantage | reward-level step weight derived from `currentToolCount/totalToolCount`; the selected default mode is overwritten by the current `if/if/else` control flow | implementation mismatch |
| SFT anchor decay | `zeta=0.5` | `sft_decay=0.01`; loss weight is `exp(-decay*step)*decay` | mismatch |
| Adaptive clipping | paper Eq. 12 schedule | ratio-max-based dynamic upper clip in actor/core code | requires validation |
| Benchmarks | BFCL v3, API-Bank, Tau2 | evaluation guidance is provided; frozen adapters and outputs are not bundled | incomplete artifact set |
| PlanArena | 20,646 trajectories, 7,941 scenarios | full dataset is not bundled | missing artifact |

## Requirements for a paper-reproduction claim

Before describing a run as an exact reproduction of the reported paper results:

1. Identify and publish the implementation revision corresponding to the reported experiments.
2. Resolve or explicitly version every paper/implementation difference listed above.
3. Decide whether to preserve or revise the `TIMEWEIGHTMODE=1` control flow, and version any change as an algorithm change.
4. Publish a frozen PlanArena artifact with split manifests, hashes, provenance, and license information.
5. Publish immutable model revisions and checkpoint hashes for every reported backbone.
6. Pin the BFCL v3, API-Bank, and Tau2 revisions and publish the adapters used for evaluation.
7. Regenerate the main and ablation tables from immutable raw outputs.

Until these requirements are met, results produced from this repository should be described as runs of the released DUPO implementation, not verified reproductions of every value in the paper.

## What can be verified from this repository

- The DUPO/DeepAction reward path and training-core changes are present.
- The documented entry points do not require repository-specific storage paths or embedded credentials.
- The sample data can be converted into the expected Parquet schema.
- The reward function imports and executes in a CPU-only smoke test.
- Training commands can be fully resolved with `DRY_RUN=1` before GPU launch.

Full training, benchmark parity, and paper-table reproduction additionally require the corresponding datasets, model weights, benchmark revisions, and multi-GPU compute.
