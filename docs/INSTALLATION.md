# Installation

## Supported environment

The bundled runtime vendors verl `0.3.1.dev`. Its reference environment is:

- Linux x86_64
- Python 3.10
- CUDA 12.1 or newer
- PyTorch 2.6.0
- vLLM 0.8.2 or 0.8.3
- `tensordict` 0.6.2
- NVIDIA Ampere-class or newer GPUs for the vLLM path

The submitted paper reports training on 8 NVIDIA A100 80 GB GPUs. Smaller hardware may work after reducing batch sizes, response length, rollout count, or enabling additional offload, but those settings are not paper-equivalent.

## Option A: container environment

The vendored verl documentation references the following compatible image:

```bash
docker pull hiyouga/verl:ngc-th2.6.0-cu126-vllm0.8.3-flashinfer0.2.2-cxx11abi0

docker run --rm -it \
  --gpus all \
  --network host \
  --shm-size 128g \
  -v "$PWD:/workspace/DUPO" \
  -w /workspace/DUPO \
  hiyouga/verl:ngc-th2.6.0-cu126-vllm0.8.3-flashinfer0.2.2-cxx11abi0 \
  bash
```

Inside the container, install this repository's vendored verl tree so that the DUPO modifications take precedence over any preinstalled package:

```bash
python -m pip install -e './verl[vllm]' --no-deps
```

Container tags are external artifacts. Pin the exact digest in a frozen reproduction record.

## Option B: Conda environment

```bash
conda create -n dupo python=3.10 -y
conda activate dupo

python -m pip install --upgrade pip wheel setuptools
python -m pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0
python -m pip install -e './verl[vllm]'
python -m pip install flash-attn --no-build-isolation
```

PyTorch wheels must match the CUDA runtime available on the host. Follow PyTorch's official selector if the generic command installs an incompatible build.

## Verify the installation

Repository-only checks:

```bash
python scripts/check_release.py
bash -n deepaction/train_dupo.sh deepaction/train_grpo.sh
```

Reward-path check:

```bash
PYTHONPATH="$PWD/verl" python scripts/smoke_reward.py
```

GPU and distributed-runtime check:

```bash
python - <<'PY'
import ray
import torch
import vllm

print("torch", torch.__version__)
print("cuda", torch.version.cuda)
print("gpu_count", torch.cuda.device_count())
print("ray", ray.__version__)
print("vllm", vllm.__version__)
assert torch.cuda.is_available()
PY
```

## Common problems

### `flash_attn` fails to build

Confirm that the compiler, CUDA toolkit, and PyTorch CUDA build are compatible. The container path is the most reproducible option.

### `tensordict` or vLLM import errors

The bundled configuration expects `tensordict==0.6.2` and vLLM 0.8.x. Reinstall those versions, then reinstall `./verl` in editable mode.

### Ray shared-memory warnings

Use a large `/dev/shm` allocation. For Docker, pass `--shm-size 128g`. The exact requirement depends on model size, batch size, and rollout count.

### Out of memory

Reduce one setting at a time and record it: `TRAIN_BATCH_SIZE`, `PPO_MINI_BATCH_SIZE`, `MAX_PROMPT_LENGTH`, `MAX_RESPONSE_LENGTH`, `ROLLOUT_N`, or `GPU_MEMORY_UTILIZATION`. Such a run is a portability experiment, not an exact paper reproduction.
