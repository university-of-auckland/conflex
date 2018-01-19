import unittest

from confluence.api import ConfluenceAPI


class TestConfluenceAPIWebPageCrawlingLists(unittest.TestCase):

    def test_basic_list(self):
        html_doc = open('tests/data/lists/basic.html', 'r')
        lst = ConfluenceAPI.handle_html_information(html_doc.read(), 'basic_list')
        html_doc.close()

        self.assertEqual(lst, {'basic_list': ['One', 'Two', 'Three']})

    def test_embedded_list(self):
        html_doc = open('tests/data/lists/embedded.html', 'r')
        lst = ConfluenceAPI.handle_html_information(html_doc.read(), 'embedded_list')
        html_doc.close()

        self.assertEqual(lst, {'embedded_list': ['One', ['Inside One', 'Inside Two']]})

    def test_multiple_list(self):
        html_doc = open('tests/data/lists/multiple.html', 'r')
        lst = ConfluenceAPI.handle_html_information(html_doc.read(), 'multiple_list')
        html_doc.close()

        self.assertEqual(lst, {'multiple_list':
                                   ['List One',
                                    ['Inside One', 'Another Inside One'],
                                    'List Two',
                                    ['Inside Two', 'Another Inside Two']]})

    def test_wiki_example_list(self):
        html_doc = open('tests/data/lists/wiki_example.html', 'r')
        lst = ConfluenceAPI.handle_html_information(html_doc.read(), 'wiki_example_list')
        html_doc.close()

        self.assertEqual(lst, {'wiki_example_list': [
            'Level 2 - username and password. Provides the minimum level of authentication requiring username and '
            'password to access a resource.',
            'Level 3 - two-step verification. Provides additional security by requiring a user to login by entering a '
            'one-time token in addition to username and password. Users are required to register for two factor '
            'authentication through the mytoken service.',
            'Note: Level 0 and Level 1 are deprecated levels of authentication.']})


class TestConfluenceAPIWebPageCrawlingTables(unittest.TestCase):
    def test_basic_table_data_only(self):
        html_doc = open('tests/data/tables/data_only.html', 'r')
        lst = ConfluenceAPI.handle_html_information(html_doc.read(), 'data_only')
        html_doc.close()

        self.assertEqual(lst, {'data_only': [{None: ['Jill', 'Smith', 'Eve', 'Jackson']}]})

    def test_basic_table_horizontal_headings(self):
        html_doc = open('tests/data/tables/horizontal_headings.html', 'r')
        lst = ConfluenceAPI.handle_html_information(html_doc.read(), 'horizontal_headings')
        html_doc.close()

        self.assertEqual(lst, {'horizontal_headings': [{'Firstname': ['Jill', 'Eve'],
                                                        'Lastname': ['Smith', 'Jackson'],
                                                        'Age': ['50', '94']}]})

    def test_basic_table_vertical_headings(self):
        html_doc = open('tests/data/tables/vertical_headings.html', 'r')
        lst = ConfluenceAPI.handle_html_information(html_doc.read(), 'vertical_headings')
        html_doc.close()

        self.assertEqual(lst, {'vertical_headings': [{'Firstname': ['John', 'Micheal'],
                                                      'Lastname': ['Smith', 'Jackson'],
                                                      'Age': ['23', '94']}]})

    def test_wiki_example_table(self):
        html_doc = open('tests/data/tables/wiki_example_table.html', 'r')
        lst = ConfluenceAPI.handle_html_information(html_doc.read(), 'wiki_example')
        html_doc.close()

        self.assertEqual(lst, {'wiki_example': [{'': ['End user', 'Administrator'],
                                                 'Development': ['https://idp3.dev.auckland.ac.nz', 'NA'],
                                                 'Production': ['https://idp3.auckland.ac.nz', 'NA'],
                                                 'Test': ['https://idp3.test.auckland.ac.nz', 'NA']}]})


if __name__ == '__main__':
    unittest.main()
