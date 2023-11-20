# Go to the root of this project
cd $(git rev-parse --show-toplevel)

# Clear previous experiments
rm -rf _magpie_logs
rm -rf _magpie_work
rm -rf experiments/experiement_results

# Experiments: Local Search
python3 -m bin.local_search --scenario experiments/scenario/triangle_uniform.txt --algo FirstImprovement
python3 -m bin.local_search --scenario experiments/scenario/triangle_weighted.txt --algo FirstImprovement

# Experiments: Genetic Programming
python3 -m bin.genetic_programming --scenario experiments/scenario/triangle_uniform.txt --algo GeneticProgrammingUniformConcat
python3 -m bin.genetic_programming --scenario experiments/scenario/triangle_weighted.txt --algo GeneticProgrammingUniformConcat 

# Parse results and produce summary statistics
python3 experiments/parse_results.py --log_dir _magpie_logs --output_dir experiments/experiement_results