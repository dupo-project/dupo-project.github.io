# SPDX-License-Identifier: CC-BY-NC-4.0
"""Download a model from ModelScope into a user-selected cache directory."""

import argparse

from modelscope.hub.snapshot_download import snapshot_download


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True, help="ModelScope model id")
    parser.add_argument("--cache-dir", required=True, help="Destination cache directory")
    args = parser.parse_args()
    model_dir = snapshot_download(args.model_id, cache_dir=args.cache_dir)
    print(model_dir)


if __name__ == "__main__":
    main()
