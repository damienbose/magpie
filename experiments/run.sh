#!/bin/bash

# Go to the root of this project
cd $(git rev-parse --show-toplevel)

# Clear previous experiments
rm -rf _magpie_logs
rm -rf _magpie_work
rm -rf experiments/results

# Experiments: Local Search
for i in {1..1}
do
    python3 -m bin.local_search --scenario experiments/scenario/test_example.txt --algo RandomSearch --seed $i --output_dir experiments/results/epsilon_greedy/random_search/trial_$i
done

# Parse results and produce summary statistics
python3 -m experiments.parse_results --result_dir experiments/results