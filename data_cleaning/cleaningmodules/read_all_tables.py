import os
from data_cleaning.cleaningmodules.table import Table
from data_cleaning.cleaningmodules.foreign_key_discovery import ForeignKeyDiscovery
from data_cleaning.cleaningmodules.settings import Settings
import traceback


def read_all_tables(path_to_tables_file):
    """
    Read all tables mentioned in path_to_tables_file and return a dictionary containing all tables."
    :param path_to_tables_file: path to file that contains all absolute paths to the csv files.
    :return: a dictionary of key-value pairs where key is the table name and value the Table object
    and the foreign keys in JSON format
    """
    # Initialise global settings
    settings = Settings()

    dict_of_tables = {}
    list_of_tables = []
    list_of_tablenames = []
    with open(path_to_tables_file) as f:
        for path in f:
            try:
                stripped_path = path.rstrip()
                (head, tail) = os.path.split(stripped_path)
                extension = tail[tail.rfind('.'):]
                if extension != '.csv':
                    raise Exception("File extension must be .csv")
                name = tail[:tail.rfind('.')]
                name = name.replace(" ", "")
                print("Processing table", stripped_path, "...")
                table_object = Table(name, head, stripped_path)
                dict_of_tables[name] = table_object
                list_of_tables.append(table_object)
                list_of_tablenames.append(name)
            except Exception as e:
                # traceback.print_exc()
                print("Could not read file", stripped_path, "due to the following error:", e)

    print("Discovering foreign keys...")
    fk_discovery = ForeignKeyDiscovery(list_of_tables)
    fk_discovery.discover_fks()
    fks = fk_discovery.get_foreign_keys()
    fks.sort()

    return dict_of_tables, list_of_tablenames, fks, settings
