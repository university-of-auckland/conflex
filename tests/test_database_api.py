import unittest

import datetime

from dateutil.tz import tzoffset

from database.api import DatabaseAPI


# noinspection PyMethodMayBeStatic
class TestDatabaseAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DatabaseAPI.connect()
        DatabaseAPI.create_spaces_table()
        DatabaseAPI.create_table('test')

    def test_update_data(self):
        DatabaseAPI.create_table('test')
        data = DatabaseAPI.update_data('test', 22, 123, 'hello')

        self.assertEqual(data, 65013279)

    def test_update_spaces(self):
        time = datetime.datetime(2017, 7, 27, 10, 41, 7, tzinfo=tzoffset(None, 43200))
        DatabaseAPI.update_spaces(12232421, 'APPLCTN', time)

        self.assertEqual(time, 65013279)

    @classmethod
    def tearDownClass(cls):
        DatabaseAPI.disconnect()


if __name__ == '__main__':
    unittest.main()
