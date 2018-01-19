import unittest

from confluence.api import ConfluenceAPI


class TestConfluenceAPIExtractor(unittest.TestCase):

    def test_heading_extraction(self):
        page = ConfluenceAPI.make_rest_request('content', '112771136', {'expand': 'body.view'})['body']['view']['value']
        content = ConfluenceAPI.extract_heading_information(page, 'Key Locations')

        self.assertEqual(content, {'basic_list': ['One', 'Two', 'Three']})

    def test_panel_extraction(self):
        page = ConfluenceAPI.make_rest_request('content', '112771136', {'expand': 'body.view'})['body']['view']['value']
        content = ConfluenceAPI.extract_panel_information(page, 'Info')

        self.assertEqual(content, {'Info': [{'CAUDIT Capability L0': ['Information Management'],
                                             'CAUDIT Capability L1': ['Identity & Access Management'],
                                             'Common Names': ['Single Sign On, Web SSO, SSO, OneLogin, '
                                                              'Shibboleth, Shibboleth IdP3.'],
                                             'External Users Allowed': ['Yes'],
                                             'Implementation Year': ['2010'],
                                             'Last Upgrade Year': ['2016'],
                                             'Life Cycle Phase': ['MATURITY'],
                                             'Platform': ['Java'],
                                             'Software Licensing Model': ['Open Source'],
                                             'Type': ['Application'],
                                             'Vendor': ['Internet2'],
                                             'Version': ['Shibboleth 3']}]})


if __name__ == '__main__':
    unittest.main()
