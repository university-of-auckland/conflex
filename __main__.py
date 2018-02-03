import argparse
import datetime

from database.api import DatabaseAPI
from settings import *
from confluence.api import ConfluenceAPI


# noinspection PyTypeChecker
def child_page_recursive(pages, space_id, parent_page_id, table_prefix, recheck_pages_meet_criteria=False):
    """Summary line.

    Extended description of function.

    Args:
        arg1 (int): Description of arg1
        arg2 (str): Description of arg2

    Returns:
        bool: Description of return value

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
            ignore_table = table + '__ignore'
            DatabaseAPI.create_table(ignore_table)

            child_pages = ConfluenceAPI.get_child_page_ids(parent_page_id)
            for child_page_id in child_pages:

                # Decision tree to see if the current page meets the criteria provided in the config file.
                # if we are not forced to recheck the page meets the criteria then use the pages in the database table.
                # else, check to see if the page meets either criteria.
                page_meets_criteria = False
                if not recheck_pages_meet_criteria:
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
                    if page_updated:
                        logger.info('Updating information in space %s for page: %s' % (str(space_id), child_pages[child_page_id]['name']))
                        DatabaseAPI.delete(info_table, child_page_id)
                        page_content = ConfluenceAPI.get_page_content(child_page_id)

                    for page_info_type in pages[page_type][page_identifier]:
                        if page_info_type == 'pages':
                            child_page_recursive(pages[page_type][page_identifier][page_info_type], space_id, child_page_id, table, recheck_pages_meet_criteria)
                        else:
                            if page_updated:
                                if page_info_type == 'panels':
                                    for panel_identifier in pages[page_type][page_identifier][page_info_type]:
                                        panel = FlatDict(ConfluenceAPI.get_panel(page_content, panel_identifier))
                                        for val in panel[panel_identifier]:
                                            DatabaseAPI.insert_or_update(info_table, child_page_id, panel_identifier, val, child_pages[child_page_id]['last_updated'])
                                elif page_info_type == 'page_properties':
                                    # Get all page properties and put the values into the database.
                                    page_properties = ConfluenceAPI.get_page_properties(child_page_id, space_id, pages[page_type][page_identifier][page_info_type])
                                    for page_property in page_properties:
                                        for val in page_properties[page_property]:
                                            DatabaseAPI.insert_or_update(info_table, child_page_id, page_property, val, child_pages[child_page_id]['last_updated'])
                                elif page_info_type == 'headings':
                                    for heading_identifier in pages[page_type][page_identifier][page_info_type]:
                                        heading = ConfluenceAPI.get_heading(page_content, heading_identifier)
                                        for val in heading:
                                            DatabaseAPI.insert_or_update(info_table, child_page_id, heading_identifier, heading[val], child_pages[child_page_id]['last_updated'])
                                elif page_info_type == 'page':
                                    page_information = ConfluenceAPI.get_page(page_content, child_pages[child_page_id]['name'])
                                    for val in page_information:
                                        DatabaseAPI.insert_or_update(info_table, child_page_id, child_pages[child_page_id]['name'], val, child_pages[child_page_id]['last_updated'])
                                elif page_info_type == 'url':
                                    for url_type in pages[page_type][page_identifier][page_info_type]:
                                        url = ConfluenceAPI.get_page_urls(child_page_id, url_type)
                                        DatabaseAPI.insert_or_update(info_table, child_page_id, url_type, url, child_pages[child_page_id]['last_updated'])
                                else:
                                    logger.warning('child_page_recursive: Unknown page information retrieval type: %s' % page_info_type)
                else:
                    # Cleanup the ignore, info and default table by removing any information associated with page.
                    DatabaseAPI.delete(table, parent_page_id, child_page_id)
                    DatabaseAPI.delete(info_table, child_page_id)
                    DatabaseAPI.delete(ignore_table, parent_page_id, child_page_id)

                    # Insert the page into the ignore table to make consecutive runs faster.
                    DatabaseAPI.insert_or_update(ignore_table, parent_page_id, child_page_id, child_pages[child_page_id]['name'], child_pages[child_page_id]['last_updated'], True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capsule Wiki Integration Application.')
    parser.add_argument('--recheck-pages-meet-criteria', action='store_true', help='force the database to recheck that all pages meet the criteria in the config file.')

    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    logger.debug('Application starting at: %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    DatabaseAPI.connect()
    DatabaseAPI.create_spaces_table()

    # Getting configuration
    for space, value in config['wiki']['spaces'].items():
        space_id = ConfluenceAPI.get_homepage_id_of_space(space)
        DatabaseAPI.update_spaces(space_id, space, ConfluenceAPI.get_last_update_time_of_content(space_id))
        child_page_recursive(value['pages'], space_id, space_id, config['mysql']['wiki_table_prefix'], args.recheck_pages_meet_criteria)

    DatabaseAPI.disconnect()

    logger.debug('Application finished updating at: %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

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
