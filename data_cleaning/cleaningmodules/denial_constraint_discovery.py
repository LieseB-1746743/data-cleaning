import pandas as pd


class DenialConstraint:
    def __init__(self, id, small_column, big_column, percentage):
        """
        Initialise denial constraint small_column < big_column.
        :param id: unique identifier for the denial constraint
        :param small_column: Column name with low values.
        :param big_column: Column name with high values.
        :param percentage: Constraint is valid for a percentage of the rows.
        """
        self.id = id
        self.small_col = small_column
        self.big_col = big_column
        self.percentage = percentage

    def to_json(self):
        json_object = {
            "id": self.id,
            "small_column": self.small_col,
            "big_column": self.big_col,
            "percentage": self.percentage
        }
        return json_object


class DenialConstraintDiscovery:
    def __init__(self, table):
        self.table = table  # Table object
        self.denial_constraints = []
        self.threshold = 75
        self.last_calculated_percentage = None
        self.count = 0

    def is_smaller_than(self, df, col1, col2):
        """True if col1 < col2 for at least threshold percentage of the rows."""
        df_sub = df.loc[df[col1] <= df[col2]].copy()
        nRows_sub = len(df_sub.index)
        percentage_left = (nRows_sub / len(df.index)) * 100
        self.last_calculated_percentage = round(percentage_left, 1)
        return percentage_left >= self.threshold

    def search_constraints_between_cols(self, df, col1, col2):
        df = df[[col1, col2]]
        df = df.dropna(how='any', inplace=False)
        if len(df.index) == 0:
            return
        if self.is_smaller_than(df, col1, col2):
            new_constraint = DenialConstraint(self.count, col1, col2, self.last_calculated_percentage)
            self.denial_constraints.append(new_constraint)
            self.count += 1
        elif self.is_smaller_than(df, col2, col1):
            new_constraint = DenialConstraint(self.count, col2, col1, self.last_calculated_percentage)
            self.denial_constraints.append(new_constraint)
            self.count += 1

    def discover_constraints_of_type(self, df):
        """
        Discover smaller than constraints between columns that hold for at least a threshold percentage.
        :param df: Pandas.Dataframe of columns of the same type
        """
        cols = list(df.columns)
        for i in cols:
            for j in range(cols.index(i) + 1, len(cols)):
                col1 = i
                col2 = cols[j]
                self.search_constraints_between_cols(df, col1, col2)

    def discover_denial_constraints(self):
        """
        Discover all denial constraints in self.table of type datetime and number.
        :return: Denial constraints as a sorted list of dictionaries.
        """
        df = self.table.get_dataframe()
        for type in ["datetime", "number"]:
            df_sub = df.select_dtypes(include=type)
            self.discover_constraints_of_type(df_sub)

        denial_constraints_sorted = self.sort_denial_constraints()
        list_of_dicts = list(map(lambda dc: dc.to_json(), denial_constraints_sorted))
        return list_of_dicts

    def sort_denial_constraints(self):
        denial_constraints_sorted = sorted(self.denial_constraints, key=lambda dc: dc.percentage, reverse=True)
        return denial_constraints_sorted

    # def jsonify(self):
    #     """
    #     Transform discovered denial constraints into JSON format.
    #     :return: Denial constraints in JSON format.
    #     """
    #     denial_constraints_sorted = self.sort_denial_constraints()
    #     list_of_dicts = list(map(lambda dc: dc.to_json(), denial_constraints_sorted))
    #     return json.dumps(list_of_dicts)
