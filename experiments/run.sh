#!/bin/bash

# Go to the root of this project
cd $(git rev-parse --show-toplevel)


# Where to put experiment output
result_dir="experiments/results"

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
for i in {1..2}
do
    # RandomSearch: baseline and e-greedy
    python3 -m bin.local_search --scenario experiments/scenario/baseline.txt --algo RandomSearch --seed $i --output_dir $result_dir/RandomSearch/baseline/trial_$i
    python3 -m bin.local_search --scenario experiments/scenario/e-greedy.txt --algo RandomSearch --seed $i --output_dir $result_dir/RandomSearch/epsilon_greedy/trial_$i

    # BestImprovementNoTabu: baseline and e-greedy
    python3 -m bin.local_search --scenario experiments/scenario/baseline.txt --algo BestImprovementNoTabu --seed $i --output_dir $result_dir/BestImprovementNoTabu/baseline/trial_$i
    python3 -m bin.local_search --scenario experiments/scenario/e-greedy.txt --algo BestImprovementNoTabu --seed $i --output_dir $result_dir/BestImprovementNoTabu/epsilon_greedy/trial_$i
done

# Wait for all child processes to complete
wait

echo "All experiments completed!" 

# Record end time
end_time=$(date +%s)
duration=$((end_time - start_time))
# Convert duration to hours, minutes, and seconds
hours=$((duration / 3600))
minutes=$(( (duration % 3600) / 60))
seconds=$((duration % 60))
# Print the duration in HH:MM:SS format
printf "Total execution time: %02d:%02d:%02d\n" $hours $minutes $seconds