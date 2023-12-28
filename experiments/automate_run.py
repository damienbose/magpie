import argparse
import shutil

scenarios = [
    "baseline.txt",
    "e-greedy.txt"
]

def set_up(args):
    # Reset
    shutil.rmtree("experiments/benchmark", ignore_errors=True)
    shutil.rmtree("experiments/minisat", ignore_errors=True)

    # Copy the data
    shutil.copytree("examples/code/minisat/data/sat_uniform", "experiments/benchmark")
    shutil.copy("examples/code/minisat/data/sat_uniform.py", "experiments/benchmark/sat_uniform.py")

    # Copy code and remove the data subdirectory
    shutil.copytree("examples/code/minisat", "experiments/minisat")
    shutil.rmtree("experiments/minisat/data")


    print("done")

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', type=str, default='setup',
                        choices=['setup', 'train', 'test'])
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    if args.step == 'setup':
        set_up(args)