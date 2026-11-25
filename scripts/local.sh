#!/usr/bin/env bash
set -euo pipefail
python -m eco.validate
python -m pytest -q
python -m eco.train
printf '
Lire reports/candidate.json puis promouvoir explicitement la version choisie.
'
