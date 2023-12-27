import re, os
import sys
import argparse
from pathlib import Path
import glob
import pickle
import magpie
import pandas as pd

def create_table_empty_table():
    # Define the columns for the new dataframe
    columns = ["search_algorithm", "rl_algorithm", "trial_number", "raw_result_file_path"] # TODO: fill in these statistics then make a jupyter notebook 
    df_final = pd.DataFrame(columns=columns)
    return df_final

df_final = create_table_empty_table() # Where we store final results

def process_trial(trial_result, output_dir):
    with open(output_dir / "result.txt", "w") as f:
        print(f"Results Summary", file=f)
        print(f"Starting Fitness: {trial_result['initial_fitness']}", file=f)
        print(f"Best Fitness: {trial_result['best_fitness']}", file=f)

def process_rl_algorithm(directory):
    # Get the name of the algorithm
    algorithm_name = directory.split("/")[-2]
    print(f"Processing {algorithm_name}...")

    # Get the list of subdirectories in the results directory
    subdirectories = glob.glob(directory + '/*/')

    # Iterate over each subdirectory
    for trial_dir in subdirectories:
        pickle_file = Path(trial_dir) / "logs/raw_result.pkl"

        with open(pickle_file, "rb") as f:
            trial_result_obj = pickle.load(f)
        
        process_trial(trial_result_obj, Path(trial_dir))

def process_search_algorithm(directory):
    # Get the name of the algorithm
    algorithm_name = directory.split("/")[-2]
    print(f"Processing {algorithm_name}...")

    subdirectories = glob.glob(directory + '/*/')

    # Iterate over each subdirectory
    for subdirectory in subdirectories:
        process_rl_algorithm(subdirectory)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_dir", type=str)
    args = parser.parse_args()

    result_output_path = Path(args.result_dir)

    # Get the list of subdirectories in the results directory
    subdirectories = glob.glob(args.result_dir + '/*/')

    # Iterate over each subdirectory
    for subdirectory in subdirectories:
        process_search_algorithm(subdirectory)
    
    # Save the final dataframe
    df_final.to_csv(result_output_path / "results.csv", index=False)
