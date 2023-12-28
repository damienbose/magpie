import argparse
import json

scenarios = [
    "baseline.txt",
    "e-greedy.txt"
]

def set_up(args):
    # TODO: Split into buckets for k-fold cross validation






    cross_val_split = None
    with open(f'experiments/{args.results_dir}/cross_val_split.json', 'w') as file:
        json.dump(cross_val_split, file, indent=4)

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', type=str, default='setup', choices=['setup', 'train', 'test'])
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--results_dir', type=str, default='results')
    args = parser.parse_args()

    if args.step == 'setup':
        set_up(args)