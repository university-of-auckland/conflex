import yaml

stream = open('config.yaml', 'r')
config = yaml.load(stream)
stream.close()
