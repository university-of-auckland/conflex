import unittest

from confluence.api import ConfluenceAPI


class TestConfluenceAPIPageRetrieval(unittest.TestCase):

    def test_application_retrieve_all_children(self):
        # Gets the children of the REFARCH space.
        child_ids = ConfluenceAPI.get_child_page_ids(87201717)

        self.assertEqual(child_ids, [125700626, 121246868, 124525205, 106007803, 86508608])


if __name__ == '__main__':
    unittest.main()
