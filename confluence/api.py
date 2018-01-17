import json

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
        content = BeautifulSoup(content, 'html.parser')
        heading = content.find(string=heading).parent
        return heading

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
        # TODO: THIS SHOULD OUTPUT THE TEXT IN A SIMILAR FASHION TO extract_heading_information
        return {page: BeautifulSoup(content).getText()}

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
    def extract_panel_information(cls):
        """Summary line.

        Extended description of function.

        Args:
            arg1 (int): Description of arg1
            arg2 (str): Description of arg2

        Returns:
            bool: Description of return value

        """
        return cls

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

        # Strip '\n' and '\r' characters from the content string.
        info = {content_name: ConfluenceAPI.recursive_html_handler(content)}
        return info

    @classmethod
    def recursive_html_handler(cls, content):
        """Handles html information

        This method will handle the HTML input, returning it as a dictionary.

        Args:
            content (str): The content to turn into a usable dictionary.

        Returns:
            list: A list dictionary that contains the content only (no HTML).
        """
        # First search through the content to see if it contains a table or a list.
        content_list = []
        html = BeautifulSoup(content, 'html.parser')
        l = html.find('ul')
        t = html.find('table')
        if l and t:
            # Content contains a list and a table!
            content_list.append(html.getText())
        elif l and t is None:
            # Content only contains a list.
            for child in l.children:
                if child != '\n':
                    embed_l = child.find('ul')
                    if embed_l:
                        content_list.append(ConfluenceAPI.recursive_html_handler(str(embed_l)))
                        # Remove the list from the html as we have parsed that list now?
                    else:
                        content_list.append(child.getText().replace('\n', ''))
        elif l is None and t:
            # Content only contains a table.
            content_list.append(html.getText())
        else:
            # Content does not contain any lists or tables so just return the information.
            content_list.append(html.getText())

        return content_list
