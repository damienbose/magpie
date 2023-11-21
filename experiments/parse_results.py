import re, os
import sys
import argparse
from pathlib import Path
import glob
import pickle
import magpie

FLOAT_REGEX = r"[-+]?(?:\d*\.*\d+)"


def parse_results(result, output_dir):
    with open(output_dir / "result.txt", "w") as f:
        print(f"Results Summary", file=f)
        print(f"Starting Fitness: {result['initial_fitness']}", file=f)
        print(f"Best Fitness: {result['best_fitness']}", file=f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_dir", type=str)
    args = parser.parse_args()

    result_output_path = Path(args.result_dir)

    # Get the list of subdirectories in the results directory
    subdirectories = glob.glob(args.result_dir + '/*/*/*/')

    # Iterate over each subdirectory
    for subdirectory in subdirectories:
        # Check if the subdirectory is named "logs"
        if subdirectory.endswith('logs/'):
            # Get the path to the pickle file
            pickle_file = Path(subdirectory) / 'raw_result.pkl'

            # Load the pickle file
            with open(pickle_file, 'rb') as f:
                result = pickle.load(f)

            # Parse the results
            parse_results(result, Path(subdirectory).parent)
