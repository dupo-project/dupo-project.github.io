# Public release checklist

## Scientific alignment

- [ ] Confirm the exact implementation revision corresponding to the submitted paper.
- [ ] Resolve every mismatch in `REPRODUCIBILITY.md`.
- [ ] Freeze commands, seeds, environments, checkpoints, and raw evaluation outputs.
- [ ] Reproduce every published table from immutable artifacts.
- [ ] Have an independent maintainer verify at least one end-to-end run.

## Data and models

- [ ] Publish PlanArena with a version, hashes, data statement, and license.
- [ ] Verify that released records contain no private user data or proprietary API responses.
- [ ] Publish or link model checkpoints with hashes and model-card limitations.
- [ ] Record every upstream model revision and license.

## Legal and attribution

- [ ] Confirm copyright holders and the final code/data license split.
- [ ] Decide between an OSI-approved software license and a noncommercial source-available release; use matching public terminology.
- [ ] Add the final author list and canonical citation metadata.
- [ ] Complete third-party attribution and license review.
- [ ] Confirm that the paper and repository publication timelines are compatible.

## Security and privacy

- [ ] Run secret scanning over the full Git history, not only the working tree.
- [ ] Complete full-history secret scanning and remediate every finding before publication.
- [ ] Configure a monitored private security-reporting address.
- [ ] Confirm that release automation cannot upload private checkpoints or data.

## Usability

- [ ] Validate installation from a clean Linux host or container.
- [ ] Run `make check`, `make smoke`, and `make prepare-mini`.
- [ ] Run a one-batch GPU test with the documented environment.
- [ ] Validate BFCL v3, API-Bank, and Tau2 adapters from clean checkouts.
- [ ] Verify every README link and public download URL.

## Publication

- [ ] Tag a signed release and publish release notes.
- [ ] Archive the release and dataset in a durable public repository.
- [ ] Add the paper URL, DOI/arXiv identifier, and project homepage.
- [ ] Announce only claims backed by the frozen release artifacts.
