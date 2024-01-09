#!/bin/bash

# Go to the root of this project
cd $(git rev-parse --show-toplevel)


# Where to put experiment output
result_dir="experiments/results"

# Clear previous experiments
rm -rf _magpie_logs
rm -rf _magpie_work
rm -rf $result_dir

# Redirect output
mkdir -p $result_dir
exec > $result_dir/experiment_logs.txt

# Record start time
start_time=$(date +%s)

python3 experiments/automate_run.py --step setup --results_dir $result_dir
python3 experiments/automate_run.py --step train --results_dir $result_dir
# python3 experiments/automate_run.py --step test --results_dir $result_dir

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