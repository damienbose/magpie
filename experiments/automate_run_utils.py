import random
import json
import subprocess
import configparser
import math
from pathlib import Path
import os
import copy
from tqdm import tqdm

def seed(seed):
    random.seed(seed)

def sample_k_random_test_cases(arr, k):
    return random.sample(arr, k)

def cross_val_setup(args, train_set_size=20, num_replications=5):
    # Generate the folds
    with open('examples/code/benchmark/sat_uniform.json', 'r') as file:
        bins = json.load(file)

    # Use absolute paths for test cases & SAT/UNSAT label
    in_path = "/cs/student/ug/2020/damibose/projects/magpie/examples/code/benchmark"
    for bin in bins:
        for i, elem in enumerate(bin):
            test_case_type = 'SAT' if elem.split('/')[-1].count('u') == 1 else 'UNSAT'
            bin[i] = f"{in_path}/{elem} {test_case_type}"
    
    # Split into train test
    train_sets = [[] for _ in range(num_replications)]
    
    assert train_set_size % len(bins) == 0, "There must be equal distribution of each test case type in train_set"
    
    test_cases_picked_so_far = set()
    num_from_each_type = train_set_size // len(bins)
    for i in range(num_replications):
        for bin in bins:
            test_cases = sample_k_random_test_cases(bin, num_from_each_type)
            test_cases_picked_so_far.update(test_cases) # Make sure we don't pick the same test case twice
            train_sets[i].append(sample_k_random_test_cases(set(bin) - test_cases_picked_so_far, num_from_each_type))
    
    # Generate the replications
    replications = {}
    for replication_num in range(num_replications):
        replications[replication_num] = {"train_test_cases": train_sets[replication_num]}
    
    cross_validation_setup = {}
    cross_validation_setup['train_set_size'] = train_set_size
    cross_validation_setup['num_replications'] = num_replications
    cross_validation_setup['replications'] = replications
    cross_validation_setup['all_test_cases'] = bins

    os.makedirs(args.results_dir, exist_ok=True)
    with open(f'{args.results_dir}/cross_val_setup.json', 'w') as file:
        json.dump(cross_validation_setup, file, indent=4)
    
    return cross_validation_setup

def set_operator_selector_config(config, operator_selector):
    config["search"]["operator_selector"] = operator_selector
    if operator_selector == 'UniformSelector':
        pass # No additional config required
    elif operator_selector == 'WeightedSelector':
        initial_weights = [1]*8 + [0]*4 # No delete operators
        config["search"]["initial_weights"] = '\n' + '\n'.join([str(weight) for weight in initial_weights])
    elif operator_selector == 'EpsilonGreedy':
        config["search"]["epsilon"] = "0.2"
    elif operator_selector == 'ProbabilityMatching':
        num_operators = len(config["search"]["possible_edits"].split('\n')) - 1
        config["search"]["p_min"] = f"{1/(2 * num_operators)}"
    elif operator_selector == 'UCB':
        config["search"]["c"] = f"{math.sqrt(2)}" # COMP0089: c=root(2) is used in the lectures for log expected regret
    elif operator_selector == 'PolicyGradient':
        config["search"]["alpha"] = "0.1" # Learning rate: sutton and barto


def set_batch_config(config, replication_num, cross_validation_setup):
    bins = copy.deepcopy(cross_validation_setup['replications'][replication_num]['train_test_cases'])
    config["search"]["batch_sample_size"] = str(sum([len(bin) for bin in bins]))
    for i in range(len(bins)):
        bins[i] = '\n'.join(bins[i])
    bins = '\n' + '\n___\n'.join(bins)
    config["search"]["batch_instances"] = bins

def scenario_config_setup(args, operator_selectors, search_algos, num_replications, cross_validation_setup, debug_mode=False):
    for operator_selector in operator_selectors:
        for algo in search_algos:
            for replication_num in range(num_replications):
                config = configparser.ConfigParser()
                config_file = "experiments/scenario/template.ini" if not debug_mode else "experiments/scenario/debug.ini"
                config.read(config_file)
                set_operator_selector_config(config, operator_selector)
                set_batch_config(config, replication_num, cross_validation_setup)
                path = f"{args.results_dir}/{algo}/{operator_selector}/trial_{replication_num}/scenario.ini"
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w') as configfile:
                    config.write(configfile)

def setup(args, train_set_size, num_replications, operator_selectors, search_algos, debug_mode=False):
    cross_validation_setup = cross_val_setup(args, train_set_size, num_replications)
    scenario_config_setup(args, operator_selectors, search_algos, num_replications, cross_validation_setup, debug_mode)

def train(args, operator_selectors, search_algos, num_replications):
    commands = []
    for i in range(num_replications):
        # Train on the training folds
        for operator_selector in operator_selectors:
            for algo in search_algos:
                scenario = f"{args.results_dir}/{algo}/{operator_selector}/trial_{i}/scenario.ini"
                command = f"python3 -m bin.local_search --scenario {scenario} --algo {algo} --seed {i} --output_dir {args.results_dir}/{algo}/{operator_selector}/trial_{i}"
                commands.append(command)
    
    for command in tqdm(commands, desc="Training Progress", file=open(f"{args.results_dir}/train_progress_logs.txt", 'a')):
        print(command, flush=True, file=open(f"{args.results_dir}/train_commands_logs.txt", 'a'))
        subprocess.run(command, shell=True, text=True)

    # Delete the progress file
    os.remove(f"{args.results_dir}/train_progress_logs.txt")
def test(args, operator_selectors, search_algos, num_replications):
    pass