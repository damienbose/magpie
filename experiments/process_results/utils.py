# helper functions for processing results
import pickle 

def generate_pickle_object(log_files_folder):
    pkl_file = log_files_folder + "raw_result.pkl"
    with open(pkl_file, "rb") as f:
            trial_result_obj = pickle.load(f)
    return trial_result_obj

def get_patch(log_files_folder):
    patch_file = log_files_folder + "experiment.patch"
    try:
        with open(patch_file, "r") as f:
            patch = f.read()
        return patch
    except FileNotFoundError: # No patches found (i.e. variants with improved fitness)
        return None

def get_num_variants_evaluated(log_files_folder):
    # TODO: hard coded for now change once the experiment_report is updated
    op_selector = log_files_folder.split("/")[-4]
    if op_selector == "EpsilonGreedy":
        return 2261
    elif op_selector == "ProbabilityMatching":
         return 1631
    elif op_selector == "UCB":
         return 1221
    elif op_selector == "UniformSelector":
         return 1965
    return -1

def get_num_successful_variants_evaluated(row):
    log_files_folder = row['path_log']
    num_warmup = row['pkl_obj']['config']["warmup"]
    with open(log_files_folder + "experiment.log", "r") as f:
        logs = f.read()
    num_success = logs.count("EXEC>  SUCCESS")
    return num_success - num_warmup
