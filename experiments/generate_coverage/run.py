import subprocess
import json
import os

if __name__ == "__main__":
    # Generate the folds
    with open('examples/code/benchmark/sat_uniform.json', 'r') as file:
        bins = json.load(file)

    # Use absolute paths for test cases & SAT/UNSAT label
    root_dir = os.getcwd()
    in_path = root_dir + "/examples/code/benchmark"
    for bin in bins:
        for i, elem in enumerate(bin):
            test_case_type = 'SAT' if elem.split('/')[-1].count('u') == 1 else 'UNSAT'
            bin[i] = f"{in_path}/{elem} {test_case_type}"
    
    # Make a copy of minisat directory
    subprocess.run(['cp', '-r', 'examples/code/minisat', 'experiments/generate_coverage/minisat'])