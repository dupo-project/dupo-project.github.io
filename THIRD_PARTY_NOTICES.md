# Third-party notices

## verl

The `verl/` subtree is a runtime-only distribution derived from the Volcano Engine Reinforcement Learning project (`volcengine/verl`), version marker `0.3.1.dev`, and includes modifications for the DUPO/DeepAction training recipe. Upstream examples, recipes, documentation builds, and test artifacts are not redistributed here.

- Upstream: https://github.com/volcengine/verl
- License: Apache License 2.0
- Local license text: `verl/LICENSE`

Files that retain Apache-2.0 headers remain governed by those headers. The subtree is kept separate so downstream users can identify the upstream component and its modifications.

## Benchmarks and models

BFCL, API-Bank, Tau2, Qwen, Llama, and any downloaded datasets or model weights are not redistributed by this repository. Users must obtain them from their official sources and comply with their respective licenses. The submitted paper notes that Qwen2.5-3B uses the Qwen Research License, while other model and benchmark variants may use different terms.

Before publication, the project owner should run a formal third-party license review and add any required attribution for the final dataset, checkpoints, paper figures, and public hosting artifacts.

## Release terminology

The current root license follows the paper's CC BY-NC 4.0 statement. Noncommercial restrictions do not satisfy the Open Source Definition's requirement against field-of-endeavor restrictions, and Creative Commons recommends software-specific licenses instead of CC licenses for code:

- https://opensource.org/osd
- https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software

Until the owner selects an approved software license, this repository should be described as source-available rather than OSI open source.
