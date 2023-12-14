# Go to the root of this project
cd $(git rev-parse --show-toplevel)

# Clear previous experiments
rm -rf _magpie_logs
rm -rf _magpie_work
rm -rf experiments/results

# Experiments: Local Search
for i in {1..3}
do
    # Maybe worth changing the seed and the number of iterations here in a more robust manner; possible solution for trial number is to do the trials sequentially
    echo "Running Sanity Check"
    python3 -m bin.local_search --scenario experiments/scenario/sanity_check.txt --algo FirstImprovement
    python3 -m bin.local_search --scenario experiments/scenario/triangle_uniform.txt --algo FirstImprovement
done

# Parse results and produce summary statistics
python3 -m experiments.parse_results --result_dir experiments/results

# TEST