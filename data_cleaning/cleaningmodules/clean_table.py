from .actions import OnForeignKeyViolation, OnDenialConstraintViolation, OnNullValue, OnFutureDate, OnDuplicateDetect, \
    OnOutlierDetect, OnFunctionalDependencyViolation
from .date_format_codes import format_codes
import numpy as np
import pandas as pd
from datetime import datetime
import os


def clean_table(settings, foreign_keys, table):
    print("START CLEANING TABLE " + table.name)
    df_to_clean = table.df.copy()
    cleaned_df = clean_foreign_keys(settings.on_foreign_key_violation, table.name, df_to_clean, foreign_keys)
    cleaned_df = clean_denial_constraints(settings.on_denial_constraint_violation, table, cleaned_df)
    cleaned_df = clean_functional_dependencies(settings.on_functional_dependency_violation, table, cleaned_df)
    cleaned_df = clean_dates(table, cleaned_df)
    cleaned_df = clean_duplicates(settings.on_duplicate_detect, table, cleaned_df)
    cleaned_df = clean_outliers(table, cleaned_df)
    cleaned_df = clean_null_values(table, cleaned_df)
    cleaned_df = clean_clustered_columns(table, cleaned_df)

    path = table.path
    cleaned_at = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    filename = table.name + "_CLEANED_" + cleaned_at + ".csv"
    path_and_filename = os.path.join(path, filename)
    cleaned_df.to_csv(path_and_filename, index=False)
    print("FINISHED CLEANING TABLE: saving cleaned table to " + path_and_filename)


def clean_foreign_keys(on_fk_violation_action, table_name, df, foreign_keys):
    if on_fk_violation_action == OnForeignKeyViolation.IGNORE:
        return df

    try:
        df_copy = df.copy()
        fks = foreign_keys.get_fks_with_violations(table_name)

        if len(fks) == 0:
            if on_fk_violation_action == OnForeignKeyViolation.FLAG:
                df_copy["FOREIGN_KEY_VIOLATION"] = False
                df_copy["FOREIGN_KEY_VIOLATION_INFO"] = ""
            return df_copy

        if on_fk_violation_action == OnForeignKeyViolation.FLAG:
            flag = pd.Series(np.full(len(df_copy.index), False), index=df_copy.index)
            flag_message = pd.Series([''] * len(df_copy.index), index=df_copy.index)
            for fk in fks:
                merged_list = fk.merged_list
                column = fk.from_column
                new_flag = ~df_copy[column].isin(merged_list)
                flag = flag.where(flag, new_flag)
                new_message = "value in column " + column + " does not exist in column " + fk.to_column + " in table " + \
                              fk.to_table + ";"
                flag_message = flag_message.where(~new_flag, (flag_message + new_message))

            df_copy["FOREIGN_KEY_VIOLATION"] = flag
            df_copy["FOREIGN_KEY_VIOLATION_INFO"] = flag_message

        elif on_fk_violation_action == OnForeignKeyViolation.REMOVE_ROW:
            df_cleaned = df_copy.copy()
            for fk in fks:
                merged_list = fk.merged_list
                column = fk.from_column
                df_cleaned = df_cleaned.loc[(df_cleaned[column].isin(merged_list)) | (df_cleaned[column].isna())]
            df_copy = df_cleaned

        print("/t Successfully cleaned foreign key violations.")
        return df_copy
    except Exception as e:
        print("/t ERROR while cleaning foreign key violations:" + str(e))
        return df


