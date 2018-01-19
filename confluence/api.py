import json
import re

import unicodedata
from bs4 import BeautifulSoup

from settings import *
from urllib import request, parse

logger = logging.getLogger(__name__)


class ConfluenceAPI(object):
    """Confluence API Class

    This class acts as an API bridge between python and the confluence API.
    """

    # Private attributes of the API class.
    host = config['confluence']['host']
    __username = config['confluence']['username']
    __password = config['confluence']['password']

    @classmethod
    def make_rest_request(cls, api_endpoint, content_id, url_params):
        """Low level request abstraction method.

        This method will make a request to the Confluence API and return the response directly to the caller.

        Args:
            api_endpoint (str): The endpoint on the rest api to call.
            content_id (str): The id of the content to retrieve.
            url_params (dict): A dictionary of url params.

        Returns:
            dict: Returns the response from the server.

        """
        params = parse.urlencode({**url_params, 'os_username': cls.__username, 'os_password': cls.__password})
        url = cls.host + '/rest/api/' + api_endpoint + '/' + content_id + '?%s' % params
        logger.debug('make_rest_request: URL requested : %s' % url)
        return json.loads(unicodedata.normalize("NFKD", request.urlopen(url).read().decode('utf-8')))

    @classmethod
    def make_master_detail_request(cls, url_params):
        """Low level request abstraction method.

        This method will make a request to the Confluence API master details page and return the response directly to
        the caller.

        Args:
            url_params (dict): A dictionary of url params.

        Returns:
            dict: Returns the response from the server.

        """
        params = parse.urlencode({**url_params, 'os_username': cls.__username, 'os_password': cls.__password})
        url = cls.host + '/rest/masterdetail/1.0/detailssummary/lines' + '?%s' % params
        logger.debug('make_master_detail_request: URL requested: %s' % url)
        return json.loads(unicodedata.normalize("NFKD", request.urlopen(url).read().decode('utf-8')))

    @classmethod
    def extract_heading_information(cls, content, heading):
        """Extracts all information beneath a heading.

        This method extracts all information beneath a heading.

        Args:
            content (str): The content to extract the text from.
            heading (str): The heading to extract the information below.

        Returns:
            dict: The extracted text in the heading.

        """
        logger.debug('extract_heading_information: Heading to extract information from: %s' % heading)
        html = BeautifulSoup(content, 'html.parser')
        heading_container = str(html.find(string=heading).parent.next_sibling)
        return ConfluenceAPI.handle_html_information(heading_container, heading)

    @classmethod
    def extract_page_information(cls, content, page):
        """Extracts all information from a page.

        This method extracts all the text information from a page.

        Args:
            content (str): The content to extract the text from.
            page (str): The title of the page that the information was taken from.
        Returns:
            dict: The extracted text.

        """
        return ConfluenceAPI.handle_html_information(content, page)

    @classmethod
    def extract_page_properties_from_page(cls, content, label):
        """Extracts the page properties macro.

        This method will extract the page properties macro from the confluence 'body.storage' content. Unfortunately due
        to complexity, this method is yet to be written and should not be used.

        Args:
            content (str): The content to abstract the k-v pairs from.
            label (str): The label given to the page_properties.

        Returns:
            dict: The page properties as key value pairs.

        """

        # TODO: WRITE METHOD
        # content = BeautifulSoup(content, 'html.parser')
        # lab = content.find('ac:parameter', string=label).parent.find('table')
        #
        # results = {}
        # for row in lab.findAll('tr'):
        #     aux = row.findAll('td')
        #     results[aux[0].string] = aux[1].string
        # logger.debug(lab)
        return content

    @classmethod
    def extract_page_properties(cls, content):
        """Extracts the page properties macro.

        This method will extract the page properties macro. This method assumes that the content is in the format
        returned by the make_master_details_request method.

        Args:
            content (dict): The content to abstract the k-v pairs from.

        Returns:
            dict: The page properties as key value pairs.

        """
        keys = []
        for k in content['renderedHeadings']:
            keys.append(BeautifulSoup(k, 'html.parser').getText())

        values = []
        for v in content['detailLines'][0]['details']:
            values.append(BeautifulSoup(v, 'html.parser').getText())
        return dict(zip(keys, values))

    @classmethod
    def extract_panel_information(cls, content, panel):
        """Summary line.

        Extended description of function.

        Args:
            arg1 (int): Description of arg1
            arg2 (str): Description of arg2

        Returns:
            bool: Description of return value

        """
        logger.debug('extract_panel_information: Panel to extract information from: %s' % panel)
        html = BeautifulSoup(content, 'html.parser')
        panel_container = str(html.find('b', string=panel).parent.next_sibling)
        return ConfluenceAPI.handle_html_information(panel_container, panel)

    @classmethod
    def get_child_page_ids(cls, parent_id):
        """Summary line.

        Extended description of function.

        Args:
            parent_id (int): Id of the parent page to get the children of.
            # child_filter (str): cql filter to apply to retrieve only child pages that match the filter.

        Returns:
            list: A list of all the child ids of the parent page.
        """
        page = 0
        size = 25
        children_id = []
        while size == 25:
            response = ConfluenceAPI.make_rest_request('content', str(parent_id) + '/child/page',
                                                       {'start': page, 'limit': 25, 'size': size})
            results = response['results']
            size = response['size']
            page += response['size']
            for result in results:
                children_id.append(int(result['id']))
        return children_id

    @classmethod
    def handle_html_information(cls, content, content_name):
        """Handles html information

        This method will handle the HTML input, returning it as a dictionary.

        Args:
            content (str): The content to turn into a usable dictionary.
            content_name (str): The name/heading/label associated with the content.

        Returns:
            dict: A usable dictionary that contains the content only (no HTML).
        """
        # Remove all newline characters and remove all spaces between two tags.
        content = re.sub('>+\s+<', '><', content.replace('\n', ''))
        return {content_name: ConfluenceAPI.recursive_html_handler(content)}

    @classmethod
    def recursive_html_handler(cls, content):
        """Handles html information

        This method will handle the HTML input, returning it as a dictionary.

        Args:
            content (str): The content to turn into a usable dictionary.

        Returns:
            list: A list dictionary that contains the content only (no HTML).
        """
        supported_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'a', 'ul', 'table']
        content_list = []
        html = BeautifulSoup(content, 'html.parser')

        # Go down the hierarchy until we are at a non-div element.
        contents = html
        while contents.contents[0].name == 'div':
            contents = contents.contents[0]

        # Look at each of the provided html's children tags and handle data for different cases.
        for tag in contents.children:
            if tag.name == 'table':
                # Table handling.
                table = tag.find('tbody')
                horizontal_headings = []
                vertical_heading = None
                table_dict = {}
                for row in table.children:
                    try:
                        current_column = 0
                        headings_only_row = not row.find('td')
                        for data in row.children:
                            if headings_only_row:
                                horizontal_headings.append(data.getText())
                            else:
                                # Data could be a heading or actual data depending on layout of
                                # table.
                                if data.name == 'th':
                                    vertical_heading = data.getText()
                                else:
                                    if data.find('table', recursive=False):
                                        content_list.append(ConfluenceAPI.recursive_html_handler(
                                            str(data.find('table', recursive=False))))
                                    else:
                                        if len(horizontal_headings) == 0:
                                            if vertical_heading in table_dict:
                                                table_dict[vertical_heading].append(data.getText())
                                            else:
                                                table_dict[vertical_heading] = [data.getText()]
                                        elif vertical_heading is None:
                                            if horizontal_headings[current_column] in table_dict:
                                                table_dict[horizontal_headings[current_column]].append(data.getText())
                                            else:
                                                table_dict[horizontal_headings[current_column]] = [data.getText()]
                                        else:
                                            if horizontal_headings[current_column] in table_dict:
                                                table_dict[horizontal_headings[current_column]][
                                                    vertical_heading].append(data.getText())
                                            else:
                                                table_dict[horizontal_headings[current_column]] = {
                                                    vertical_heading: [data.getText()]}
                            current_column += 1
                    except:
                        logger.error('recursive_html_handler: Unable to parse table: %s',
                                     tag.getText())
                content_list.append(table_dict)
            elif tag.name == 'ul':
                # List handling
                for child in tag.children:
                    if child.find('table', recursive=False):
                        content_list.append(ConfluenceAPI.recursive_html_handler(str(child.find('table', recursive=False))))
                    elif child.find('ul', recursive=False):
                        content_list.append(ConfluenceAPI.recursive_html_handler(str(child.find('ul', recursive=False))))
                    else:
                        content_list.append(child.getText())
            elif tag.name in supported_tags:
                # Content does not contain any lists or tables so just return the information.
                content_list.append(tag.getText())

        return content_list
