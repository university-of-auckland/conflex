from confluence.api import ConfluenceAPI
from database.api import DatabaseAPI
from flatdict import FlatDict
import pandas as pd
import application_inventory
import config_parser
import os
import re
import logging
import datetime
import argparse
VERSION = '1.3.2'

# noinspection PyTypeChecker,PyShadowingNames
def child_page_recursive(pages, space_id, parent_page_id, table_prefix, recheck_pages_meet_criteria=False, config_modified=False):
    """Recursively inserts page information into the database after making requests to the Confluence API.

    Args:
        pages (dict): A dictionary of pages to crawl through, have a look at the example config for more information.
        space_id (int): The top level space_id that the information relates to.
        parent_page_id (int): The current pages parent page id.
        table_prefix (str): The current database table name prefix.
        recheck_pages_meet_criteria (bool): Ensures that all current pages meet the criteria set out in the config file.
            If this is False, it will assume that all pages in the database meet the criteria and will only take delta changes for these.
        config_modified (bool): Whether the config has been modified since last launch.
    """
    # if the child page has not been updated since we last stored the information, then no need to check labels/title!
    for page_type in pages:
        for page_identifier in pages[page_type]:

            # Create tables to store the pages in and the information they contain.
            # table = table_prefix + '_' + page_type + '_' + page_identifier
            table = table_prefix.replace(
                ' ', '') + '_' + page_identifier.replace('_', '').replace(' ', '')[:5].lower()
            DatabaseAPI.create_table(table)
            info_table = table + '__info'
            DatabaseAPI.create_table(info_table, True)

            child_pages = ConfluenceAPI.get_child_page_ids(parent_page_id)
            for child_page_id in child_pages:

                # Decision tree to see if the current page meets the criteria provided in the config file.
                # if we are not forced to recheck the page meets the criteria then use the pages in the database table.
                # else, check to see if the page meets either criteria.
                page_meets_criteria = False
                if not recheck_pages_meet_criteria and not config_modified:
                    if DatabaseAPI.check_data_exists(table, parent_page_id, child_page_id):
                        # If the page already exists in the database ignore checking the page meets the criteria, unless forced to.
                        page_meets_criteria = True
                else:
                    if page_type == 'titles':
                        if child_pages[child_page_id]['name'] == page_identifier:
                            page_meets_criteria = True
                    elif page_type == 'labels':
                        if page_identifier in ConfluenceAPI.get_page_labels(child_page_id):
                            # Check that the page meets the criteria given, i.e. it is labelled as something/title is something and needs to be updated.
                            page_meets_criteria = True

                if page_meets_criteria:
                    page_updated = DatabaseAPI.insert_or_update(
                        table, parent_page_id, child_page_id, child_pages[child_page_id]['name'], child_pages[child_page_id]['last_updated'], True)

                    # If the current page information was updated since the last run, delete all children information and re-fill it.
                    page_content = ''
                    if page_updated or config_modified:
                        logger.info('Updating information in space %s for page: %s' % (
                            str(space_id), child_pages[child_page_id]['name']))
                        DatabaseAPI.delete(info_table, child_page_id)
                        page_content = ConfluenceAPI.get_page_content(
                            child_page_id)

                    for page_info_type in pages[page_type][page_identifier]:
                        if page_info_type == 'pages':
                            child_page_recursive(pages[page_type][page_identifier][page_info_type], space_id,
                                                 child_page_id, table, recheck_pages_meet_criteria, config_modified)
                        else:
                            if page_updated or config_modified:
                                try:
                                    if page_info_type == 'panels':
                                        for panel_identifier in pages[page_type][page_identifier][page_info_type]:
                                            panel = FlatDict(ConfluenceAPI.get_panel(
                                                page_content, panel_identifier, space_id))
                                            for k, v in panel.items():
                                                # For each key remove list numbers. i.e. FlatDict will put in :0, :1: for each list element.
                                                k = re.sub(':(\d+)', '', k)
                                                k = re.sub(':(\d+):', ':', k)
                                                DatabaseAPI.insert_or_update(
                                                    info_table, child_page_id, k, v, child_pages[child_page_id]['last_updated'])
                                    elif page_info_type == 'page_properties':
                                        # Get all page properties and put the values into the database.
                                        page_properties = ConfluenceAPI.get_page_properties(
                                            child_page_id, space_id, pages[page_type][page_identifier][page_info_type])
                                        for page_property in page_properties:
                                            for val in page_properties[page_property]:
                                                DatabaseAPI.insert_or_update(
                                                    info_table, child_page_id, page_property, val, child_pages[child_page_id]['last_updated'])
                                    elif page_info_type == 'headings':
                                        for heading_identifier in pages[page_type][page_identifier][page_info_type]:
                                            heading = FlatDict(ConfluenceAPI.get_heading(
                                                page_content, heading_identifier))
                                            for k, v in heading.items():
                                                # For each key remove list numbers. i.e. FlatDict will put in :0, :1: for each list element.
                                                k = re.sub(':(\d+)', '', k)
                                                k = re.sub(':(\d+):', ':', k)
                                                DatabaseAPI.insert_or_update(
                                                    info_table, child_page_id, k, v, child_pages[child_page_id]['last_updated'])
                                    elif page_info_type == 'page':
                                        page_information = FlatDict(ConfluenceAPI.get_page(
                                            page_content, child_pages[child_page_id]['name']))
                                        for k, v in page_information.items():
                                            # For each key remove list numbers. i.e. FlatDict will put in :0, :1: for each list element.
                                            k = re.sub(':(\d+)', '', k)
                                            k = re.sub(':(\d+):', ':', k)
                                            DatabaseAPI.insert_or_update(
                                                info_table, child_page_id, k, v, child_pages[child_page_id]['last_updated'])
                                    elif page_info_type == 'url':
                                        for url_type in pages[page_type][page_identifier][page_info_type]:
                                            url = ConfluenceAPI.get_page_urls(
                                                child_page_id, url_type)
                                            DatabaseAPI.insert_or_update(
                                                info_table, child_page_id, url_type, url, child_pages[child_page_id]['last_updated'])
                                    else:
                                        logger.warning(
                                            'child_page_recursive: Unknown page information retrieval type: %s' % page_info_type)
                                except:
                                    logger.error('child_page_recursive: Error inserting data for page with id: %s, name: %s' % (
                                        str(child_page_id), child_pages[child_page_id]['name']))
                else:
                    # Cleanup the ignore, info and default table by removing any information associated with page.
                    # Child pages get cleaned up by the cleanup method.
                    DatabaseAPI.delete(table, parent_page_id, child_page_id)
                    DatabaseAPI.delete(info_table, child_page_id)


