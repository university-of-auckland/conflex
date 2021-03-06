import datetime
import logging

import pymysql.cursors

logger = logging.getLogger(__name__)


# noinspection SqlResolve
class DatabaseAPI(object):
    __prefix = None
    __connection = None

    @classmethod
    def connect(cls, config):
        """Connect to the database."""
        DatabaseAPI.__connection = pymysql.connect(host=config['mysql']['host'],
                                                   port=config['mysql']['port'],
                                                   db=config['mysql']['database'],
                                                   user=config['mysql']['username'],
                                                   password=config['mysql']['password'],
                                                   charset='utf8mb4',
                                                   cursorclass=pymysql.cursors.DictCursor)
        cls.__prefix = config['mysql']['table_prefix']
        logger.debug('connect_to_database: Connected to MySQL database: %s' % str(config['mysql']['host']) + ':' + str(
            config['mysql']['port']) + '/' + config['mysql']['database'])

    @classmethod
    def disconnect(cls):
        """ Disconnect from the database."""
        DatabaseAPI.__connection.close()

    @classmethod
    def create_spaces_table(cls):
        """Creates the PREFIX_spaces table within the database.
        """
        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SHOW TABLES LIKE '" + cls.__prefix + "_spaces'"
            cursor.execute(sql)
            if cursor.fetchone() is None:
                sql = "CREATE TABLE IF NOT EXISTS `" + cls.__prefix + "_spaces` (`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY , `space_id` INT(11) NOT NULL UNIQUE, `name` VARCHAR(256) NOT NULL, `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP())"
                cursor.execute(sql)
                logger.debug("create_spaces_table: Created table: `" + cls.__prefix + "'_spaces`")
                DatabaseAPI.__connection.commit()

    @classmethod
    def create_application_table(cls):
        """Creates the PREFIX_conflex table within the database.

        """
        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SHOW TABLES LIKE '" + cls.__prefix + "_conflex'"
            cursor.execute(sql)
            if cursor.fetchone() is None:
                sql = "CREATE TABLE IF NOT EXISTS `" + cls.__prefix + "_conflex` (`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY , `key` VARCHAR(60) NOT NULL UNIQUE, `value` VARCHAR(256) NOT NULL)"
                cursor.execute(sql)
                logger.debug("create_spaces_table: Created table: `" + cls.__prefix + "_conflex`")
                DatabaseAPI.__connection.commit()

    @classmethod
    def update_spaces(cls, space_id, space_name, last_updated):
        """Basic space update/insert.

        This method will update/insert the spaces into the spaces table. It will update the table value only if
        the last_updated times are different.

        Args:
            space_id (int): The id of the space to update/insert.
            space_name (str): Name of the space.
            last_updated (datetime.datetime): The last time the space was updated.

        """
        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SELECT * FROM `" + cls.__prefix + "_spaces` WHERE `space_id`=%s"
            cursor.execute(sql, space_id)

            space = cursor.fetchone()
            if space is not None:
                # Object found, perform an update if last_update out of date.
                if space['last_updated'] != last_updated.replace(tzinfo=None):
                    sql = "UPDATE `" + cls.__prefix + "_spaces` SET `name`=%s, `last_updated`=%s WHERE `space_id`=%s"
                    cursor.execute(sql, (space_name, last_updated.strftime('%Y-%m-%d %H:%M:%S'), space_id))
                    logger.debug("update_spaces: Updating " + cls.__prefix + "_space %d: %s" % (space_id, space_name))
            else:
                sql = "INSERT INTO `" + cls.__prefix + "_spaces` (`space_id`, `name`, `last_updated`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (space_id, space_name, last_updated.strftime('%Y-%m-%d %H:%M:%S')))
                logger.debug("update_spaces: Inserting " + cls.__prefix + "_space %d: %s" % (space_id, space_name))

            DatabaseAPI.__connection.commit()

    @classmethod
    def update_conflex_application(cls, k, v):
        """Basic application update/insert.

        This method will update/insert the key value pairs into the PREFIX_conflex table.

        Args:
            k (str): The key of the conflex_application row to update/insert.
            v (str): A Value to update/insert

        Returns:
            str: The previous data that was in the key.
        """
        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SELECT * FROM `" + cls.__prefix + "_conflex` WHERE `key`=%s"
            cursor.execute(sql, k)

            info = cursor.fetchone()
            if info is not None:
                # Object found, perform an update.
                if info['value'] != v:
                    sql = "UPDATE `" + cls.__prefix + "_conflex` SET `value`=%s WHERE `key`=%s"
                    cursor.execute(sql, (v, k))
                    logger.debug("update_conflex_application: Updating " + cls.__prefix + "_conflex %s: %s" % (k, v))
            else:
                sql = "INSERT INTO `" + cls.__prefix + "_conflex` (`key`, `value`) VALUES (%s, %s)"
                cursor.execute(sql, (k, v))
                logger.debug("update_conflex_application: Inserting " + cls.__prefix + "_conflex %s: %s" % (k, v))

            DatabaseAPI.__connection.commit()
            return info

    @classmethod
    def create_table(cls, table_name, varchar_key=False):
        """Creates a table with a specified name and can allow for a VARCHAR key..

        Args:
            table_name (str): A name for the table.
            varchar_key (bool): Will default to an INT(11) `key` column or a VARCHAR(512) if this is True.

        """
        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SHOW TABLES LIKE '" + table_name + "'"
            cursor.execute(sql)
            if cursor.fetchone() is None:
                if varchar_key:
                    sql = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, `parent` INT(11) UNSIGNED NOT NULL, `key` VARCHAR(512) NOT NULL, `value` TEXT, `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(), INDEX `parent__index` (`parent`))"
                    logger.debug("create_table: Creating table: `%s` with VARCHAR(256) key" % table_name)
                else:
                    sql = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, `parent` INT(11) UNSIGNED NOT NULL, `key` INT(11) UNSIGNED NOT NULL, `value` TEXT, `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(), INDEX `parent__index` (`parent`), INDEX `key__index` (`key`))"
                    logger.debug("create_table: Creating table: `%s` with INT(11) key" % table_name)

                cursor.execute(sql)
                DatabaseAPI.__connection.commit()

    @classmethod
    def insert_or_update(cls, table, parent, k, value, last_updated, update=False):
        """Inserts/updates data in a table.

        Args:
            table (str): The table to insert/update the data into.
            parent (int): The id of the parent that we are inserting/updating.
            k (str): An integer representing a page key or the key name for the value.
            value (str): The value to update.
            last_updated (datetime.datetime): The last update time of the row to insert/update.
            update (bool): Whether we are to insert duplicate rows or update duplicate parent-key rows.

        Returns:
            bool: If Data was inserted or not.

        """
        # Perform a quick data cleanup first by not inserting information that is not useful.
        if value in ['Name:Email:Phone:', 'Name:N/AEmail:N/APhone:N/A', 'N/A', 'None', '?', '? hours', '?hours', 'tbc', 'TBC', 'n/a', 'None', None]:
            return False

        with DatabaseAPI.__connection.cursor() as cursor:
            try:
                sql = "SELECT * FROM " + table + " WHERE `parent`=%s AND `key`=%s"
                cursor.execute(sql, (parent, k))
                result = cursor.fetchone()
                if result is not None and update:
                    if result['last_updated'] != last_updated.replace(microsecond=0, tzinfo=None):
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
        """Checks to see if the data exists in the table.

        Args:
            table (str): The table to check for the data.
            parent (int): The parent component to find.
            k (str): The key component to find.

        Returns:
            dict: The data if it exists in the table.

        """

        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SELECT * FROM " + table + " WHERE `parent`=%s AND `key`=%s"
            cursor.execute(sql, (parent, k))
            return cursor.fetchone()

    @classmethod
    def delete(cls, table, parent, k=None):
        """Deletes data from a table.

        Args:
            table (str): The table to delete the data from.
            parent (int): The parent component to delete
            k (str): The key component to delete (if provided).

        """
        with DatabaseAPI.__connection.cursor() as cursor:
            if k:
                sql = "DELETE FROM `" + table + "` WHERE `parent`=%s AND `key`=%s"
                cursor.execute(sql, (parent, k))
            else:
                sql = "DELETE FROM `" + table + "` WHERE `parent`=%s"
                cursor.execute(sql, parent)
            DatabaseAPI.__connection.commit()

    @classmethod
    def get_spaces(cls):
        """Retrieves all the wiki spaces.

        Returns:
            list: The list of spaces.

        """
        with DatabaseAPI.__connection.cursor() as cursor:
            sql = "SELECT * FROM `wiki_spaces`"
            cursor.execute(sql)

            return cursor.fetchall()

    @classmethod
    def select(cls, table, parent=None, k=None):
        """Retrieves information from the database given a parent-key combination.

        Args:
            table (str): The table to find the data in
            parent (int): The parent component to find.
            k (str): The key component to find (if provided).

        Returns:
            list: The list of information.
        """
        with DatabaseAPI.__connection.cursor() as cursor:
            if k and parent:
                sql = "SELECT * FROM `" + table + "` WHERE `parent`=%s AND `key`=%s"
                cursor.execute(sql, (parent, k))
            elif not k and parent:
                sql = "SELECT * FROM `" + table + "` WHERE `parent`=%s"
                cursor.execute(sql, parent)
            elif k and not parent:
                sql = "SELECT * FROM `" + table + "` WHERE `key`=%s"
                cursor.execute(sql, k)
            else:
                sql = "SELECT * FROM `" + table + "`"
                cursor.execute(sql)

            return cursor.fetchall()
