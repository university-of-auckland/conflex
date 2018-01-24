import pymysql.cursors

from settings import *

logger = logging.getLogger(__name__)


class DatabaseAPI(object):
    __connection = None
    host = config['mysql']['host']
    port = config['mysql']['port']
    database = config['mysql']['database']
    __username = config['mysql']['username']
    __password = config['mysql']['password']

    @classmethod
    def connect(cls):
        # Connect to the database
        DatabaseAPI.__connection = pymysql.connect(host=DatabaseAPI.host,
                                                   port=DatabaseAPI.port,
                                                   db=DatabaseAPI.database,
                                                   user=DatabaseAPI.__username,
                                                   password=DatabaseAPI.__password,
                                                   charset='utf8mb4',
                                                   cursorclass=pymysql.cursors.Cursor)
        logger.debug('connect_to_database: Connected to MySQL database: %s' % str(DatabaseAPI.host) + ':' + str(
            DatabaseAPI.port) + '/' + DatabaseAPI.database)

    @classmethod
    def disconnect(cls):
        DatabaseAPI.__connection.close()

    @classmethod
    def create_table(cls, table_name):
        # All tables follow the same structure.
        structure = {'id': 'int '}

        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "CREATE TABLE IF NOT EXISTS " + table_name + ""
            cursor.execute(sql)

        DatabaseAPI.__connection.commit()
