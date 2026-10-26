#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  DATA_DIR=/path/to/parquet BASE_MODEL=/path/or/hf-id bash deepaction/train_dupo.sh

Required environment variables:
  DATA_DIR                 Directory containing train.parquet and test.parquet
  BASE_MODEL               Hugging Face model id or local model directory

Common optional variables (implementation defaults):
  MODEL_FAMILY=qwen        qwen or llama; controls reward-output parsing
  N_GPUS=16
  ROLLOUT_N=4
  TRAIN_BATCH_SIZE=512
  VAL_BATCH_SIZE=128
  PPO_MINI_BATCH_SIZE=128
  TOOL_WEIGHT=0.7
  PLAN_WEIGHT=0.1
  SFT_DECAY=0.01
  DECAY_RATE=0.5
  DRY_RUN=0               Set to 1 to print the command without running it

See docs/TRAINING.md for every setting and the paper/code alignment warning.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ -z "${DATA_DIR:-}" ]]; then
  echo "ERROR: DATA_DIR is required." >&2
  usage >&2
  exit 2
fi

if [[ -z "${BASE_MODEL:-}" ]]; then
  echo "ERROR: BASE_MODEL is required." >&2
  usage >&2
  exit 2
fi

if [[ ! -f "$DATA_DIR/train.parquet" || ! -f "$DATA_DIR/test.parquet" ]]; then
  echo "ERROR: DATA_DIR must contain train.parquet and test.parquet: $DATA_DIR" >&2
  exit 2
fi

MODEL_FAMILY="${MODEL_FAMILY:-qwen}"
if [[ "$MODEL_FAMILY" != "qwen" && "$MODEL_FAMILY" != "llama" ]]; then
  echo "ERROR: MODEL_FAMILY must be 'qwen' or 'llama'." >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PYTHON_BIN="${PYTHON_BIN:-python3}"
N_GPUS="${N_GPUS:-16}"
ROLLOUT_TP_SIZE="${ROLLOUT_TP_SIZE:-1}"
ROLLOUT_N="${ROLLOUT_N:-4}"
TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-512}"
VAL_BATCH_SIZE="${VAL_BATCH_SIZE:-128}"
PPO_MINI_BATCH_SIZE="${PPO_MINI_BATCH_SIZE:-128}"
MAX_PROMPT_LENGTH="${MAX_PROMPT_LENGTH:-2048}"
MAX_RESPONSE_LENGTH="${MAX_RESPONSE_LENGTH:-1024}"
LEARNING_RATE="${LEARNING_RATE:-1e-6}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.6}"
TOTAL_EPOCHS="${TOTAL_EPOCHS:-20}"
SAVE_FREQ="${SAVE_FREQ:-200}"
TEST_FREQ="${TEST_FREQ:-5}"

TOOL_WEIGHT="${TOOL_WEIGHT:-0.7}"
PLAN_WEIGHT="${PLAN_WEIGHT:-0.1}"
SFT_DECAY="${SFT_DECAY:-0.01}"
DECAY_RATE="${DECAY_RATE:-0.5}"
AVG_RELEVANCE="${AVG_RELEVANCE:-0.496}"
EXPERIMENT_NAME="${EXPERIMENT_NAME:-dupo-${MODEL_FAMILY}}"
OUTPUT_DIR="${OUTPUT_DIR:-$REPO_ROOT/checkpoints/DeepAction/$EXPERIMENT_NAME}"