def clean_denial_constraints(on_dc_violation_action, table, df):
    if on_dc_violation_action == OnDenialConstraintViolation.IGNORE:
        return df

    try:
        df_copy = df.copy()
        denial_constraints = table.rules.get_selected_denial_constraints()

        flag = pd.Series(np.full(len(df_copy.index), False), index=df_copy.index)
        flag_message = pd.Series([''] * len(df_copy.index), index=df_copy.index)
        for dc in denial_constraints:
            percentage_valid = dc["percentage"]
            if percentage_valid < 100:
                small_column = dc["small_column"]
                big_column = dc["big_column"]
                new_flag = df_copy[small_column] > df_copy[big_column]
                flag = flag.where(flag, new_flag)
                new_message = small_column + " > " + big_column + ";"
                flag_message = flag_message.where(~new_flag, flag_message + new_message)

        if on_dc_violation_action == OnDenialConstraintViolation.FLAG:
            df_copy["SMALLER_THAN_VIOLATION"] = flag
            df_copy["SMALLER_THAN_VIOLATION_INFO"] = flag_message
        elif on_dc_violation_action == OnDenialConstraintViolation.REMOVE_ROW:
            df_copy = df_copy.loc[~flag]
        print("/t Successfully cleaned <= constraint violations.")
        return df_copy

    except Exception as e:
        print("/t ERROR while cleaning <= constraint violations:" + str(e))
        return df


def clean_functional_dependencies(on_fd_violation_action, table, df):
    if on_fd_violation_action == OnFunctionalDependencyViolation.IGNORE:
        return df

    try:
        df_copy = df.copy()
        fds = table.rules.functional_dependency_discovery.functional_dependencies
        flag = pd.Series(np.full(len(df_copy.index), False), index=df_copy.index)
        flag_message = pd.Series([''] * len(df_copy.index), index=df_copy.index)

        for fd in fds:
            df_sub = df_copy.groupby(fd.lhs, sort=False)[fd.rhs]
            df_sub = df_sub.nunique()
            df_sub = df_sub.loc[df_sub > 1]
            lhs_with_violations = list(df_sub.index)
            new_flag = df_copy[fd.lhs].isin(lhs_with_violations)
            new_flag = new_flag.iloc[:, 0]
            flag = flag.where(flag, new_flag)
            new_message = "violation on rule " + str(fd.lhs) + " -> " + str(fd.rhs)
            flag_message = flag_message.where(~flag, flag_message + new_message)

        if on_fd_violation_action == OnFunctionalDependencyViolation.FLAG:
            df_copy["FUNCTIONAL_DEPENDENCY_VIOLATION"] = flag
            df_copy["FUNCTIONAL_DEPENDENCY_VIOLATION_INFO"] = flag_message
        elif on_fd_violation_action == OnFunctionalDependencyViolation.REMOVE_ROW:
            df_copy = df_copy.loc[~flag]

        print("/t Successfully cleaned functional dependency violations.")
        return df_copy

    except Exception as e:
        print("/t ERROR while cleaning functional dependency violations:" + str(e))
        return df


# def clean_functional_dependencies(on_fd_violation_action, table, df):
#     if on_fd_violation_action == OnFunctionalDependencyViolation.IGNORE:
#         return df
#
#     fds = table.rules.functional_dependency_discovery.functional_dependencies
#     flag = pd.Series(np.full(len(df.index), False), index=df.index)
#     flag_message = pd.Series([''] * len(df.index), index=df.index)
#
#     for fd in fds:
#         new_message = "violation on " + str(fd.lhs) + " -> " + str(fd.rhs)
#         df_sub = df.groupby(fd.lhs, sort=False)[fd.rhs]
#         df_sub = df_sub.nunique()
#         df_sub = df_sub.loc[df_sub > 1]
#         lhs_with_violations = list(df_sub.index)
#         for lhs in lhs_with_violations:
#             for l in fd.lhs:
#                 df_sub = df.loc[df[l] == lhs]
#             max = df_sub[fd.rhs].value_counts().index[0]
#             violations = df_sub.loc[df_sub[fd.rhs] != max]
#             new_flag = pd.Series(df.index.isin(list(violations.index)))
#             flag = flag.where(flag, new_flag)
#             flag_message = flag_message.where(~flag, flag_message + new_message)
#
#     if on_fd_violation_action == OnFunctionalDependencyViolation.FLAG:
#         df["FUNCTIONAL_DEPENDENCY_VIOLATION"] = flag
#         df["FUNCTIONAL_DEPENDENCY_VIOLATION_INFO"] = flag_message
#     elif on_fd_violation_action == OnFunctionalDependencyViolation.REMOVE_ROW:
#         df = df.loc[~flag]
#
#     return df


