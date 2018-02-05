# import unittest
#
# import datetime
#
# from dateutil.tz import tzoffset
#
# from database.api import DatabaseAPI
#
#
# # noinspection PyMethodMayBeStatic
# class TestDatabaseAPI(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         DatabaseAPI.connect()
#         DatabaseAPI.create_spaces_table()
#         DatabaseAPI.create_table('test')
#
#     def test_update_data(self):
#         time = datetime.datetime(2017, 7, 27, 10, 41, 10, tzinfo=tzoffset(None, 43200))
#         data = DatabaseAPI.insert_or_update('test', 65013279, 123, 'hello', time)
#
#         self.assertEqual(data, True)
#
#     def test_update_spaces(self):
#         time = datetime.datetime(2017, 7, 27, 10, 41, 7, tzinfo=tzoffset(None, 43200))
#         data = DatabaseAPI.update_spaces(65013279, 'APPLCTN', time)
#
#         self.assertEqual(data, None)
#
#     @classmethod
#     def tearDownClass(cls):
#         DatabaseAPI.disconnect()
#
#
# if __name__ == '__main__':
#     unittest.main()