# Feature switches exposed for reproducible configuration.
export WITHLENGTH="${WITHLENGTH:-0}"
export REFINEDREWARD="${REFINEDREWARD:-0}"
export COARSEREWARD="${COARSEREWARD:-0}"
export STRICTMATCH="${STRICTMATCH:-0}"
export CORRECTMAX1="${CORRECTMAX1:-0}"
export MAX1STEP30MAX3="${MAX1STEP30MAX3:-0}"
export SCHEDULEREWARD="${SCHEDULEREWARD:-1}"
export SCHEDULELENGTH="${SCHEDULELENGTH:-0}"
export ENABLENEGATIVE="${ENABLENEGATIVE:-1}"
export NEGATIVEMODE="${NEGATIVEMODE:-0}"
export TIMEWEIGHTMODE="${TIMEWEIGHTMODE:-1}"
export TOOLWEIGHT="$TOOL_WEIGHT"
export GLOBALWEIGHT="$PLAN_WEIGHT"
export AVGRELEVANCE="$AVG_RELEVANCE"
export DECAYRATE="$DECAY_RATE"
export EXPERIMENT_NAME
export HYDRA_FULL_ERROR="${HYDRA_FULL_ERROR:-1}"
export VLLM_ATTENTION_BACKEND="${VLLM_ATTENTION_BACKEND:-XFORMERS}"
export PYTHONPATH="$REPO_ROOT/verl${PYTHONPATH:+:$PYTHONPATH}"

command=(
  "$PYTHON_BIN" -m verl.trainer.main_ppo
  "algorithm.adv_estimator=grpo"
  "data.train_files=$DATA_DIR/train.parquet"
  "data.val_files=$DATA_DIR/test.parquet"
  "data.train_batch_size=$TRAIN_BATCH_SIZE"
  "data.val_batch_size=$VAL_BATCH_SIZE"
  "data.max_prompt_length=$MAX_PROMPT_LENGTH"
  "data.max_response_length=$MAX_RESPONSE_LENGTH"
  "actor_rollout_ref.model.path=$BASE_MODEL"
  "actor_rollout_ref.actor.optim.lr=$LEARNING_RATE"
  "actor_rollout_ref.model.use_remove_padding=True"
  "actor_rollout_ref.actor.ppo_mini_batch_size=$PPO_MINI_BATCH_SIZE"
  "actor_rollout_ref.actor.use_dynamic_bsz=True"
  "actor_rollout_ref.actor.use_sft_loss=True"
  "actor_rollout_ref.actor.sft_decay=$SFT_DECAY"
  "actor_rollout_ref.actor.use_kl_loss=False"
  "actor_rollout_ref.actor.kl_loss_coef=0.001"
  "actor_rollout_ref.actor.kl_loss_type=low_var_kl"
  "actor_rollout_ref.model.enable_gradient_checkpointing=True"
  "actor_rollout_ref.actor.fsdp_config.param_offload=False"
  "actor_rollout_ref.actor.fsdp_config.grad_offload=False"
  "actor_rollout_ref.actor.fsdp_config.optimizer_offload=False"
  "actor_rollout_ref.rollout.tensor_model_parallel_size=$ROLLOUT_TP_SIZE"
  "actor_rollout_ref.rollout.name=vllm"
  "actor_rollout_ref.rollout.gpu_memory_utilization=$GPU_MEMORY_UTILIZATION"
  "actor_rollout_ref.rollout.n=$ROLLOUT_N"
  "actor_rollout_ref.ref.fsdp_config.param_offload=True"
  "algorithm.kl_ctrl.kl_coef=0.001"
  "trainer.critic_warmup=0"
  "trainer.logger=['console']"
  "trainer.project_name=DeepAction"
  "trainer.experiment_name=$EXPERIMENT_NAME"
  "trainer.n_gpus_per_node=$N_GPUS"
  "trainer.nnodes=1"
  "trainer.default_local_dir=$OUTPUT_DIR"
  "trainer.save_freq=$SAVE_FREQ"
  "trainer.test_freq=$TEST_FREQ"
  "trainer.total_epochs=$TOTAL_EPOCHS"
)

# Additional Hydra overrides are appended last and therefore take precedence.
if (( $# > 0 )); then
  command+=("$@")
fi

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  "$PYTHON_BIN" - "${command[@]}" <<'PY'
import shlex
import sys

print("Resolved command:")
print(shlex.join(sys.argv[1:]))
PY
  exit 0
fi

mkdir -p "$OUTPUT_DIR"
exec "${command[@]}"
