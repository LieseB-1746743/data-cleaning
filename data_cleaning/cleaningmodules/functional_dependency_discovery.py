import pandas as pd
import itertools
import warnings


class FunctionalDependency:
    def __init__(self, lhs, rhs, percentage, id):
        """
        :param lhs: left-hand-side as a list of strings (column names)
        :param rhs: right-hand-side as a string (column name)
        """
        self.lhs = lhs
        self.rhs = rhs
        self.percentage = round(percentage, 1)
        self.checked = True
        self.id = id


class FunctionalDependencyDiscovery:
    def __init__(self, table, violation_threshold=10):
        self.functional_dependencies = []
        self.table = table
        self.violation_threshold = violation_threshold
        self.id = 1

        # temporary
        self.nblocks = None
        self.blocksize_min = None
        self.blocksize_med = None
        self.blocksize_avg = None
        self.blocksize_max = None
        self.percentage = None

    def createSubsets(self, elements, maxLength):
        """
        Create all subsets of elements with maxLength as maximum length of the subset.
        :param elements: list of strings
        :param maxLength: maximum length of subset
        :return: list of all subsets
        """
        subsets = []
        for i in range(1, maxLength + 1):  # 1, 2, ..., maxLength
            sublist = list(itertools.combinations(elements, i))  # create all subsets of length i
            sublist = map(lambda x: list(x), sublist)
            subsets += sublist
        return subsets

    def calc_percentage_violations(self, df, lhs, rhs):
        """
        Calculate the percentage of total rows that are violating the functional dependency lhs -> rhs
        :param df: the table as a Pandas.Dataframe
        :param lhs: left-hand-side of the functional dependency
        :param rhs: right-hand-side of the functional dependency
        :return: None if the percentage cannot be calculated because there are no two tuples with the same lhs
                 , or the percentage of violations otherwise
        """
        all_attrs = lhs.copy()
        all_attrs.append(rhs)
        df_sub = df[all_attrs]
        df_sub = df_sub.dropna()
        total_rows = len(df_sub.index)
        df_sub = df_sub.groupby(lhs, sort=False)[rhs]
        self.nblocks = df_sub.ngroups
        self.blocksize_min = df_sub.size().min()
        self.blocksize_max = df_sub.size().max()
        self.blocksize_avg = round(df_sub.size().mean(), 1)
        self.blocksize_med = round(df_sub.size().median(),1)
        size = df_sub.size()
        if size.loc[size > 1].empty:  # cannot find two tuples with the same left-hand-side
            return None
        nunique = df_sub.nunique()
        nunique = nunique.loc[nunique > 1]
        warnings.filterwarnings("ignore")
        non_unique_groups = pd.Series(list(nunique.index))
        warnings.filterwarnings("default")
        if len(non_unique_groups) == 0:
            n_violating_rows = 0
        else:
            non_unique_groups = pd.DataFrame(non_unique_groups.tolist(), index=non_unique_groups.index)
            non_unique_groups.columns = lhs
            merged = pd.merge(df, non_unique_groups, on=lhs)
            merged = merged.groupby(lhs, sort=False)[rhs].value_counts()
            n_violating_rows = merged.sum() - merged.groupby(lhs, sort=False).max().sum()
        percentage_violations = n_violating_rows / total_rows * 100
        self.percentage = round(100-percentage_violations, 1)
        return percentage_violations

    def fd_valid_percentage(self, df, lhs, rhs):
        """
        Check if a functional dependency is valid for at least 90% of the rows.
        :param df: table as a Pandas.DataFrame
        :param lhs: left-hand-side of the functional dependency as a list of string(s)
        :param rhs: right-hand-side of the functional dependency as string
        :return: True if the FD is valid, False otherwise
        """
        percentage_violations = self.calc_percentage_violations(df, lhs, rhs)
        if percentage_violations and percentage_violations < self.violation_threshold:
            return float(100 - percentage_violations)
        return None

    def boolean_in_fd(self, lhs, rhs):
        for attribute in lhs:
            if self.table.get_column_type(attribute) == bool:
                return True
        if self.table.get_column_type(rhs) == bool:
            return True
        return False

    def calc_fds_on_subset(self, df, df_sub, attr):
        """
        Find all functional dependencies in df. All FDs will be saved in self.functional_dependencies.
        :param df: the full table as a Pandas.Dataframe
        :param df_sub: table as a Pandas.Dataframe containing a subset of the original table
        :param attr: all column names of df
        """
        for rhs in attr:  # for every possible RHS
            # create subsets: create all possible left-hand-sides
            attr_left = attr.copy()
            attr_left.remove(rhs)  # prune trivial FD's
            subsets = self.createSubsets(attr_left, 1)
            fd_lhs = []
            for lhs in subsets:  # for every possible subset (=LHS)
                if len(set(fd_lhs).intersection(set(lhs))) > 0:  # we won't check for non-minimal FD's
                    continue
                if self.boolean_in_fd(lhs, rhs):
                    continue
                if self.fd_valid_percentage(df_sub, lhs, rhs):
                    percentage = self.fd_valid_percentage(df, lhs, rhs)
                    if percentage:
                        if len(lhs) == 1:
                            fd_lhs.append(lhs[0])
                        new_fd = FunctionalDependency(lhs, rhs, percentage, self.id)
                        self.id += 1
                        self.functional_dependencies.append(new_fd)  # save FD

    def calc_subset_size(self, df):
        """
        Calculate amount of rows based on total amount of rows and columns.
        :param df: full dataset as Pandas.DataFrame
        :return: subset size as an int
        """
        nCols = len(df.columns)
        nRows = len(df.index)
        size = min(int(nRows / nCols), 100000)
        size = max(size, 10000)
        size = min(size, nRows)
        return size

    def calc_fds(self):
        """
        Discover all functional dependencies in df. They will be saved in self.functional_dependencies.
        """
        df = self.table.get_dataframe()
        subset_size = self.calc_subset_size(df)
        df_sub = df.head(subset_size)

        columns = [col for col in list(df_sub.columns) if df_sub[col].dtype != type(True) and self.table.get_column_type(col) is not None]
        self.calc_fds_on_subset(df, df_sub, columns)
        self.functional_dependencies = sorted(self.functional_dependencies, key=lambda fd: fd.percentage, reverse=True)
