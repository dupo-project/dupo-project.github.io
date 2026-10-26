# Algorithm-to-code map

This document maps the released implementation to the concepts used in the DUPO paper. It describes the code that is present and does not fill missing mechanisms by interpretation.

| Concept | Current implementation location | Notes |
| --- | --- | --- |
| PLAN/TOOL format | `verl/verl/utils/reward_score/rlla.py` | Parses `<plan>`, `<tool_call>`, and optional `<response>` spans. |
| TOOL validity/correctness reward | `verl/verl/utils/reward_score/rlla.py` | Checks tags, JSON tool calls, names, arguments, and negative-tool penalties. |
| PLAN reward | `verl/verl/utils/reward_score/rlla.py` | Uses exact equality or overlap via `match_score`; it is not an embedding cosine in the released implementation. |
| Step-position weighting | `timed_reward_function_dynamic_k` in `rlla.py` | Exponential, linear, or discrete modes controlled by environment variables. See the source-behavior warning below. |
| GRPO advantage | `verl/verl/trainer/ppo/core_algos.py` | Uses the vendored verl GRPO implementation. |
| Adaptive clipping | `core_algos.compute_policy_loss` and `workers/actor/dp_actor.py` | Derives a dynamic upper clip parameter from observed ratio maxima and remaining steps. |
| SFT anchor | `workers/actor/dp_actor.py` | Mixes the policy loss with an exponentially decayed log-probability term. |
| Training-step propagation | `trainer/ppo/ray_trainer.py`, `trainer/ppo/reward.py`, and `workers/reward_manager/naive.py` | Passes the current step into reward and actor updates. |
| Entry point | `deepaction/train_dupo.sh` | Configurable wrapper around `python -m verl.trainer.main_ppo`. |

## Important implementation boundary

The paper's mode-separated objective defines different importance ratios over PLAN and TOOL token masks. In the released implementation, `DataParallelPPOActor.update_policy` passes one response mask to `compute_policy_loss`; PLAN/TOOL separation is expressed in reward components, not as two independently masked policy-ratio losses.

The paper's PLAN semantic reward uses a pretrained sentence encoder. In the released implementation, `base_content_reward_func` compares PLAN strings directly and uses overlap when they are not equal.

The released entry point sets `TIMEWEIGHTMODE=1`, but `compute_score` implements the mode switch as `if mode == 1`, followed by a second `if mode == 2 ... else`. The `else` therefore overwrites the mode-1 score with the unweighted score. The current release records that behavior and does not repair it because doing so changes the training objective.

These are material differences for a paper-facing release. They are recorded rather than silently “fixed” because the project requirement is to avoid algorithmic changes during open-source cleanup.
