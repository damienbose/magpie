import random
import json
import subprocess
import configparser
import math
from pathlib import Path

def seed(seed):
    random.seed(seed)

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


def cross_val_setup(args, num_folds=5, num_replications=5):
    # Generate the folds
    with open('examples/code/benchmark/sat_uniform.json', 'r') as file:
        bins = json.load(file)

    # Instance path
    in_path = "/cs/student/ug/2020/damibose/projects/magpie/examples/code/benchmark"
    for bin in bins:
        for i, elem in enumerate(bin):
            bin[i] = f"{in_path}/{elem}"

    # Make sure correct path is used
    folds = [[] for _ in range(num_folds)]

    for bin in bins:
        mini_fold = split_into_equal_random_subsets(bin, num_folds)
        for i in range(num_folds):
            folds[i].append(mini_fold[i])
        
    assert num_replications <= num_folds

    # Generate the replications
    replications = {}
    for replication_num in range(num_replications):
        test_folds = [replication_num]
        train_folds = [i for i in range(num_folds) if i not in test_folds]
        replications[replication_num] = {"train_folds" : train_folds, "test_folds" : test_folds}
    
    cross_validation_setup = {}
    cross_validation_setup['num_folds'] = num_folds
    cross_validation_setup['num_replications'] = num_replications
    cross_validation_setup['folds'] = {i : folds[i] for i in range(num_folds)}
    cross_validation_setup['replications'] = replications

    with open(f'{args.results_dir}/cross_val_setup.json', 'w') as file:
        json.dump(cross_validation_setup, file, indent=4) # TODO: seperate into bins
    
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


def set_batch_config(config, replication_num, cross_validation_setup):
    return # TODO
    train_folds = [cross_validation_setup['folds'][i] for i in cross_validation_setup['replications'][replication_num]['train_folds']]
    # config["search"]["batch_sample_size"] = str(sum([len(fold) for fold in train_folds]))
    for i in range(len(train_folds)):
        train_folds[i] = '\n'.join(train_folds[i])
    train_folds = '\n' + '\n___\n'.join(train_folds)
    config["search"]["batch_instances"] = train_folds
    config["search"]["batch_sample_size"] = "5" # Maybe add to template?

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

def setup(args, num_folds, num_replications, operator_selectors, search_algos, debug_mode=False):
    cross_validation_setup = cross_val_setup(args, num_folds, num_replications)
    scenario_config_setup(args, operator_selectors, search_algos, num_replications, cross_validation_setup, debug_mode)

def train(args, operator_selectors, search_algos, num_replications):
    for i in range(num_replications):
        # Train on the training folds
        for operator_selector in operator_selectors:
            for algo in search_algos:
                scenario = f"{args.results_dir}/{algo}/{operator_selector}/trial_{i}/scenario.ini"
                command = f"python3 -m bin.local_search --scenario {scenario} --algo {algo} --seed {i} --output_dir {args.results_dir}/{algo}/{operator_selector}/trial_{i}"
                print(command)
                subprocess.run(command, shell=True, text=True)

def test(args, operator_selectors, search_algos, num_replications):
    pass