def clean_null_values(table, df):
    try:
        null_rules = table.rules.on_null_detection

        df_copy = df.copy()
        for col in null_rules:  # first, remove rows that need to be removed
            if null_rules[col] == OnNullValue.REMOVE_ROW:
                df_copy.dropna(inplace=True, subset=[col])

        flag = pd.Series(np.full(len(df_copy.index), False), index=df_copy.index)
        flag_message = pd.Series([''] * len(df_copy.index), index=df_copy.index)
        flag_activated = False
        for col in null_rules:  # then, check for flags
            if null_rules[col] == OnNullValue.FLAG:
                flag_activated = True
                new_flag = df_copy[col].isna()
                flag = flag.where(flag, new_flag)
                new_message = col + " is NULL;"
                flag_message = flag_message.where(~new_flag, flag_message + new_message)

        if flag_activated:
            df_copy["NULL_FLAG"] = flag
            df_copy["NULL_FLAG_INFO"] = flag_message

        print("/t Successfully cleaned NULL values.")
        return df_copy

    except Exception as e:
        print("/t ERROR while cleaning NULL values:" + str(e))
        return df


def clean_dates(table, df):
    try:
        date_rules = table.rules.date_rules
        df_copy = df.copy()

        for col in date_rules:  # first, remove rows that need to be removed
            if date_rules[col]["action"] == OnFutureDate.REMOVE_ROW:
                df_copy = df_copy.loc[(df_copy[col] <= datetime.now()) | (df_copy[col].isna())]

        for col in date_rules:  # then, set null
            if date_rules[col]["action"] == OnFutureDate.SET_NULL:
                df_copy.loc[df_copy[col] > datetime.now(), col] = None

        flag = pd.Series(np.full(len(df_copy.index), False), index=df_copy.index)
        flag_message = pd.Series([''] * len(df_copy.index), index=df_copy.index)
        flag_activated = False
        for col in date_rules:  # then, check for flags
            if date_rules[col]["action"] == OnFutureDate.FLAG:
                flag_activated = True
                new_flag = df_copy[col] > datetime.now()
                flag = flag.where(flag, new_flag)
                new_message = col + " is a date in the future;"
                flag_message = flag_message.where(~new_flag, flag_message + new_message)

            # format date strings
            format_nr = date_rules[col]["format"]
            format_str = format_codes[format_nr]["format"]
            df_copy[col] = df_copy[col].dt.strftime(format_str)

        if flag_activated:
            df_copy["FUTURE_DATE_FLAG"] = flag
            df_copy["FUTURE_DATE_FLAG_INFO"] = flag_message
        print("/t Successfully cleaned future dates.")
        return df_copy

    except Exception as e:
        print("/t ERROR while cleaning future dates:" + str(e))
        return df