def recursive_db_cleanup(pages, space_id, table_prefix, mode):
    """Recursively remove page information from the database by checking if the current page still exists in the database.

    Args:
        pages (dict): A dictionary of pages to crawl through, have a look at the example config for more information.
        space_id (int): The top level space_id that the information relates to.
        table_prefix (str): The current database table name prefix.
        mode (bool): Only perform cleanup during a full sync.
    """
    if mode:
        for page_type in pages:
            for page_identifier in pages[page_type]:
                # Determine the table name that we are looking in.
                table = table_prefix.replace(
                    ' ', '') + '_' + page_identifier.replace('_', '').replace(' ', '')[:5].lower()
                info_table = table + '__info'
                child_pages = DatabaseAPI.select(table)

                # For each of the child pages check to see if they still exist, if they do not then delete the page.
                for child_page in child_pages:
                    # See if the parent page exists in the database if not then we can immediately delete this child
                    # page.
                    parent_exists = True
                    if space_id != child_page['parent']:
                        parent_exists = len(DatabaseAPI.select(
                            table_prefix.replace(' ', ''), None, child_page['parent'])) != 0
                    exists = ConfluenceAPI.check_page_exists(child_page['key'])

                    # The page does not exist on the wiki or the parent does not exist so delete it from the database
                    # along with the info.
                    if not parent_exists or not exists:
                        logger.info("recursive_db_cleanup: Deleting page with id: %s, Name: %s" % (
                            str(child_page['key']), child_page['value']))
                        DatabaseAPI.delete(
                            table, child_page['parent'], child_page['key'])
                        DatabaseAPI.delete(info_table, child_page['key'])

                # Go down the next level and remove these pages.
                for page_info_type in pages[page_type][page_identifier]:
                    if page_info_type == 'pages':
                        recursive_db_cleanup(
                            pages[page_type][page_identifier][page_info_type], space_id, table, mode)


