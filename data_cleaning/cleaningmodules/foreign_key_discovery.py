import pandas as pd
import numpy as np


class ForeignKey:
    def __init__(self, id, from_table, from_column, to_table, to_column, percentage, merged_list):
        self.id = id
        self.from_table = from_table
        self.from_column = from_column
        self.to_table = to_table
        self.to_column = to_column
        self.valid_percentage = percentage
        self.merged_list = merged_list  # result of inner join as a list
        self.selected = True


class ForeignKeys:
    def __init__(self):
        self.foreign_keys = {}

    def add(self, type, fk):
        if type in self.foreign_keys:
            fks = self.foreign_keys[type]
            fks.append(fk)
        else:
            self.foreign_keys[type] = [fk]

    def sort(self):
        for type in self.foreign_keys:
            foreign_keys = self.foreign_keys[type]
            foreign_keys_sorted = sorted(foreign_keys, key=lambda fk: fk.valid_percentage, reverse=True)
            self.foreign_keys[type] = foreign_keys_sorted

    def to_list_of_dicts(self):
        result = []
        for type in self.foreign_keys:
            foreign_keys = self.foreign_keys[type]
            for fk in foreign_keys:
                result.append({
                    'id': fk.id,
                    'type': type,
                    'from_table': fk.from_table,
                    'from_column': fk.from_column,
                    'to_table': fk.to_table,
                    'to_column': fk.to_column,
                    'percentage': fk.valid_percentage,
                    'checked': fk.selected})
        return result

    def select_foreign_key(self, id, checked):
        for type in self.foreign_keys:
            foreign_keys = self.foreign_keys[type]
            for fk in foreign_keys:
                if fk.id == id:
                    fk.selected = checked
                    return

    def get_fks_with_violations(self, from_table):
        result = []
        for type in self.foreign_keys:
            foreign_keys = self.foreign_keys[type]
            for fk in foreign_keys:
                if fk.selected and fk.from_table == from_table and fk.valid_percentage < 100:
                    result.append(fk)
        return result


class ForeignKeyDiscovery:
    def __init__(self, tables):
        self.tables = tables
        self.foreign_keys = ForeignKeys()
        self.valid_threshold = 90
        self.id = 0

    def check_fk_2cols(self, table1, tablename1, col1, table2, tablename2, col2, type):
        """
        Check if a foreign key is valid from col1 to col2.
        Any found foreign key will be added to self.foreign_keys.
        :param col1: a Pandas.Series object representing the first column to be checked
        :param col2: a Pandas.Series object representing the second column to be checked
        """
        # check if both col1 and col2 contain non-NA values
        if col1.count() == 0 or col2.count() == 0:
            return

        # check if col2 contains unique values only, because a foreign key always references a unique column
        col2_unique = col2.drop_duplicates(keep='first', inplace=False)
        if col2.count() != col2_unique.count():
            return

        col1_unique = col1.drop_duplicates(keep='first', inplace=False)
        col1_notna = col1_unique.dropna(inplace=False)
        col2_notna = col2_unique.dropna(inplace=False)
        merged_df = pd.merge(col1_notna, col2_notna, left_on=col1_notna.name, right_on=col2_notna.name)
        percentage = len(merged_df.index) / len(col1_notna.index) * 100
        if percentage >= self.valid_threshold:
            merged_as_series = merged_df.iloc[:, 0]
            merged_list = merged_as_series.tolist()
            new_fk = ForeignKey(self.id, tablename1, col1.name, tablename2, col2.name, round(percentage, 1),
                                merged_list)
            self.id += 1
            self.foreign_keys.add(str(type), new_fk)
            # A foreign key column does not need to be clustered
            if col1.name in table1.rules.cluster_columns:
                table1.rules.remove_cluster_col(col1.name)
            if col2.name in table2.rules.cluster_columns:
                table2.rules.remove_cluster_col(col2.name)

    def discover_fk_2tables(self, table1, table2):
        """
        Discover all foreign keys between two tables.
        :param table1: Table object representing the first table
        :param table2: Table object representing the second table
        """
        df1 = table1.get_dataframe()
        df2 = table2.get_dataframe()
        for col1 in df1.columns:
            col1_type = table1.get_column_type(col1)
            if not(np.issubdtype(col1_type, np.number)) and col1_type != np.object:
                continue
            #df1[col1].drop_duplicates(keep='first', inplace=True)
            for col2 in df2.columns:
                col2_type = table2.get_column_type(col2)
                if col2_type != col1_type:
                    continue
                #df2[col2].drop_duplicates(keep='first', inplace=True)
                self.check_fk_2cols(table1, table1.get_name(), df1[col1], table2, table2.get_name(), df2[col2], col1_type)
                self.check_fk_2cols(table2, table2.get_name(), df2[col2], table1, table1.get_name(), df1[col1], col1_type)

    def discover_fks(self):
        """
        Discover all foreign keys between all tables.
        """
        tables = self.tables
        nTables = len(tables)
        for i in range(0, nTables):
            for j in range(i + 1, nTables):
                self.discover_fk_2tables(tables[i], tables[j])

    def get_foreign_keys(self):
        return self.foreign_keys
