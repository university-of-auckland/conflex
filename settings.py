import yaml
from flatdict import FlatDict

stream = open('config.yaml', 'r')
config = yaml.load(stream)

# Change the value of the $ref tags in the dictionary.
config = FlatDict(config)
ref = []

for key in config:
    if '$ref' in key:
        config[key.replace(':$ref', '')] = config[config[key].replace('#/', '').replace('/', ':')]

config = config.as_dict()
stream.close()
