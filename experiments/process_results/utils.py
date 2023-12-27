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