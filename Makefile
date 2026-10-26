.PHONY: check smoke prepare-mini dry-run

check:
	python scripts/check_release.py
	bash -n deepaction/train_dupo.sh deepaction/train_grpo.sh

smoke:
	PYTHONPATH="$(CURDIR)/verl" python scripts/smoke_reward.py

prepare-mini:
	python scripts/prepare_data.py --input examples/mini_planarena.json --output-dir data/mini

dry-run:
	DATA_DIR="$(CURDIR)/data/mini" BASE_MODEL="Qwen/Qwen2.5-3B-Instruct" DRY_RUN=1 bash deepaction/train_dupo.sh
