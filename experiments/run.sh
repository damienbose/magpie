#!/bin/bash

# Go to the root of this project
cd $(git rev-parse --show-toplevel)


# Where to put experiment output
result_dir="experiments/results_e_greedy_proof_of_concept"

# Clear previous experiments
rm -rf _magpie_logs
rm -rf _magpie_work
rm -rf $result_dir

# Rediect output
mkdir -p $result_dir
exec > $result_dir/experiment_run_statistics.txt

# Record start time
start_time=$(date +%s)


# Experiments: Local Search
for i in {1..10}
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

# Record end time
end_time=$(date +%s)
duration=$((end_time - start_time))
# Convert duration to hours, minutes, and seconds
hours=$((duration / 3600))
minutes=$(( (duration % 3600) / 60))
seconds=$((duration % 60))
# Print the duration in HH:MM:SS format
printf "Total execution time: %02d:%02d:%02d\n" $hours $minutes $seconds

# Parse results and produce summary statistics
python3 -m experiments.parse_results --result_dir experiments/results