# Evaluation

The paper reports BFCL v3, API-Bank, and Tau2. This repository does not vendor those projects or their generated outputs. Install each benchmark from its official source, pin the evaluated revision, and keep raw generations separate from scores.

## Common evaluation record

For each benchmark, record:

- DUPO repository commit and checkpoint hash;
- benchmark repository commit and dataset version;
- exact generation command and parser/adapter revision;
- model chat template, temperature, maximum tokens, and tensor-parallel size;
- raw generations, normalized predictions, per-case scores, and aggregate report;
- failed or excluded case IDs with reasons.

An aggregate CSV without the corresponding raw generations is not sufficient reproduction evidence.

## BFCL v3

Official project: https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard

Install the official evaluator in a separate environment or checkout:

```bash
git clone https://github.com/ShishirPatil/gorilla.git
cd gorilla/berkeley-function-call-leaderboard
python -m pip install -e '.[oss_eval_vllm]'
```

The current BFCL main branch also contains BFCL v4 and has changed model-handler interfaces. To reproduce the paper, pin a BFCL v3-compatible commit and preserve the released PLAN/TOOL parser behavior. Do not compare a v4 aggregate directly with the paper's v3 table.

The official workflow separates generation and evaluation:

```bash
bfcl generate --model MODEL_NAME --test-category all --backend vllm \
  --num-gpus 8 --local-model-path /path/to/checkpoint
bfcl evaluate --model MODEL_NAME --test-category all
```

Replace `MODEL_NAME` with a registered handler or add a versioned DUPO handler following BFCL's extension guide.

## API-Bank

Official project: https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/api-bank

This repository does not include a frozen API-Bank adapter. To reproduce the reported evaluation, implement the PLAN/TOOL parser as a small adapter against a pinned API-Bank checkout, add unit tests, and publish the adapter revision used for Table 2.

Report Level 1, Level 2, Level 3, and overall success separately. Keep raw model output so formatting and parser errors can be independently audited.

## Tau2

Official project: https://github.com/sierra-research/tau2-bench

Install from a pinned revision:

```bash
git clone https://github.com/sierra-research/tau2-bench
cd tau2-bench
uv sync
```

The paper reports Retail, Airline, and Telecom. Tau2 is stateful and uses both an agent and a simulated user, so the release record must also pin the user-simulator model, random seed, trial count, task IDs, and domain data. A current Tau2 run may not be directly comparable with the paper if tasks or scoring changed after the paper snapshot.

## Missing release artifacts

Before claiming paper reproduction, add a manifest containing the exact benchmark commits, adapter files, commands, raw-output hashes, and expected aggregate values for every model in the paper. Generated benchmark outputs are not bundled because a complete provenance manifest is not available.
