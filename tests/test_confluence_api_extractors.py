import unittest

from confluence.api import ConfluenceAPI


# noinspection PyUnresolvedReferences
class TestConfluenceAPIExtractor(unittest.TestCase):
    def setUp(self):
        self.confluence = ConfluenceAPI

    def test_heading_extraction(self):
        page = self.confluence._ConfluenceAPI__make_rest_request('content', '112771136', {'expand': 'body.view'})['body']['view']['value']
        content = ConfluenceAPI.extract_heading_information(page, 'Key Locations')

        self.assertEqual(content, {'Key Locations': [{'Configuring Shibboleth SPs': [['SSO Enablement Procedures',
                                                                                      'Apache integration with '
                                                                                      'Shibboleth for Single '
                                                                                      'Sign On',
                                                                                      'Windows Based Migration '
                                                                                      'Procedures',
                                                                                      'Shibboleth SP Installer '
                                                                                      'for IIS',
                                                                                      'Windows Server with '
                                                                                      'Virtual Hosts to EPR '
                                                                                      'Shibboleth']],
                                                      'Knowledge': [
                                                          'https://wiki.shibboleth.net/confluence/display/IDP30'],
                                                      'Product homepage': ['https://shibboleth.net/'],
                                                      'Product management': [
                                                          'https://jira.auckland.ac.nz/browse/IDENTITYShibboleth '
                                                          'IDP3 Upgrade Development '
                                                          'Notes(Applications Engineering) '
                                                          'Attribute list - Attribute '
                                                          'Resolver Migration'],
                                                      'Reference Architecture': ['Element_Shibboleth'],
                                                      'Source repository': [
                                                          'https://stash.auckland.ac.nz/projects/ITSSHI'],
                                                      'Support Site': ['http://shibboleth.net/community/'],
                                                      'Test plan': ['Shibboleth Upgrade - EPR v4.26.x (Release '
                                                                    'Date dd/mm/2016)']}]})

    def test_panel_extraction(self):
        page = self.confluence._ConfluenceAPI__make_rest_request('content', '112771136', {'expand': 'body.view'})['body']['view']['value']
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
