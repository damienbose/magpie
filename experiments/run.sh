#!/bin/bash

# Go to the root of this project
cd $(git rev-parse --show-toplevel)

# Clear previous experiments
rm -rf _magpie_logs
rm -rf _magpie_work
rm -rf experiments/results

# Where to put experiment output
result_dir="experiments/results"

# Experiments: Local Search
for i in {1..1}
do
    # RandomSearch: baseline and e-greedy
    python3 -m bin.local_search --scenario experiments/scenario/baseline.txt --algo RandomSearch --seed $i --output_dir $result_dir/baseline/RandomSearch/trial_$i
    python3 -m bin.local_search --scenario experiments/scenario/e-greedy.txt --algo RandomSearch --seed $i --output_dir $result_dir/epsilon_greedy/RandomSearch/trial_$i
    
    # RandomWalk: baseline and e-greedy
    python3 -m bin.local_search --scenario experiments/scenario/baseline.txt --algo RandomWalk --seed $i --output_dir $result_dir/baseline/RandomWalk/trial_$i
    python3 -m bin.local_search --scenario experiments/scenario/e-greedy.txt --algo RandomWalk --seed $i --output_dir $result_dir/epsilon_greedy/RandomWalk/trial_$i

    # BestImprovementNoTabu: baseline and e-greedy
    python3 -m bin.local_search --scenario experiments/scenario/baseline.txt --algo BestImprovementNoTabu --seed $i --output_dir $result_dir/baseline/BestImprovementNoTabu/trial_$i
    python3 -m bin.local_search --scenario experiments/scenario/e-greedy.txt --algo BestImprovementNoTabu --seed $i --output_dir $result_dir/epsilon_greedy/BestImprovementNoTabu/trial_$i

    # FirstImprovementNoTabu: baseline and e-greedy
    python3 -m bin.local_search --scenario experiments/scenario/baseline.txt --algo FirstImprovementNoTabu --seed $i --output_dir $result_dir/baseline/FirstImprovementNoTabu/trial_$i
    python3 -m bin.local_search --scenario experiments/scenario/e-greedy.txt --algo FirstImprovementNoTabu --seed $i --output_dir $result_dir/epsilon_greedy/FirstImprovementNoTabu/trial_$i
done

# Wait for all child processes to complete
wait

echo "All experiments complete!"

# Parse results and produce summary statistics
python3 -m experiments.parse_results --result_dir experiments/results