import unittest

import datetime

from dateutil.tz import tzoffset

from confluence.api import ConfluenceAPI


class TestConfluenceAPIPageRetrieval(unittest.TestCase):

    def test_application_retrieve_all_children(self):
        # Gets the children of the REFARCH space.
        child_ids = ConfluenceAPI.get_child_page_ids(87201717)

        self.assertEqual(child_ids, {
             63147993: {'last_updated': datetime.datetime(2015, 7, 20, 9, 55, 1, tzinfo=tzoffset(None, 43200)),
                        'name': 'Reference Architecture'},
             86508608: {'last_updated': datetime.datetime(2017, 5, 29, 9, 47, 13, tzinfo=tzoffset(None, 43200)),
                        'name': 'Technical Reference Architecture Overview and Purpose'},
             106007803: {'last_updated': datetime.datetime(2016, 2, 9, 8, 33, 12, tzinfo=tzoffset(None, 46800)),
                         'name': 'TRA_Data Warehousing future state'},
             121246868: {'last_updated': datetime.datetime(2017, 10, 31, 9, 55, 48, tzinfo=tzoffset(None, 46800)),
                         'name': 'Reference Guides'},
             124525205: {'last_updated': datetime.datetime(2017, 6, 21, 9, 35, 4, tzinfo=tzoffset(None, 43200)),
                         'name': 'Security Reference Architecture Project Update 21 June '
                                 '2017'},
             125700626: {'last_updated': datetime.datetime(2017, 7, 27, 10, 41, 7, tzinfo=tzoffset(None, 43200)),
                         'name': 'Decision log'}})

    def test_space_to_id_conversion(self):
        space_id = ConfluenceAPI.get_homepage_id_of_space('APPLCTN')

        self.assertEqual(space_id, 65013279)


if __name__ == '__main__':
    unittest.main()
