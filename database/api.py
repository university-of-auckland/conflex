import datetime
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
        """Connect to the database."""
        DatabaseAPI.__connection = pymysql.connect(host=DatabaseAPI.host,
                                                   port=DatabaseAPI.port,
                                                   db=DatabaseAPI.database,
                                                   user=DatabaseAPI.__username,
                                                   password=DatabaseAPI.__password,
                                                   charset='utf8mb4',
                                                   cursorclass=pymysql.cursors.DictCursor)
        logger.debug('connect_to_database: Connected to MySQL database: %s' % str(DatabaseAPI.host) + ':' + str(
            DatabaseAPI.port) + '/' + DatabaseAPI.database)

    @classmethod
    def disconnect(cls):
        """ Disconnect from the database."""
        DatabaseAPI.__connection.close()

    @classmethod
    def create_spaces_table(cls):
        """Summary line.

        Extended description of function.

        Args:
            arg1 (int): Description of arg1
            arg2 (str): Description of arg2

        Returns:
            bool: Description of return value

        """
        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SHOW TABLES LIKE 'wiki_spaces'"
            cursor.execute(sql)
            if cursor.fetchone() is None:
                sql = "CREATE TABLE IF NOT EXISTS `wiki_spaces` (`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY , `space_id` INT(11) NOT NULL UNIQUE, `name` VARCHAR(256) NOT NULL, `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP())"
                cursor.execute(sql)
                logger.debug("create_spaces_table: Created table: `wiki_spaces`")
                DatabaseAPI.__connection.commit()

    @classmethod
    def update_spaces(cls, space_id, space_name, last_updated):
        """Basic space update/insert.

        This method will update/insert the spaces into the spaces database. It will update the database value only if
        the last_updated times are different.

        Args:
            space_id (int): The id of the space to update/insert.
            space_name (str): Name of the space.
            last_updated (datetime.datetime): The last time the space was updated.

        """
        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SELECT * FROM `wiki_spaces` WHERE `space_id`=%s"
            cursor.execute(sql, space_id)

            space = cursor.fetchone()
            if space is not None:
                # Object found, perform an update if last_update out of date.
                if space['last_updated'] != last_updated.replace(tzinfo=None):
                    sql = "UPDATE `wiki_spaces` SET `name`=%s, `last_updated`=%s WHERE `space_id`=%s"
                    cursor.execute(sql, (space_name, last_updated.strftime('%Y-%m-%d %H:%M:%S'), space_id))
                    logger.debug("update_spaces: Updating wiki space %d: %s" % (space_id, space_name))
            else:
                sql = "INSERT INTO `wiki_spaces` (`space_id`, `name`, `last_updated`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (space_id, space_name, last_updated.strftime('%Y-%m-%d %H:%M:%S')))
                logger.debug("update_spaces: Inserting wiki space %d: %s" % (space_id, space_name))

            DatabaseAPI.__connection.commit()

    @classmethod
    def create_table(cls, table_name, varchar_key=False):
        """Summary line.

            Extended description of function.

            Args:
                arg1 (int): Description of arg1
                arg2 (str): Description of arg2

            Returns:
                bool: Description of return value

        """
        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SHOW TABLES LIKE '" + table_name + "'"
            cursor.execute(sql)
            if cursor.fetchone() is None:
                if varchar_key:
                    sql = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, `parent` INT(11) UNSIGNED NOT NULL, `key` VARCHAR(256) NOT NULL, `value` VARCHAR(20000) NOT NULL DEFAULT '', `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(), INDEX `parent__index` (`parent`))"
                    logger.debug("create_table: Creating table: `%s` with VARCHAR(256) key" % table_name)
                else:
                    sql = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, `parent` INT(11) UNSIGNED NOT NULL, `key` INT(11) UNSIGNED NOT NULL, `value` VARCHAR(20000) NOT NULL DEFAULT '', `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(), INDEX `parent__index` (`parent`), INDEX `key__index` (`key`))"
                    logger.debug("create_table: Creating table: `%s` with INT(11) key" % table_name)

                cursor.execute(sql)
                DatabaseAPI.__connection.commit()

    @classmethod
    def insert_or_update(cls, table, parent, k, value, last_updated, update=False):
        """Summary line.

            Extended description of function.

            Args:
                arg1 (int): Description of arg1
                arg2 (str): Description of arg2

            Returns:
                bool: If Data was inserted or not.
        """
        with DatabaseAPI.__connection.cursor() as cursor:
            try:
                sql = "SELECT * FROM " + table + " WHERE `parent`=%s AND `key`=%s"
                cursor.execute(sql, (parent, k))
                result = cursor.fetchone()
                if result is not None and update:
                    if result['last_updated'] != last_updated.replace(tzinfo=None):
                        sql = "UPDATE `" + table + "` SET `parent`=%s, `key`=%s, `value`=%s, `last_updated`=%s WHERE `id`=%s"
                        cursor.execute(sql, (parent, k, value, last_updated, result['id']))
                        logger.debug("insert_or_update: Updating `%s`: parent: %s, key: %s" % (table, str(parent), str(k)))
                        DatabaseAPI.__connection.commit()
                        return True
                else:
                    sql = "INSERT INTO `" + table + "` (`parent`, `key`, `value`, `last_updated`) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (parent, k, value, last_updated))
                    logger.debug("update_data: Inserting into `%s` new Data: parent: %s, key: %s" % (table, str(parent), str(k)))
                    DatabaseAPI.__connection.commit()
                    return True

                return False
            except:
                logger.error("insert_or_update: There was an issue updating some data in the database for table: %s, parent: %s, key: %s" % (table, str(parent), str(k)))
                return False

    @classmethod
    def check_data_exists(cls, table, parent, k):
        """Summary line.

            Extended description of function.

            Args:
                arg1 (int): Description of arg1
                arg2 (str): Description of arg2

            Returns:
                bool: If Data was inserted or not.
        """

        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SELECT * FROM " + table + " WHERE `parent`=%s AND `key`=%s"
            cursor.execute(sql, (parent, k))
            return cursor.fetchone()

    @classmethod
    def delete(cls, table, parent, k=None):
        """Summary line.

            Extended description of function.

            Args:
                arg1 (int): Description of arg1
                arg2 (str): Description of arg2

            Returns:
                bool: If Data was inserted or not.
        """
        with DatabaseAPI.__connection.cursor() as cursor:
            if k:
                sql = "DELETE FROM `" + table + "` WHERE `parent`=%s AND `key`=%s"
                cursor.execute(sql, (parent, k))
            else:
                sql = "DELETE FROM `" + table + "` WHERE `parent`=%s"
                cursor.execute(sql, parent)
