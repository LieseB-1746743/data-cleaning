import pandas as pd
import numpy as np
import warnings
from .denial_constraint_discovery import DenialConstraintDiscovery
from .functional_dependency_discovery import FunctionalDependencyDiscovery
from .clustering import Clustering
from .outlier_detection import OutlierDetection
from .rules import Rules
from .actions import OnNullValue


class Table:
    def __init__(self, name, path, path_and_filename):
        self.path = path
        self.name = name
        self.df = self.read_table(path_and_filename)
        self.columns = list(self.df.columns)
        self.column_types = self.detect_coltypes()
        self.characteristics = self.detect_characteristics()

        cluster_columns = self.detect_cluster_columns()
        non_cluster_columns = self.get_noncluster_columns(cluster_columns)
        denial_constraints = self.discover_denial_constraints()
        outlier_detection = self.init_outlier_detection()
        on_null_detection = dict.fromkeys(self.columns, OnNullValue.FLAG)
        date_columns = [column for column in self.columns if np.issubdtype(self.get_column_type(column), np.datetime64)]
        self.rules = Rules(cluster_columns, non_cluster_columns, denial_constraints, outlier_detection,
                           on_null_detection, date_columns, FunctionalDependencyDiscovery(self))

        self.results = False
        self.clusters = {}  # key = column name and value contains the clusters

    def init_outlier_detection(self):
        outlier_detection = {}
        for col in self.columns:
            type = self.get_column_type(col)
            if type is not None and (np.issubdtype(type, np.number) or np.issubdtype(type, np.datetime64)):
                data = self.df[col]
                od = OutlierDetection(data)
                od.calc_interval()
                outlier_detection[col] = od
        return outlier_detection

    def cluster_all_columns(self):
        for column in self.rules.cluster_columns:
            print("Starting with clustering column", column)
            self.calculate_clusters(column)
        self.results = True

    def calculate_clusters(self, column):
        clustering = Clustering(self, column)
        clustering.cluster()
        self.clusters[column] = clustering

    def discover_denial_constraints(self):
        dc_discovery = DenialConstraintDiscovery(self)
        dcs = dc_discovery.discover_denial_constraints()
        return dcs

    def detect_cluster_columns(self):
        """
        Search which columns need to be clustered.
        :return: A list of column names.
        """
        result = []
        for col in self.columns:
            type = self.get_column_type(col)
            if type is None or type != np.object:
                continue
            s = self.df[col].copy()
            value_counts = s.value_counts(sort=False)
            n_diff_values = value_counts.count()
            unique_values = value_counts.loc[(value_counts == 1)]
            n_unique_values = unique_values.count()
            if float(n_unique_values/n_diff_values) >= 0.2:
                result.append(col)
        return result

    def detect_coltypes(self):
        """
        Detect column types
        :return: Dictionary of key-value pairs, where key is the column name and value the column type.
        """
        col_types = {}
        for col in self.columns:
            coldata = self.df[col].dropna(inplace=False)
            if len(coldata.index) == 0:
                col_types[col] = None
                continue
            type = self.df[col].dtype
            if isinstance(type, bool):
                col_types[col] = bool
            elif type == np.object:  # string
                coldata_bool = coldata.loc[(coldata == True) | (coldata == False) | (coldata == "Y") | (coldata == "N") | (coldata == "0") | (coldata == "1")]
                if len(coldata.index) == len(coldata_bool.index):
                    col_types[col] = bool
                else:
                    datecol = self.parse_to_dates(self.df[col])
                    if not datecol.empty:
                        self.df[col] = datecol
                        col_types[col] = datecol.dtype
                    else:
                        col_types[col] = type
            else:  # numeric
                coldata_bool = coldata.loc[(coldata == 0) | (coldata == 1)]
                if len(coldata.index) == len(coldata_bool.index):
                    col_types[col] = bool
                else:
                    col_types[col] = type
        return col_types

    def read_table(self, path):
        warnings.simplefilter("ignore")
        flag_columns = ["FOREIGN_KEY_VIOLATION", "SMALLER_THAN_VIOLATION", "NULL_FLAG", "FUTURE_DATE_FLAG",
                        "FOREIGN_KEY_VIOLATION_INFO", "SMALLER_THAN_VIOLATION_INFO", "NULL_FLAG_INFO",
                        "FUTURE_DATE_FLAG_INFO", "DUPLICATE_FLAG_MESSAGE", "OUTLIER_FLAG_INFO"]
        df = pd.read_csv(path, usecols=lambda x: x not in flag_columns)
        warnings.simplefilter("default")

        return df

    def parse_to_dates(self, col):
        """
        Try to parse the column to a date column.
        :param col: The column as a Pandas.Series object.
        :return: Date column if possible, an empty column otherwise
        """
        notna = col.dropna(inplace=False)
        nNotNull_original = notna.size
        nunique = notna.drop_duplicates(inplace=False, keep='first')
        if (nunique.count() / nNotNull_original * 100) < 0.1:
            return pd.Series(dtype='float64')

        firstpart = notna.iloc[:int(nNotNull_original * 0.1)].copy()
        secondpart = notna.iloc[int(nNotNull_original * 0.1)+1:].copy()
        length_firstpart = firstpart.size

        # detecting "%d%b%Y" goes very slow, so test this format first before detecting the other formats
        datecol = pd.to_datetime(notna, format="%d%b%Y", errors="coerce")
        if (datecol.count() / nNotNull_original) >= 0.9:
            return datecol

        dayfirst = pd.to_datetime(firstpart, infer_datetime_format=True, dayfirst=True, errors="coerce")

        if (dayfirst.count() / length_firstpart) >= 0.8:
            dayfirst_secondpart = pd.to_datetime(secondpart, infer_datetime_format=True, dayfirst=True, errors="coerce")
            datecol = dayfirst.append(dayfirst_secondpart)
            if (datecol.count() / nNotNull_original) >= 0.9:
                return datecol

        monthfirst = pd.to_datetime(firstpart, infer_datetime_format=True, dayfirst=False, errors="coerce")
        if (monthfirst.count() / length_firstpart) >= 0.8:
            monthfirst_secondpart = pd.to_datetime(secondpart, infer_datetime_format=True, dayfirst=False, errors="coerce")
            datecol = monthfirst.append(monthfirst_secondpart)
            if (datecol.count() / nNotNull_original) >= 0.9:
                return datecol

        return pd.Series(dtype='float64')

    def detect_characteristics(self):
        warnings.simplefilter('ignore')
        result = {}

        for colname in self.columns:
            type = self.get_column_type(colname)
            if type is None:
                result[colname] = {
                    "Type": "No type detected - empty column"
                }
            elif type == np.object:
                result[colname] = self.detect_characteristics_string(self.df[colname])
            elif np.issubdtype(type, np.number):
                result[colname] = self.detect_characteristics_numeric(self.df[colname])
            elif type == bool:
                result[colname] = self.detect_characteristics_bool(self.df[colname])
            elif np.issubdtype(type, np.datetime64):
                result[colname] = self.detect_characteristics_date(self.df[colname])
            else:
                result[colname] = {}

        warnings.simplefilter('default')
        return result

    def detect_characteristics_numeric(self, col):
        """
        Detect characteristics of a numeric column.
        :param col: Pandas.Series object
        """
        nMissing = col.size - col.count()
        percentage = round(float(nMissing / col.size * 100), 4)
        if percentage == 100:
            return {"Missing (#)": int(nMissing),
                    "Missing (%)": percentage,
                    "Minimum": None,
                    "Mean": None,
                    "Median": None,
                    "Maximum": None}

        min = col.min()
        max = col.max()
        avg = round(float(col.mean()), 2)
        median = round(float(col.median()), 2)
        return {"Type": "numeric",
                "Missing (#)": int(nMissing),
                "Missing (%)": percentage,
                "Minimum": int(min),
                "Mean": avg,
                "Median": median,
                "Maximum": int(max)}

    def detect_characteristics_date(self, col):
        """
        Detect characteristics of a date column.
        :param col: Pandas.Series object
        """
        nMissing = col.size - col.count()
        percentage = round(float(nMissing / col.size * 100), 4)
        return {"Type": "date",
                "Missing (#)": int(nMissing),
                "Missing (%)": percentage}

    def detect_characteristics_string(self, col):
        """
        Detect characteristics of a column containing strings.
        :param col: Pandas.Series object
        """
        nMissing = col.size - col.count()
        percentage = round(float(nMissing / col.size * 100), 4)
        return {"Type": "string",
                "Missing (#)": int(nMissing),
                "Missing (%)": percentage}

    def detect_characteristics_bool(self, col):
        """
        Detect characteristics of a boolean column.
        :param col: Pandas.Series object
        """
        true = col.loc[(col == True) | (col == "Y") | (col == 1)]
        nTrue = true.count()
        false = col.loc[(col == False) | (col == "N") | (col == 0)]
        nFalse = false.count()
        nMissing = col.size - nTrue - nFalse
        percentage = round(float(nMissing / col.size * 100), 4)
        return {"Type": "boolean",
                "Missing (#)": int(nMissing),
                "Missing (%)": percentage,
                "True (#)": int(nTrue),
                "False (#)": int(nFalse)}

    def get_columns(self):
        return self.columns

    def get_column_types(self):
        return self.column_types

    def get_column_type(self, col):
        return self.column_types[col]

    def get_dataframe(self):
        return self.df

    def get_name(self):
        return self.name

    def get_characteristics(self, colname=None):
        if colname:
            return self.characteristics[colname]
        else:
            return self.characteristics

    def get_noncluster_columns(self, cluster_columns):
        """
        Get list of columns that aren't selected for clustering, but can be clustered.
        :param cluster_columns: columns detected and/or selected for clustering
        :return: list of column names
        """
        result = []
        for col in self.columns:
            type = self.get_column_type(col)
            if (col not in cluster_columns) and (type is not None) and (type == np.object):
                result.append(col)
        return result
