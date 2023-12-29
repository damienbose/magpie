import argparse
import importlib
import automate_run_utils as utils
importlib.reload(utils) # Reload instead of using cached version


scenarios = [
    "baseline.txt",
    "e-greedy.txt"
]

# Cross validation setup
num_folds = 5
num_replications = 3

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', type=str, default='setup', choices=['setup', 'train', 'test'])
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--results_dir', type=str, default='results')
    args = parser.parse_args()

    # Seed
    utils.seed(args.seed)

    if args.step == 'setup':
        utils.setup(args, num_folds, num_replications)