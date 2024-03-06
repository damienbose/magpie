import subprocess
import json
import os

def gen_for_test_case(test_case, root_dir, out_path):
    # Make a copy of minisat directory
    print(f"Generating coverage for {test_case}")

    subprocess.run(['cp', '-r', 'examples/code/minisat', 'experiments/generate_coverage/minisat'])

    os.chdir('experiments/generate_coverage/minisat')
    subprocess.run(["./compile_coverage.sh"])
    subprocess.run(f"./run_single_with_code.sh {test_case}")
    subprocess.run(f"gcovr --txt-metric branch --txt-report-covered -f core/Solver.cc > {out_path}/{test_case.split('/')[-1].split(' ')[0]}.txt", shell=True)
    os.chdir(root_dir)

    # Clean up
    os.remove('experiments/generate_coverage/minisat')


if __name__ == "__main__":
    root_dir = os.getcwd()
    out_path = root_dir + "/experiments/generate_coverage/outputs"

    # Make sure clean 
    os.remove('experiments/generate_coverage/minisat')

    # Generate the folds
    with open('examples/code/benchmark/sat_uniform.json', 'r') as file:
        bins = json.load(file)

    # Use absolute paths for test cases & SAT/UNSAT label
    in_path = root_dir + "/examples/code/benchmark"
    for bin in bins:
        for i, elem in enumerate(bin):
            test_case_type = 'SAT' if elem.split('/')[-1].count('u') == 1 else 'UNSAT'
            bin[i] = f"{in_path}/{elem} {test_case_type}"

    # Make the directory
    os.makedirs(out_path, exist_ok=True)
    test_cases = [test_case for bin in bins for test_case in bin]
    for test_case in test_cases:
        gen_for_test_case(test_case, root_dir, out_path)