import logging

import os

import sys
import yaml
from flatdict import FlatDict

if __name__ == 'main':
    sys.exit('configparser.py should not be called as a script, but should instead be called from other scripts.')


def parse(config_file):
    config = {'config_modified_time': os.path.getmtime(config_file)}
    stream = open(config_file, 'r')
    config.update(yaml.load(stream))

    # Change the value of the $ref tags in the dictionary.
    config = FlatDict(config)
    ref = []

    for key in config:
        if '$ref' in key:
            config[key.replace(':$ref', '')] = config[config[key].replace('#/', '').replace('/', ':')]
    config = config.as_dict()
    # print(config)
    stream.close()

    # Setup logging,
    level = logging.getLevelName(config['logging']['level'])

    logging.basicConfig(level=level)

    # Setup backoff logging for when we get URL errors.
    logging.getLogger('backoff').addHandler(logging.StreamHandler())
    logging.getLogger('backoff').setLevel(level)

    return config
