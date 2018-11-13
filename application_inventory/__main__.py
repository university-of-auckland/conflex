# This file deals with moving the information from the connex application database into the previously used tables.
# This means that views do not need to be rewritten and does not disrupt current applications accessing the database.
# This is a very 'hacky' way of doing this.
import argparse
import datetime
import logging
import os
import config_parser

from database.api import DatabaseAPI


# noinspection PyUnresolvedReferences,PyProtectedMember,PyShadowingNames
def insert_or_update(table, app, k, v, id_column_name, key_column_name, value_column_name, update=False):
    database = DatabaseAPI
    with database._DatabaseAPI__connection.cursor() as cursor:
        try:
            sql = "SELECT * FROM " + table + " WHERE `app`=%s AND `" + key_column_name + "`=%s"
            cursor.execute(sql, (app, k))
            result = cursor.fetchone()
            if result is not None and update:
                sql = "UPDATE `" + table + "` SET `app`=%s, `" + key_column_name + "`=%s, `" + value_column_name + "`=%s WHERE `" + id_column_name + "`=%s"
                cursor.execute(sql, (app, k, v, result[id_column_name]))
                logger.debug("Application Inventory: insert_or_update: Updating `%s`: app: %s, key: %s" % (table, str(app), str(k)))
                database._DatabaseAPI__connection.commit()
            else:
                sql = "INSERT INTO `" + table + "` (`app`, `" + key_column_name + "`, `" + value_column_name + "`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (app, k, v))
                logger.debug(
                    "Application Inventory: update_data: Inserting into `%s` new Data: app: %s, key: %s" % (table, str(app), str(k)))
                database._DatabaseAPI__connection.commit()
        except:
            logger.error(
                "Application Inventory: insert_or_update: There was an issue updating some data in the database for table: %s, app: %s, key: %s" % (
                table, str(app), str(k)))
            return False


# noinspection PyPep8Naming
def run(config):
    spaces = DatabaseAPI.get_spaces()
    APPLCTN_id = 0
    for space in spaces:
        if space['name'] == 'APPLCTN':
            APPLCTN_id = space['space_id']
    applications = DatabaseAPI.select('wiki_appli', APPLCTN_id)

    ignore_values = ['Name:Email:Phone:', 'Name:N/AEmail:N/APhone:N/A', 'N/A', 'None', '?', '? hours', '?hours', 'tbc',
                     'TBC', 'n/a']
    append_values = ['Overview', 'Roadmap']

    # Rebuild the application into the information we want it to contain.
    for application in applications:
        app_temp = {}
        app_id = application['key']
        app_name = application['value']

        logger.info('Application Inventory updating application: %s' % app_name)
        app_info = DatabaseAPI.select('wiki_appli__info', app_id)
        for info in app_info:
            if info['key'] in append_values:
                if info['key'] in app_temp:
                    app_temp[info['key']] = app_temp[info['key']] + ' ' + info['value']
                    continue
            app_temp[info['key']] = info['value']

        support_page = DatabaseAPI.select('wiki_appli_suppo', app_id)
        if len(support_page) > 0:
            # noinspection PyUnresolvedReferences
            app_support = DatabaseAPI.select('wiki_appli_suppo__info', support_page[0]['key'])
            for support in app_support:
                app_temp[support['key']] = support['value']

        arch_overview_page = DatabaseAPI.select('wiki_appli_invar', app_id)
        if len(arch_overview_page) > 0:
            # noinspection PyUnresolvedReferences
            app_arch_overview = DatabaseAPI.select('wiki_appli_invar__info', arch_overview_page[0]['key'])
            for arch_overview in app_arch_overview:
                app_temp[arch_overview['key']] = arch_overview['value']

        # Cut off the excess Overview information.
        if 'Overview' in app_temp:
            temp = app_temp['Overview'].split('The application is accessible from these locations')
            app_temp['Overview'] = temp[0]

        # Remove Empty Account Manager, Tech Contact
        app = {}
        for tag, value in app_temp.items():
            if value in ignore_values:
                continue
            app[tag] = value

        # We now have a single dictionary that contains all the information we need to sort.
        # First insert everything into the full table.
        for k, v in app.items():
            insert_or_update(config['mysql']['wiki_table_prefix'] + '_full', app_name, k, v, 'id', 'key', 'value', True)

        for label in config['application']['labels']:
            # We can do a simple update for certain labels. For others we need to do a little more work...
            table_name = config['mysql']['wiki_table_prefix'] + '_' + label

            if label == 'app_tiny_url':
                for identifier in config['application']['labels'][label]:
                    if identifier in app:
                        insert_or_update(table_name, app_name, app['tinyui'], app['webui'], 'tiny_url', 'tiny_url',
                                         'url', True)
            elif label == 'nfr':
                for identifier in config['application']['labels'][label]:
                    if identifier in app:
                        insert_or_update(table_name, app_name, identifier, app[identifier], 'id', 'metric', 'value',
                                         True)
            elif label == 'stakeholder':
                for identifier in config['application']['labels'][label]:
                    if identifier in app:
                        insert_or_update(table_name, app_name, identifier, app[identifier], 'id', 'role', 'person',
                                         True)
            elif label == 'support':
                for identifier in config['application']['labels'][label]:
                    if identifier in app:
                        insert_or_update(table_name, app_name, identifier, app[identifier], 'id', 'role', 'team', True)
            else:
                # Label uses a simple k-v store so can just update those rows...
                for identifier in config['application']['labels'][label]:
                    if identifier in app:
                        insert_or_update(table_name, app_name, identifier, app[identifier], 'id', 'key', 'value', True)


if __name__ == '__main__':
    # Argument parsing.
    parser = argparse.ArgumentParser(description='Connex Wiki Integration Application.')
    parser.add_argument('--config', action='store', help='the location of the configuration file to run the application with.')
    args = parser.parse_args()

    conf = config_parser.parse(args.config or os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.yaml')))

    # Change working directory to parent so DatabaseAPI works.
    os.chdir('../')

    # Setup logging,
    logger = logging.getLogger(__name__)
    logger.info('Application Inventory CleanUp starting at: %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    DatabaseAPI.connect(conf)

    # Run the application inventory tool.
    run(conf)

    DatabaseAPI.disconnect()
    logger.info('Application Inventory CleanUp finished at: %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))