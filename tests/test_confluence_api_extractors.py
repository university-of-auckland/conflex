import unittest
import config_parser
import os

from confluence.api import ConfluenceAPI


# noinspection PyUnresolvedReferences
class TestConfluenceAPIExtractor(unittest.TestCase):
    def setUp(self):
        config = config_parser.parse(os.path.abspath(os.path.join(os.path.dirname(__file__), '../config.yaml')))
        self.confluence = ConfluenceAPI
        self.confluence.setup(config)

    def test_heading_extraction(self):
        page = \
            self.confluence._ConfluenceAPI__make_rest_request('content', '112771136', {'expand': 'body.view'})['body'][
                'view']['value']
        content = self.confluence._ConfluenceAPI__extract_heading_information(page, 'Key Locations')

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
        page = \
            self.confluence._ConfluenceAPI__make_rest_request('content', '112771136', {'expand': 'body.view'})['body'][
                'view']['value']
        content = self.confluence._ConfluenceAPI__extract_panel_information(page, 'Info')

        self.assertEqual(content, {'Info': [{'CAUDIT Capability L0': ['Information Management'],
                                             'CAUDIT Capability L1': ['Identity & Access Management'],
                                             'Common Names': ['Single Sign On, Web SSO, SSO, OneLogin, '
                                                              'Shibboleth, Shibboleth IdP3.'],
                                             'External Users Allowed': ['Yes'],
                                             'Implementation Year': ['2010'],
                                             'Last Upgrade Year': ['2018'],
                                             'Life Cycle Phase': ['MATURITY'],
                                             'Platform': ['Java'],
                                             'Software Licensing Model': ['Open Source'],
                                             'Type': ['Application'],
                                             'Vendor': ['Internet2'],
                                             'Version': ['Shibboleth 3']}]})

    def test_page_properties_extraction(self):
        page = self.confluence._ConfluenceAPI__make_master_detail_request({'cql': 'label = inv_item_info AND id = '
                                                                                  '112771136', 'spaceKey': '65013279'})
        content = self.confluence._ConfluenceAPI__extract_page_properties(page)

        self.assertEqual(content, {'Business Owner': ['jpye004'],
                                   'CAUDIT Capability L0': ['Information Management'],
                                   'CAUDIT Capability L1': ['Identity & Access Management'],
                                   'Common Names': ['Single Sign On, Web SSO, SSO, OneLogin, Shibboleth, '
                                                    'Shibboleth IdP3.'],
                                   'Configuring Shibboleth SPs': ['SSO Enablement Procedures',
                                                                  'Apache integration with Shibboleth for Single '
                                                                  'Sign On',
                                                                  'Windows Based Migration Procedures',
                                                                  'Shibboleth SP Installer for IIS',
                                                                  'Windows Server with Virtual Hosts to EPR '
                                                                  'Shibboleth'],
                                   'Data Sensitivity': ['High'],
                                   'Delivery Team': ['Identity Management'],
                                   'External Users Allowed': ['Yes'],
                                   'Hosting Tier': ['Platinum'],
                                   'Hours of Support': ['24x7'],
                                   'Hours of Use': ['24x7'],
                                   'Implementation Year': ['2010'],
                                   'Knowledge': ['https://wiki.shibboleth.net/confluence/display/IDP30'],
                                   'Last Upgrade Year': ['2018'],
                                   'Life Cycle Phase': ['MATURITY'],
                                   'Maintenance Windows': ['6 am Friday mornings (if required)'],
                                   'Organisation Owner': ['Digital Strategy & Architecture'],
                                   'Patching Cycle': ['Auto-patched'],
                                   'Platform': ['Java'],
                                   'Product homepage': ['https://shibboleth.net/'],
                                   'Product management': ['https://jira.auckland.ac.nz/browse/IDENTITY',
                                                          'Shibboleth IDP3 Upgrade Development Notes',
                                                          '(Applications Engineering) Attribute list - Attribute '
                                                          'Resolver Migration'],
                                   'RPO Current': ['Zero'],
                                   'RPO Required': ['zero'],
                                   'RTO Current': ['1 minute'],
                                   'RTO Required': ['15 minutes'],
                                   'Reference Architecture': ['Element_Shibboleth'],
                                   'Service Criticality': ['Yes'],
                                   'Service Manager': ['awal091'],
                                   'Service Owner': ['tals001'],
                                   'Software Licensing Model': ['Open Source'],
                                   'Source repository': ['https://stash.auckland.ac.nz/projects/ITSSHI'],
                                   'Subject Matter Experts': ['rwat090', 'wwan174', 'tell022'],
                                   'Support Site': ['http://shibboleth.net/community/'],
                                   'TIME Cost': ['2'],
                                   'TIME Fitness': ['4'],
                                   'TIME Value': ['5'],
                                   'Test plan': ['Shibboleth Upgrade - EPR v4.26.x (Release Date dd/mm/2016)'],
                                   'Type': ['Application'],
                                   'Vendor': ['Internet2'],
                                   'Version': ['Shibboleth 3']})

    def test_page_properties_extraction_with_empty_fields(self):
        page = self.confluence._ConfluenceAPI__make_master_detail_request({'cql': 'label = inv_item_info AND id = '
                                                                                  '88119617',
                                                                           'spaceKey': '65013279'})
        content = self.confluence._ConfluenceAPI__extract_page_properties(page)

        self.assertEqual(content, {'Account Manager': ['Name:Email:Phone:'],
                                   'Business Owner': ['regg002'],
                                   'CAUDIT Capability L0': ['Human Resource Management'],
                                   'CAUDIT Capability L1': ['Staff Engagement'],
                                   'Data Sensitivity': ['Low'],
                                   'External Users Allowed': ['No'],
                                   'Hosting Tier': ['SaaS'],
                                   'Hours of Support': ['24 x 7'],
                                   'Hours of Use': ['24 x 7'],
                                   'Implementation Year': ['2014'],
                                   'Last Upgrade Year': ['2015'],
                                   'Life Cycle Phase': ['INTRODUCTION'],
                                   'Maintenance Windows': ['TBC'],
                                   'Organisation Owner': ['IT Services'],
                                   'Platform': ['SaaS'],
                                   'Product homepage': ['http://www.15five.com'],
                                   'Service Criticality': ['No'],
                                   'Service Manager': ['regg002'],
                                   'Service Owner': ['regg002'],
                                   'Software Licensing Model': ['Software-as-a-Service'],
                                   'Subject Matter Experts': ['regg002'],
                                   'Support Site': ['http://success.15five.com/http://status.15five.com/'],
                                   'TIME Cost': ['5'],
                                   'TIME Fitness': ['4'],
                                   'TIME Value': ['2'],
                                   'Tech Contact': ['Name:Email:Phone:'],
                                   'Type': ['Application'],
                                   'Vendor': ['15five'],
                                   'Version': ['2015']})

    def test_panel_extraction_Infrastructure_table(self):
        page = \
            self.confluence._ConfluenceAPI__make_rest_request('content', '111481721', {'expand': 'body.view'})['body'][
                'view']['value']
        content = self.confluence._ConfluenceAPI__extract_panel_information(page, 'Infrastructure')

        self.assertEqual(content, {'Infrastructure': [{'Servers': [{'App': ['optfssprd01.uoa.auckland.ac.nz']}]},
                    {'Database': [{'Development': {'Account': ['VCADMIN'],
                                                   'Host': ['Local Host'],
                                                   'Password': ['Ask'],
                                                   'Schema': ['Local Host'],
                                                   'Type': ['FoxPro File '
                                                            'System']},
                                   'Production': {'Account': ['VCADMIN'],
                                                  'Password': ['Ask'],
                                                  'Schema': ['\\\\optfssprd01.uoa.auckland.ac.nz\\Accounts '
                                                             'Manager - '
                                                             'Clinic'],
                                                  'Type': ['FoxPro File '
                                                           'System']}}]}]})


if __name__ == '__main__':
    unittest.main()