def clean_duplicates(on_duplicate_action, table, df):
    if on_duplicate_action == OnDuplicateDetect.IGNORE:
        return df

    try:
        unique_constraints = table.rules.unique_constraints
        df_copy = df.copy()

        if on_duplicate_action == OnDuplicateDetect.REMOVE_ALL or \
                on_duplicate_action == OnDuplicateDetect.REMOVE_EXCEPT_FIRST:
            for uc_id in unique_constraints:
                list_of_columns = unique_constraints[uc_id]
                if on_duplicate_action == OnDuplicateDetect.REMOVE_ALL:
                    df_copy.drop_duplicates(inplace=True, subset=list_of_columns, keep=False)
                else:  # REMOVE_EXCEPT_FIRST
                    df_copy.drop_duplicates(inplace=True, subset=list_of_columns, keep='first')

        elif on_duplicate_action == OnDuplicateDetect.FLAG_ALL or \
                on_duplicate_action == OnDuplicateDetect.FLAG_EXCEPT_FIRST:
            flag = pd.Series(np.full(len(df_copy.index), False), index=df_copy.index)
            flag_message = pd.Series([''] * len(df_copy.index), index=df_copy.index)
            flag_activated = False

            for uc_id in unique_constraints:
                list_of_columns = unique_constraints[uc_id]
                if on_duplicate_action == OnDuplicateDetect.FLAG_ALL:
                    flag_activated = True
                    new_flag = df_copy.duplicated(subset=list_of_columns, keep=False)
                    flag = flag.where(flag, new_flag)
                    new_message = "combination of columns " + str(list_of_columns) + " is not unique;"
                    flag_message = flag_message.where(~new_flag, flag_message + new_message)
                elif on_duplicate_action == OnDuplicateDetect.FLAG_EXCEPT_FIRST:
                    flag_activated = True
                    new_flag = df_copy.duplicated(subset=list_of_columns, keep='first')
                    flag = flag.where(flag, new_flag)
                    new_message = "combination of columns " + str(list_of_columns) + " is not unique;"
                    flag_message = flag_message.where(~new_flag, flag_message + new_message)

            if flag_activated:
                df_copy["DUPLICATE_FLAG"] = flag
                df_copy["DUPLICATE_FLAG_MESSAGE"] = flag_message

        print("/t Successfully cleaned duplicates (unique constraint violations).")
        return df_copy

    except Exception as e:
        print("/t ERROR while cleaning duplicates (unique constraint violations):" + str(e))
        return df


def clean_outliers(table, df):
    try:
        outlier_detection = table.rules.outlier_detection
        df_copy = df.copy()

        # FIRST: REMOVE_ROW
        for col in outlier_detection:
            od = outlier_detection[col]
            if od.action == OnOutlierDetect.REMOVE_ROW:
                interval = od.interval
                df_copy = df_copy.loc[
                    ((df_copy[col] >= interval[0]) & (df_copy[col] <= interval[1])) | (df_copy[col].isna())]

        # THEN: SET NULL
        for col in outlier_detection:
            od = outlier_detection[col]
            if od.action == OnOutlierDetect.SET_NULL:
                interval = od.interval
                df_copy.loc[((df_copy[col] < interval[0]) | (df_copy[col] > interval[1])), col] = None

        # THEN: FLAG
        flag = pd.Series(np.full(len(df_copy.index), False), index=df_copy.index)
        flag_message = pd.Series([''] * len(df_copy.index), index=df_copy.index)
        flag_activated = False
        for col in outlier_detection:
            od = outlier_detection[col]
            if od.action == OnOutlierDetect.FLAG:
                flag_activated = True
                interval = od.interval
                new_flag = ((df_copy[col] < interval[0]) | (df_copy[col] > interval[1]))
                flag = flag.where(flag, new_flag)
                new_message = col + " < " + str(interval[0]) + " or " + col + " > " + str(interval[1])
                flag_message = flag_message.where(~new_flag, flag_message + new_message)

        if flag_activated:
            df_copy["OUTLIER_FLAG"] = flag
            df_copy["OUTLIER_FLAG_INFO"] = flag_message

        print("/t Successfully cleaned outliers.")
        return df_copy

    except Exception as e:
        print("/t ERROR while cleaning outliers:" + str(e))
        return df


def clean_clustered_columns(table, df):
    try:
        df_copy = df.copy()
        cluster_results = table.clusters

        for col in cluster_results:
            clustering = cluster_results[col]
            clusters = clustering.get_selected_clusters()
            for cluster in clusters:
                new_value = cluster.replaceby
                values_to_replace = cluster.get_strings_in_cluster()
                df_copy.loc[df_copy[col].isin(values_to_replace), col] = new_value

        print("/t Successfully cleaned clustered columns.")
        return df_copy

    except Exception as e:
        print("/t ERROR while cleaning clustered columns:" + str(e))
        return df
