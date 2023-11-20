

import re, os
import sys
import argparse
from pathlib import Path

FLOAT_REGEX = r"[-+]?(?:\d*\.*\d+)"


def parse_results(result, output_dir):
    # Name of algorithm
    algorithm = re.findall(r"algorithm = (.*)", result)[0]

    # Create the directory if it does not exist
    output_dir = Path(output_dir) / algorithm
    output_dir.mkdir(parents=True, exist_ok=True)

    # Name of operator selection technique
    operator_selector = re.findall(r"operator_selector = (.*)", result)[0]

    # Create the directory if it does not exist
    output_dir = Path(output_dir) / operator_selector
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "result.txt", "w") as f:
        # Fitness Summary
        starting_fitness = [*map(float, re.findall(r"INITIAL SUCCESS\s+(" + FLOAT_REGEX + r")", result))][0]
        best_fitness = [*map(float, re.findall(r"Best fitness: (" + FLOAT_REGEX + r")", result))][0]

        print(f"Results Summary", file=f)
        print(f"Starting Fitness: {starting_fitness:.4f}", file=f)
        print(f"Best Fitness: {best_fitness:.4f}", file=f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_dir", type=str)
    parser.add_argument("--output_dir", type=str)
    args = parser.parse_args()

    log_path = Path(args.log_dir)
    result_output_path = Path(args.output_dir)

    # Get all log files for all experiments
    log_files = [f for f in log_path.glob("**/*.log") if f.is_file()]

    for log_file in log_files:
        with open(log_file) as f:
            parse_results(f.read(), result_output_path)
    