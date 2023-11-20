# Navigate to magpie root
cd ..

# Clean previous experiments
rm -rf _magpie_logs
rm -rf _magpie_work

# Run new expiriements
python3 -m bin.local_search --scenario experiments/scenario/triangle_uniform.txt
python3 -m bin.local_search --scenario experiments/scenario/triangle_weighted.txt