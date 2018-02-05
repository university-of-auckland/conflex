import json
import re

import unicodedata

import backoff
import dateutil.parser

# noinspection PyProtectedMember
from bs4 import BeautifulSoup, NavigableString

from settings import *
from urllib import request, parse, error

logger = logging.getLogger(__name__)


class ConfluenceAPI(object):
    """Confluence API Class

    This class acts as an API bridge between python and the confluence API.
    """

    # Private attributes of the API class.
    host = config['confluence']['host']
    __username = config['confluence']['username']
    __password = config['confluence']['password']

    empty_contents = ['', ',', '.', ' ']

    @classmethod
    @backoff.on_exception(backoff.expo, (error.URLError, error.ContentTooShortError, error.HTTPError, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError), max_tries=8)
    def __make_rest_request(cls, api_endpoint, content_id, url_params):
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
    @backoff.on_exception(backoff.expo, (error.URLError, error.ContentTooShortError, error.HTTPError, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError), max_tries=8)
    def __make_master_detail_request(cls, url_params):
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
    def get_homepage_id_of_space(cls, space):
        """Summary line.

        Extended description of function.

        Args:
            arg1 (int): Description of arg1
            arg2 (str): Description of arg2

        Returns:
            bool: Description of return value

        """
        response = ConfluenceAPI.__make_rest_request('space', space, {})
        logger.debug('get_homepage_id_of_space: %s has id of %d' %
                     (space, int(response['_expandable']['homepage'].replace('/rest/api/content/', ''))))
        return int(response['_expandable']['homepage'].replace('/rest/api/content/', ''))

    @classmethod
    def get_last_update_time_of_content(cls, content_id):
        """Summary line.

        Extended description of function.

        Args:
            arg1 (int): Description of arg1

        Returns:
            datetime.datetime: Description of return value

        """
        response = ConfluenceAPI.__make_rest_request('content', str(content_id), {'expand': 'version'})
        return dateutil.parser.parse(response['version']['when'])

    @classmethod
    def get_page_labels(cls, content_id):
        labels = []
        for label in ConfluenceAPI.__make_rest_request('content', str(content_id) + '/label', {})['results']:
            labels.append(label['name'])
        return labels

    @classmethod
    def get_page_content(cls, content_id):
        return ConfluenceAPI.__make_rest_request('content', str(content_id), {'expand': 'body.view'})['body']['view']['value']

    @classmethod
    def get_panel(cls, content, panel):
        return ConfluenceAPI.__extract_panel_information(content, panel)

    @classmethod
    def get_heading(cls, content, heading):
        return ConfluenceAPI.__extract_heading_information(content, heading)

    @classmethod
    def get_page(cls, content, page_title):
        return  ConfluenceAPI.__extract_page_information(content, page_title)

    @classmethod
    def get_page_properties(cls, content_id, space_key, labels):
        cql = 'label in ('
        for label in labels[:-1]:
            cql += "'" + label + "',"
        cql += "'" + labels[-1] + "') "
        cql += 'AND id = ' + str(content_id)
        return ConfluenceAPI.__extract_page_properties(ConfluenceAPI.__make_master_detail_request({'cql': cql, 'spaceKey': space_key}))

    @classmethod
    def get_page_urls(cls, content_id, url_type):
        result = ConfluenceAPI.__make_rest_request('content', str(content_id), {})['_links']
        return result['base'] + result[url_type]

    @classmethod
    def __extract_heading_information(cls, content, heading):
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
        heading_container = ''
        try:
            heading_container = str(html.find(string=heading).parent.next_sibling)
        except:
            logger.warning('__extract_heading_information: The following heading does not exists for the content provided: %s' % heading)
        return ConfluenceAPI.__handle_html_information(heading_container, heading)

    @classmethod
    def __extract_page_information(cls, content, page):
        """Extracts all information from a page.

        This method extracts all the text information from a page.

        Args:
            content (str): The content to extract the text from.
            page (str): The title of the page that the information was taken from.
        Returns:
            dict: The extracted text.

        """
        return ConfluenceAPI.__handle_html_information(content, page)

    @classmethod
    def __extract_page_properties_from_page(cls, content, label):
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
        return content

    @classmethod
    def __extract_page_properties(cls, content):
        """Extracts the page properties macro.

        This method will extract the page properties macro. This method assumes that the content is in the format
        returned by the make_master_details_request method.

        Args:
            content (dict): The content to abstract the k-v pairs from.

        Returns:
            dict: The page properties as key value pairs.

        """
        if len(content['detailLines']) > 0:
            keys = []
            for k in content['renderedHeadings']:
                keys.append(BeautifulSoup(k, 'html.parser').getText().strip())

            values = []
            for v in content['detailLines'][0]['details']:
                values.append(ConfluenceAPI.__recursive_html_handler(v))
            page_properties = dict(zip(keys, values))
            page_properties.pop('', None)

            # Remove empty key value pairs from dictionary.
            keys = []
            values = []
            for k, v in page_properties.items():
                vals = []
                for val in v:
                    if type(val) is str:
                        if val.replace(' ', '') not in ConfluenceAPI.empty_contents:
                            vals.append(val)
                    else:
                        vals.append(val)
                if len(vals) > 0:
                    values.append(vals)
                    keys.append(k)
            page_properties = dict(zip(keys, values))
            return page_properties
        else:
            return {}

    @classmethod
    def __extract_panel_information(cls, content, panel):
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
        panel_container = ''
        try:
            panel_container = str(html.find('b', string=panel).parent.next_sibling)
        except:
            logger.warning('__extract_panel_information: The following panel does not exists for the content provided: %s' % panel)
        return ConfluenceAPI.__handle_html_information(panel_container, panel)

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
        children_id = {}
        while size == 25:
            response = ConfluenceAPI.__make_rest_request('content', str(parent_id) + '/child/page',
                                                         {'start': page, 'limit': 25, 'size': size,
                                                          'expand': 'version'})
            results = response['results']
            size = response['size']
            page += response['size']
            for result in results:
                children_id[int(result['id'])] = {'name': result['title'], 'last_updated':dateutil.parser.parse(result['version']['when'])}
        return children_id

    @classmethod
    def __handle_html_information(cls, content, content_name):
        """Handles html information

        This method will handle the HTML input, returning it as a dictionary.

        Args:
            content (str): The content to turn into a usable dictionary.
            content_name (str): The name/heading/label associated with the content.

        Returns:
            dict: A usable dictionary that contains the content only (no HTML).
        """
        return {content_name: ConfluenceAPI.__recursive_html_handler(content)}

    @classmethod
    def __recursive_html_handler(cls, content):
        """Handles html information

        This method will handle the HTML input, returning it as a dictionary.

        Args:
            content (str): The content to turn into a usable dictionary.

        Returns:
            list: A list dictionary that contains the content only (no HTML).
        """
        # Remove all newline characters and remove all spaces between two tags.
        content = re.sub('>+\s+<', '><', content.replace('\n', ''))
        heading = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7']
        supported_tags = ['p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'a', 'ul', 'table']
        content_list = []
        html = BeautifulSoup(content, 'html.parser')

        # Go down the hierarchy until we are at a non-div element.
        contents = html
        if contents.contents:
            while contents.contents[0].name == 'div':
                contents = contents.contents[0]

        # Look at each of the provided html's children tags and handle data for different cases.
        for tag in contents.children:
            # Check if previous sibling was a heading.
            if tag.previous_sibling:
                if tag.previous_sibling.name in heading:
                    continue

            # Making sure we are at the lowest element in the current tag.
            while tag.name == 'div':
                tag = tag.contents[0]

            if tag.name == 'ul':
                # List handling
                for child in tag.children:
                    child_to_insert = child.getText().strip()
                    if child.find('table', recursive=False):
                        child_to_insert = ConfluenceAPI.__recursive_html_handler(
                            str(child.find('table', recursive=False)))
                    if child.find('ul', recursive=False):
                        child_to_insert = ConfluenceAPI.__recursive_html_handler(str(child.find('ul', recursive=False)))
                    if child_to_insert not in ConfluenceAPI.empty_contents:
                        content_list.append(child_to_insert)

            elif tag.name == 'table':
                # Table handling.
                table = tag.find('tbody')
                horizontal_headings = []
                vertical_heading = None
                table_dict = {}
                for row in table.children:
                    # noinspection PyBroadException
                    try:
                        current_column = 0
                        headings_only_row = not row.find('td')
                        for data in row.children:
                            if headings_only_row:
                                horizontal_headings.append(data.getText().strip())
                            else:
                                # Data could be a heading or actual data depending on layout of
                                # table.
                                if data.name == 'th':
                                    vertical_heading = data.getText().strip()
                                else:
                                    data_to_insert = data.getText().strip()
                                    if data.find('table', recursive=False):
                                        data_to_insert = ConfluenceAPI.__recursive_html_handler(str(data.find('table', recursive=False)))
                                    if data.find('ul', recursive=False):
                                        data_to_insert = ConfluenceAPI.__recursive_html_handler(str(data.find('ul', recursive=False)))

                                    if data_to_insert not in ConfluenceAPI.empty_contents:
                                        if len(horizontal_headings) == 0 and vertical_heading is None:
                                            # Dealing with a completely flat table.
                                            content_list.append(data_to_insert)
                                        elif len(horizontal_headings) == 0:
                                            if vertical_heading in table_dict:
                                                table_dict[vertical_heading].append(data_to_insert)
                                            else:
                                                table_dict[vertical_heading] = [data_to_insert]
                                        elif vertical_heading is None:
                                            if horizontal_headings[current_column] in table_dict:
                                                table_dict[horizontal_headings[current_column]].append(data_to_insert)
                                            else:
                                                table_dict[horizontal_headings[current_column]] = [data_to_insert]
                                        else:
                                            if horizontal_headings[current_column] in table_dict:
                                                if vertical_heading in table_dict[horizontal_headings[current_column]]:
                                                    table_dict[horizontal_headings[current_column]][vertical_heading].append(data_to_insert)
                                                else:
                                                    table_dict[horizontal_headings[current_column]][vertical_heading] = [data_to_insert]
                                            else:
                                                table_dict[horizontal_headings[current_column]] = {vertical_heading: [data_to_insert]}
                            current_column += 1
                    except:
                        logger.error('recursive_html_handler: Unable to parse table: %s', tag.getText().strip())
                if table_dict != {}:
                    content_list.append(table_dict)
            elif tag.name in heading:
                heading_to_insert = tag.getText().strip()
                heading_content = ConfluenceAPI.__recursive_html_handler(str(tag.next_sibling))
                content_list.append({heading_to_insert: heading_content})
            elif tag.name in supported_tags:
                information_to_insert = tag.getText().strip()
                if tag.find('table', recursive=False):
                    information_to_insert = ConfluenceAPI.__recursive_html_handler(str(tag.find('table', recursive=False)))
                if tag.find('ul', recursive=False):
                    information_to_insert = ConfluenceAPI.__recursive_html_handler(str(tag.find('ul', recursive=False)))
                # Content does not contain any lists, tables or links to a user so just return the information.
                if tag.find('a', class_='user-mention') or 'data-username' in tag.attrs:
                    if tag.find('a', class_='user-mention'):
                        for user in tag.find_all('a', class_='user-mention'):
                            content_list.append(user.attrs['data-username'])
                    else:
                        content_list.append(tag.attrs['data-username'])
                else:
                    if information_to_insert not in ConfluenceAPI.empty_contents:
                        content_list.append(information_to_insert)

            elif type(tag) is NavigableString:
                content_list.append(str(tag.string).strip())

        return content_list
