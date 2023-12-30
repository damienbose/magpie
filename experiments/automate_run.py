import argparse
import importlib
import traceback
import automate_run_utils as utils
importlib.reload(utils) # Reload instead of using cached version

# Cross validation setup
num_folds = 5
num_replications = 1

scenarios = [
    "baseline.txt",
    # "e-greedy.txt"
]

search_algos = [
    'RandomSearch',
    # 'BestImprovementNoTabu'
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', type=str, default='setup', choices=['setup', 'train', 'test'])
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--results_dir', type=str, default='experiments/results')
    args = parser.parse_args()

    # Seed
    utils.seed(args.seed)

    try:
        if args.step == 'setup':
            # Generate the cross-validation split
            utils.setup(args, num_folds, num_replications)
        elif args.step == 'train':
            # Run GI on the training set
            utils.train(args, scenarios, search_algos)
        elif args.step == 'test':
            pass
    except Exception:
        with open(f"{args.results_dir}/error_{args.step}.txt", 'w') as f:
            print(traceback.format_exc(), file=f)