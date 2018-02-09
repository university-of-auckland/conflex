import argparse
import datetime
import re

from database.api import DatabaseAPI
from settings import *
from confluence.api import ConfluenceAPI


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
            table = table_prefix.replace(' ', '') + '_' + page_identifier.replace('_', '').replace(' ', '')[:5].lower()
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
                    page_updated = DatabaseAPI.insert_or_update(table, parent_page_id, child_page_id, child_pages[child_page_id]['name'], child_pages[child_page_id]['last_updated'], True)

                    # If the current page information was updated since the last run, delete all children information and re-fill it.
                    page_content = ''
                    if page_updated or config_modified:
                        logger.info('Updating information in space %s for page: %s' % (str(space_id), child_pages[child_page_id]['name']))
                        DatabaseAPI.delete(info_table, child_page_id)
                        page_content = ConfluenceAPI.get_page_content(child_page_id)

                    for page_info_type in pages[page_type][page_identifier]:
                        if page_info_type == 'pages':
                            child_page_recursive(pages[page_type][page_identifier][page_info_type], space_id, child_page_id, table, recheck_pages_meet_criteria, config_modified)
                        else:
                            if page_updated or config_modified:
                                try:
                                    if page_info_type == 'panels':
                                        for panel_identifier in pages[page_type][page_identifier][page_info_type]:
                                            panel = FlatDict(ConfluenceAPI.get_panel(page_content, panel_identifier, space_id))
                                            for k, v in panel.items():
                                                # For each key remove list numbers. i.e. FlatDict will put in :0, :1: for each list element.
                                                k = re.sub(':(\d+)', '', k)
                                                k = re.sub(':(\d+):', ':', k)
                                                DatabaseAPI.insert_or_update(info_table, child_page_id, k, v, child_pages[child_page_id]['last_updated'])
                                    elif page_info_type == 'page_properties':
                                        # Get all page properties and put the values into the database.
                                        page_properties = ConfluenceAPI.get_page_properties(child_page_id, space_id, pages[page_type][page_identifier][page_info_type])
                                        for page_property in page_properties:
                                            for val in page_properties[page_property]:
                                                DatabaseAPI.insert_or_update(info_table, child_page_id, page_property, val, child_pages[child_page_id]['last_updated'])
                                    elif page_info_type == 'headings':
                                        for heading_identifier in pages[page_type][page_identifier][page_info_type]:
                                            heading = FlatDict(ConfluenceAPI.get_heading(page_content, heading_identifier))
                                            for k, v in heading.items():
                                                # For each key remove list numbers. i.e. FlatDict will put in :0, :1: for each list element.
                                                k = re.sub(':(\d+)', '', k)
                                                k = re.sub(':(\d+):', ':', k)
                                                DatabaseAPI.insert_or_update(info_table, child_page_id, k, v, child_pages[child_page_id]['last_updated'])
                                    elif page_info_type == 'page':
                                        page_information = FlatDict(ConfluenceAPI.get_page(page_content, child_pages[child_page_id]['name']))
                                        for k, v in page_information.items():
                                            # For each key remove list numbers. i.e. FlatDict will put in :0, :1: for each list element.
                                            k = re.sub(':(\d+)', '', k)
                                            k = re.sub(':(\d+):', ':', k)
                                            DatabaseAPI.insert_or_update(info_table, child_page_id, k, v, child_pages[child_page_id]['last_updated'])
                                    elif page_info_type == 'url':
                                        for url_type in pages[page_type][page_identifier][page_info_type]:
                                            url = ConfluenceAPI.get_page_urls(child_page_id, url_type)
                                            DatabaseAPI.insert_or_update(info_table, child_page_id, url_type, url, child_pages[child_page_id]['last_updated'])
                                    else:
                                        logger.warning('child_page_recursive: Unknown page information retrieval type: %s' % page_info_type)
                                except:
                                    logger.error('child_page_recursive: Error inserting data for page with id: %s, name: %s' % (str(child_page_id), child_pages[child_page_id]['name']))
                else:
                    # Cleanup the ignore, info and default table by removing any information associated with page.
                    DatabaseAPI.delete(table, parent_page_id, child_page_id)
                    DatabaseAPI.delete(info_table, child_page_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capsule Wiki Integration Application.')
    parser.add_argument('--recheck-pages-meet-criteria', action='store_true', help='force the database to recheck that all pages meet the criteria in the config file.')

    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    logger.info('Application starting at: %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    DatabaseAPI.connect()
    DatabaseAPI.create_spaces_table()
    DatabaseAPI.create_application_table()

    # Store Last config modified time in database.
    config_data = DatabaseAPI.update_capsule_application('last_config_change', str(config_modified_time))
    config_modified = False
    if config_data:
        if float(config_data['value']) != config_modified_time:
            # The configuration has been modified since last time.
            logger.info('Configuration file has been updated!')
            config_modified = True

    # Getting configuration
    for space, value in config['wiki']['spaces'].items():
        space_id = ConfluenceAPI.get_homepage_id_of_space(space)
        DatabaseAPI.update_spaces(space_id, space, ConfluenceAPI.get_last_update_time_of_content(space_id))
        child_page_recursive(value['pages'], space_id, space_id, config['mysql']['wiki_table_prefix'], args.recheck_pages_meet_criteria, config_modified)

    DatabaseAPI.disconnect()

    logger.info('Application finished updating at: %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # Reading the html
    # html_doc = open('html.html', 'r')
    # soup = BeautifulSoup(html_doc, 'html.parser')
    # print(soup.find('b', string='Overview').parent.parent.get_text().replace('Overview', ''))

    # Reading the xml
    # xml_doc = open('test.xml', 'r')
    # soup = BeautifulSoup(xml_doc, 'html.parser')
    # # print(soup)
    # print(soup.find('ac:structured-macro'))
    # message = ConfluenceAPI.make_request('content', '65013279', {'expand': 'page'})
