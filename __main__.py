from settings import *
from confluence.api import ConfluenceAPI

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    # Confluence Server Address takes precedence over URL if present.
    # api = ConfluenceAPI(confluence_api_url, confluence_api_user, confluence_api_pass)

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

    # Tests for detail requests.
    details = ConfluenceAPI.make_master_detail_request({'cql': 'label = inv_item_info AND id = 112771136',
                                                        'spaceKey': 'APPLCTN'})
    props = ConfluenceAPI.extract_page_properties(details)
    # print(props)

    # Tests for heading.
    info = ConfluenceAPI.make_rest_request('content', '130561436', {'expand': 'body.view'})['body']['view']['value']
    content = ConfluenceAPI.extract_heading_information(info, 'Design Considerations')
    print(content)

    # Tests for panel?
    message = ConfluenceAPI.make_rest_request('content', '112771136', {'expand': 'body.view'})['body']['view']['value']
    content = ConfluenceAPI.extract_heading_information(message, 'Overview')
    # print(message)
    # print(message.find('ac:parameter', string='inv_item_info'))
    # ConfluenceAPI.extract_page_properties(message, 'inv_item_info')
    # message = ConfluenceAPI.make_request('search', '', {'cql': 'label=application'})
