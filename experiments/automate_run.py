import argparse
import importlib
import traceback
import automate_run_utils as utils
importlib.reload(utils) # Reload instead of using cached version

is_debug_mode = False

MAX_SUB_PROCESSES = 4

# Cross validation setup
train_set_size = 20
num_replications = 4

operator_selectors = [
    # 'UniformSelector',
    # 'WeightedSelector',
    # 'EpsilonGreedy',
    # 'ProbabilityMatching',
    # 'UCB',
    'PolicyGradient'
]

search_algos = [
    'RandomSearch',
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
            utils.setup(args, train_set_size, num_replications, operator_selectors, search_algos, debug_mode=is_debug_mode)
        elif args.step == 'train':
            # Run GI on the training set
            utils.train(args, operator_selectors, search_algos, num_replications, MAX_SUB_PROCESSES=MAX_SUB_PROCESSES)
        elif args.step == 'test':
            # Run on validation set
            utils.test(args, operator_selectors, search_algos, num_replications)
    except Exception:
        with open(f"{args.results_dir}/error_{args.step}.txt", 'w') as f:
            print(traceback.format_exc(), file=f)
        raise