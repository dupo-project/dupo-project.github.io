# Contributing

Thank you for helping improve DUPO. Please keep changes small, reviewable, and reproducible.

## Before opening a change

1. Create a focused branch.
2. Do not commit model weights, datasets, benchmark outputs, API keys, or machine-specific filesystem paths.
3. Keep algorithm changes separate from documentation, packaging, or infrastructure changes.
4. For an algorithm change, document the affected equation or mechanism and include an ablation or unit test.
5. Preserve third-party copyright and license headers under `verl/`.

## Local checks

```bash
python scripts/check_release.py
PYTHONPATH="$PWD/verl" python scripts/smoke_reward.py
bash -n deepaction/train_dupo.sh deepaction/train_grpo.sh
```

If the full development dependencies are installed:

```bash
python -m compileall -q scripts verl/verl
```

GPU training and benchmark runs must record the code commit, model revision, dataset version, command, hardware, random seed, and output artifact path.

## Pull request checklist

- [ ] The change is scoped and described.
- [ ] Public documentation is updated.
- [ ] No secrets, non-public hosts, machine-specific paths, or large generated files are included.
- [ ] Tests or validation evidence are attached.
- [ ] Paper-facing result claims link to frozen evaluation artifacts.
- [ ] Licensing implications were reviewed for new data, code, or model dependencies.
