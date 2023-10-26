import argparse
import configparser
import pathlib

import magpie


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magpie genetic programming')
    parser.add_argument('--scenario', type=pathlib.Path, required=True)
    parser.add_argument('--algo', type=str)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    # read scenario file
    config = configparser.ConfigParser()
    config.read_dict(magpie.core.default_scenario)
    config.read(args.scenario)
    magpie.core.pre_setup(config)

    # select GP algorithm
    if args.algo is not None:
        config['search']['algorithm'] = args.algo
    if config['search']['algorithm']:
        algo = magpie.core.utils.algo_from_string(config['search']['algorithm'])
        if not issubclass(algo, magpie.algos.GeneticProgramming):
            raise RuntimeError('{} is not a GP algorithm'.format(args.algo))
    else:
        config['search']['algorithm'] = 'GeneticProgrammingUniformConcat'
        algo = magpie.algos.GeneticProgrammingUniformConcat

    # setup protocol
    magpie.core.setup(config)
    protocol = magpie.core.utils.protocol_from_string(config['search']['protocol'])()
    protocol.search = algo()
    protocol.software = magpie.core.utils.software_from_string(config['software']['software'])(config)
    protocol.setup(config)

    # run experiments
    protocol.run()
