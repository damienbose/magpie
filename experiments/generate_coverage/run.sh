#!/bin/bash

# Go to the root of this project
cd $(git rev-parse --show-toplevel)

python3 experiments/generate_coverage/run.py