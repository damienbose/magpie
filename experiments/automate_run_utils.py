import random
import json

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


def setup(args, num_folds=5, num_replications=5):
    # Generate the folds
    with open('experiments/benchmark/sat_uniform.json', 'r') as file:
        bins = json.load(file)

    folds = [[] for _ in range(num_folds)]

    for bin in bins:
        mini_fold = split_into_equal_random_subsets(bin, num_folds)
        for i in range(num_folds):
            folds[i] += mini_fold[i]
        
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

    with open(f'experiments/{args.results_dir}/cross_val_setup.json', 'w') as file:
        json.dump(cross_validation_setup, file, indent=4)