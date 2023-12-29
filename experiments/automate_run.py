import argparse
import json
import random

scenarios = [
    "baseline.txt",
    "e-greedy.txt"
]

def split_into_equal_random_subsets(arr, k):

    arr_temp = arr.copy()

    # Ensure the array can be divided into k equal subsets
    n = len(arr_temp)
    if n % k != 0:
        raise ValueError("Array size is not divisible by k")

    # Shuffle the array
    random.shuffle(arr_temp)

    # Calculate the size of each subset
    subset_size = n // k

    # Split the array into k subsets
    subsets = [arr_temp[i*subset_size:(i+1)*subset_size] for i in range(k)]
    return subsets


def set_up(args):
    num_folds = 5

    # 2. replication 0: train on 1-9, test on 10
    # 3. replication 1: train on 2-10, test on 1

    # Generate the folds
    with open('experiments/benchmark/sat_uniform.json', 'r') as file:
        bins = json.load(file)

    folds = [[] for _ in range(num_folds)]

    for bin in bins:
        mini_fold = split_into_equal_random_subsets(bin, num_folds)
        for i in range(num_folds):
            folds[i] += mini_fold[i]
        
    # Save the folds
    with open(f'experiments/{args.results_dir}/cross_val_split.json', 'w') as file:
        json.dump(folds, file, indent=4)

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', type=str, default='setup', choices=['setup', 'train', 'test'])
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--results_dir', type=str, default='results')
    args = parser.parse_args()

    # Seed
    random.seed(args.seed)
    if args.step == 'setup':
        set_up(args)