def dump_application_inventory(mode):
    if mode:
        logger.info("dump_application_inventory: Creating CSV dump file.")
        dump = pd.DataFrame(DatabaseAPI.select('wiki_app_info_full'))
        dump.to_csv(os.path.dirname(os.path.realpath(__file__)) + "/application_inventory/dump/" +
                    datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + ".csv", index=None)


def run(conf, mode, conf_modified):
    for space, value in conf['wiki']['spaces'].items():
        space_id = ConfluenceAPI.get_homepage_id_of_space(space)
        DatabaseAPI.update_spaces(
            space_id, space, ConfluenceAPI.get_last_update_time_of_content(space_id))
        child_page_recursive(value['pages'], space_id, space_id,
                             conf['mysql']['table_prefix'], mode, conf_modified)
        recursive_db_cleanup(value['pages'], space_id,
                             conf['mysql']['table_prefix'], mode)
        # dump_application_inventory(mode)


if __name__ == '__main__':
    # Argument parsing.
    parser = argparse.ArgumentParser(description='Conflex')
    parser.add_argument('--application-inventory', action='store_true',
                        help='run the application inventory existing database update script.')
    # parser.add_argument('--bigquery', action='store_true', help='run the Google Big Query update application.')
    parser.add_argument('--config', action='store',
                        help='the location of the configuration file to run the application with.')
    # parser.add_argument('--datastore', action='store_true', help='run the Google DataStore update application.')
    parser.add_argument('--full-sync', action='store_true',
                        help='runs the application in full sync mode. i.e. pages are checked to ensure they meet the criteria in the config file.')
    parser.add_argument('--half-sync', action='store_true',
                        help='runs the application in half sync mode. i.e. no new pages will be added to the database.')
    parser.add_argument('--version', action='version',
                        version='Conflex Version: ' + VERSION)
    args = parser.parse_args()

    # Get configuration file.
    config = config_parser.parse(args.config or os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'config.yaml')))

    # Setup logging.
    logger = logging.getLogger(__name__)

    # Connect to database and setup tables.
    DatabaseAPI.connect(config)
    DatabaseAPI.create_spaces_table()
    DatabaseAPI.create_application_table()

    # Setup the confluence API.
    ConfluenceAPI.setup(config)

    # Store Last config modified time in database.
    config_data = DatabaseAPI.update_connex_application(
        'last_config_change', str(config['config_modified_time']))
    config_modified = False
    if config_data:
        if float(config_data['value']) != config['config_modified_time']:
            # The configuration has been modified since last time.
            logger.info('Configuration file has been updated!')
            config_modified = True

    # Run the application inventory application if requested.
    if args.application_inventory:
        application_inventory.__main__.run(config)

    # Run the datastore sync application.
    # if args.datastore:
    #     datastore.run(config)

    # Run the main application in the appropriate mode.
    if args.full_sync:
        logger.info('Application starting at: %s, running in full sync mode.' %
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        run(config, True, config_modified)

    if args.half_sync:
        logger.info('Application starting at: %s, running in half sync mode.' %
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        run(config, False, config_modified)

    # Disconnect from the database.
    DatabaseAPI.disconnect()

    logger.info('Application finished updating at: %s' %
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
