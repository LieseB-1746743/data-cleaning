from data_cleaning.cleaningmodules.actions import OnNullValue, OnFutureDate
from datetime import datetime


class Rules:
    def __init__(self, cluster_columns, non_cluster_columns, denial_constraints, outlier_detection, on_null_detection,
                 date_columns, fd_discovery):
        self.cluster_columns = cluster_columns
        self.non_cluster_columns = non_cluster_columns
        self.denial_constraints = denial_constraints
        self.dc_ids_selected = list(map(lambda dc: dc['id'], self.denial_constraints))
        self.outlier_detection = outlier_detection  # dict where key = column name and value the outlier detection obj
        self.on_null_detection = on_null_detection  # dict where key = column name and value the OnNullValue action
        self.date_rules = self.init_date_rules(date_columns)
        self.unique_constraints = {}
        self.unique_constraint_counter = 0
        self.date_columns = date_columns
        self.functional_dependency_discovery = fd_discovery

    def init_date_rules(self, date_columns):
        on_future_date_detect = {}
        for date_col in date_columns:
            on_future_date_detect[date_col] = {
                "format": 5,
                "action": OnFutureDate.FLAG
            }
        return on_future_date_detect

    def change_on_future_date_detect_action(self, action, column=None):
        if column:
            if column in self.date_rules:
                self.date_rules[column]["action"] = OnFutureDate(action)
        else:
            for col in self.date_rules:
                self.date_rules[col]["action"] = OnFutureDate(action)

    def change_date_format(self, format_code, column=None):
        if column:
            if column in self.date_rules:
                self.date_rules[column]["format"] = format_code
        else:
            for col in self.date_rules:
                self.date_rules[col]["format"] = format_code

    def add_cluster_column(self, column_name):
        self.cluster_columns.append(column_name)
        self.non_cluster_columns.remove(column_name)

    def remove_cluster_col(self, column_name):
        self.cluster_columns.remove(column_name)
        self.non_cluster_columns.append(column_name)

    def add_denial_constraint(self, denial_constraint_id):
        if denial_constraint_id not in self.dc_ids_selected:
            self.dc_ids_selected.append(denial_constraint_id)

    def remove_denial_constraint(self, denial_constraint_id):
        if denial_constraint_id in self.dc_ids_selected:
            self.dc_ids_selected.remove(denial_constraint_id)

    def add_unique_constraint(self, unique_constraint):
        self.unique_constraint_counter += 1
        self.unique_constraints[self.unique_constraint_counter] = unique_constraint
        return self.unique_constraint_counter

    def delete_unique_constraint(self, dc_id):
        try:
            del self.unique_constraints[dc_id]
        except KeyError:
            print("Could not remove unique constraint with id", dc_id)
            return

    def get_outlier_info(self):
        outlier_ranges = {}
        for col in self.outlier_detection:
            od = self.outlier_detection[col]
            if col in self.date_columns:
                outlier_ranges[col] = {"min": od.interval[0],
                                       "max": od.interval[1],
                                       "action": self.outlier_detection[col].action.value}
            else:
                outlier_ranges[col] = {"min": round(od.interval[0], 2),
                                       "max": round(od.interval[1], 2),
                                       "action": self.outlier_detection[col].action.value}
        return outlier_ranges

    def change_outlier_interval(self, column_name, type, min_value=None, max_value=None):
        if column_name in self.outlier_detection:
            outlier_detect = self.outlier_detection[column_name]
            if type == "number":
                if min_value and not max_value:
                    old_interval = outlier_detect.interval
                    if min_value < old_interval[1]:
                        outlier_detect.interval = (min_value, old_interval[1])
                elif max_value and not min_value:
                    old_interval = outlier_detect.interval
                    if old_interval[0] <= max_value:
                        outlier_detect.interval = (old_interval[0], max_value)
            else:  # date
                if min_value and not max_value:
                    old_max = datetime.strptime(outlier_detect.interval[1], '%Y-%m-%d')
                    new_min = datetime.strptime(min_value, '%Y-%m-%d')
                    if new_min <= old_max:
                        outlier_detect.interval = (min_value, outlier_detect.interval[1])
                elif max_value and not min_value:
                    old_min = datetime.strptime(outlier_detect.interval[0], '%Y-%m-%d')
                    new_max = datetime.strptime(max_value, '%Y-%m-%d')
                    if old_min <= new_max:
                        outlier_detect.interval = (outlier_detect.interval[0], max_value)

    def change_on_outlier_detect_action(self, action, column=None):
        if column:
            if column in self.outlier_detection:
                od = self.outlier_detection[column]
                od.set_action(action)

        else:
            for column in self.outlier_detection:
                self.outlier_detection[column].set_action(action)

    def change_on_null_detect_action(self, action, column=None):
        if column:
            if (column in self.on_null_detection) and (action in set([action.value for action in OnNullValue])):
                self.on_null_detection[column] = OnNullValue(action)

        elif action in set([action.value for action in OnNullValue]):
            for column in self.on_null_detection:
                self.on_null_detection[column] = OnNullValue(action)

    def get_selected_denial_constraints(self):
        result = []
        for dc in self.denial_constraints:
            if dc['id'] in self.dc_ids_selected:
                result.append(dc)
        return result

    def select_functional_dependency(self, fd_id, checked):
        for fd in self.functional_dependency_discovery.functional_dependencies:
            if fd.id == fd_id:
                fd.checked = checked
                break
