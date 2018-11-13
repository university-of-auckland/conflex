import argparse
import logging
import os
import datetime
import config_parser
from database.api import DatabaseAPI

# Imports the Google Cloud client library
from google.cloud import datastore


def run(config):
    client = datastore.Client()
    entity = datastore.Entity()
    client.put(entity)
    logger.error('error.')


if __name__ == '__main__':
    # Argument parsing.
    parser = argparse.ArgumentParser(description='Connex Wiki Integration Application.')
    parser.add_argument('--config', action='store', help='the location of the configuration file to run the application with.')
    args = parser.parse_args()

    conf = config_parser.parse(args.config or os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.yaml')))

    # Change working directory to parent so DatabaseAPI works.
    os.chdir('../')

    # Setup logging,
    logger = logging.getLogger(__name__)
    logger.info('Datastore Sync starting at: %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    DatabaseAPI.connect(conf)

    # Run the datastore tool.
    run(conf)

    DatabaseAPI.disconnect()
    logger.info('Datastore Sync finished at: %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))