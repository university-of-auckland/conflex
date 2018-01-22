from settings import *
from confluence.api import ConfluenceAPI

if __name__ == '__main__':
    logger = logging.getLogger(__name__)

    # Getting configuration
    for space, value in config['wiki']['spaces'].items():
        space_id = ConfluenceAPI.get_homepage_id_of_space(space)
        print(value)

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
