import argparse
import shutil

scenarios = [
    "baseline.txt",
    "e-greedy.txt"
]

def set_up(args):
    # Define the source and destination paths
    source_path = '/path/to/source/file.ext'
    destination_path = '/path/to/destination/file.ext'
    shutil.copy(source_path, destination_path)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', type=str, default='check',
                        choices=['setup', 'training', 'test'])
    parser.add_argument('--seed', type=int, default=123)
    args = parser.parse_args()

    if args.step == 'setup':
        set_up(args)