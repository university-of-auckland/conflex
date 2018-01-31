from database.api import DatabaseAPI
from settings import *
from confluence.api import ConfluenceAPI


def child_page_recursive(pages, parent_page_id):
    """Summary line.

    Extended description of function.

    Args:
        arg1 (int): Description of arg1
        arg2 (str): Description of arg2

    Returns:
        bool: Description of return value

    """
    # child_page_ids = ConfluenceAPI.get_child_page_ids(space_id)
    # if the child page has not been updated since we last stored the information, then no need to check labels/title!
    for page_type in pages:
        for page_identifier in pages[page_type]:
            for page_info_type in pages[page_type][page_identifier]:
                print(page_info_type + ':')
                if 'pages' in page_info_type:
                    child_page_recursive(pages[page_type][page_identifier][page_info_type], parent_page_id)
                elif 'database_overwrite' in page_info_type:
                    logger.error('Currently Database overwrite is not supported')
                else:
                    # It must be a page_properties, panel, heading or other.
                    for info_identifier in pages[page_type][page_identifier][page_info_type]:
                        print(info_identifier)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)

    DatabaseAPI.connect()
    DatabaseAPI.create_spaces_table()

    # Getting configuration
    for space, value in config['wiki']['spaces'].items():
        space_id = ConfluenceAPI.get_homepage_id_of_space(space)
        DatabaseAPI.update_spaces(space_id, space, ConfluenceAPI.get_last_update_time_of_content(space_id))
        child_page_recursive(value['pages'], space_id)

    DatabaseAPI.disconnect()

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
