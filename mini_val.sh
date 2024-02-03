#!/bin/bash

result_dir="experiments/mini_experiments/results_100h_random_search/RandomSearch"
scenario="experiments/scenario/validate_scenario.ini"

for rl_algorithm in EpsilonGreedy ProbabilityMatching UCB UniformSelector
do
    for trial_no in trial_0 trail_1 trial_2 trial_3 trial_4
    do
        python3 -m bin.revalidate_patch --scenario $scenario --patch $result_dir/$rl_algorithm/$trial_no/logs/experiment.patch --output_dir $result_dir/$rl_algorithm/$trial_no
    done
done
