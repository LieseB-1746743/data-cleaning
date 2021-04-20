from flask import Flask, render_template, request, url_for, redirect
from data_cleaning.cleaningmodules import tables, tablenames, foreign_keys, global_settings
from data_cleaning.cleaningmodules.date_format_codes import format_codes
from data_cleaning.cleaningmodules.clean_table import clean_table
app = Flask(__name__)
import traceback
import sys
import getopt


@app.route('/', methods=["GET"])
def index():
    if request.method == "GET":
        return redirect(url_for("foreignkeys"))


@app.route('/properties/<string:tablename>', methods=["GET", "POST"])
def properties(tablename):
    if tablename in tables:
        table = tables[tablename]
        if request.method == "GET":
            properties = table.get_characteristics()
            outlier_detection = table.rules.get_outlier_info()
            on_null_detect = {k: v.value for k, v in table.rules.on_null_detection.items()}
            return render_template("properties.html", tablenames=tablenames, tablename=tablename,
                                   properties=properties, outlier_detection=outlier_detection,
                                   on_null_detect=on_null_detect, date_rules=table.rules.date_rules,
                                   date_format_codes=format_codes), 200
        elif request.method == "POST":
            if request.json["settingname"] == "outlieraction":
                action = int(request.json["action"])
                column = request.json["column"]
                table.rules.change_on_outlier_detect_action(action=action, column=column)
            elif request.json["settingname"] == "outlierrange-min":
                min = request.json["min"]
                if request.json["type"] == "number":
                    min = float(min)
                column = request.json["column"]
                table.rules.change_outlier_interval(column, type=request.json["type"], min_value=min)
            elif request.json["settingname"] == "outlierrange-max":
                max = request.json["max"]
                if request.json["type"] == "number":
                    max = float(max)
                column = request.json["column"]
                table.rules.change_outlier_interval(column, type=request.json["type"], max_value=max)
            elif request.json["settingname"] == "nullaction":
                action = int(request.json["action"])
                column = request.json["column"]
                table.rules.change_on_null_detect_action(action, column)
            elif request.json["settingname"] == "futuredateaction":
                action = int(request.json["action"])
                column = request.json["column"]
                table.rules.change_on_future_date_detect_action(action=action, column=column)
            elif request.json["settingname"] == "date-format":
                format = int(request.json["format"])
                column = request.json["column"]
                table.rules.change_date_format(format, column)
        return '', 200
    else:
        return "", 404


@app.route('/rules/<string:tablename>', methods=["GET"])
def rules(tablename):
    if tablename in tables:
        table = tables[tablename]
        foreignkeys = foreign_keys.to_list_of_dicts()
        foreignkeys = [fk for fk in foreignkeys if fk['from_table'] == tablename]
        clusters = {col: clustering.get_clusters_as_dictionaries() for col, clustering in table.clusters.items()}
        functional_dependencies = table.rules.functional_dependency_discovery.functional_dependencies
        return render_template("rules.html", tablenames=tablenames, tablename=tablename,
                               columns=table.columns, clustercolumns=table.rules.cluster_columns,
                               nonclustercolumns=table.rules.non_cluster_columns,
                               denialconstraints=table.rules.denial_constraints,
                               selected_dc=table.rules.dc_ids_selected,
                               foreign_keys=foreignkeys, uniqueconstraints=table.rules.unique_constraints,
                               clusters=clusters, filter_percentage=100,
                               functional_dependencies=functional_dependencies,
                               fds_enabled=global_settings.enable_fds), 200
    else:
        return "", 404


@app.route('/setclustercolumns/<string:tablename>', methods=["POST"])
def setclustercolumns(tablename):
    try:
        if tablename in tables:
            table = tables[tablename]
            if request.json['checked']:
                table.rules.add_cluster_column(request.json['column'])
            else:
                table.rules.remove_cluster_col(request.json['column'])
        return "", 200
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/setclusterselect/<string:tablename>/<string:column>', methods=["POST"])
def setclusterselect(tablename, column):
    try:
        if tablename in tables:
            table = tables[tablename]
            cluster_rules = table.clusters
            if column in cluster_rules:
                clustering = cluster_rules[column]
                cluster_id = request.json['id']
                selected = request.json['checked']
                clustering.select_cluster_with_id(cluster_id, selected)
        return "", 200
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/setclusterreplaceby/<string:tablename>/<string:column>', methods=["POST"])
def setclusterreplaceby(tablename, column):
    try:
        if tablename in tables:
            table = tables[tablename]
            cluster_rules = table.clusters
            if column in cluster_rules:
                clustering = cluster_rules[column]
                cluster_id = request.json['id']
                new_value = request.json['replaceby']
                clustering.change_replaceby(cluster_id, new_value)
        return "", 200
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/splitcluster/<string:tablename>/<string:column>', methods=["POST"])
def splitcluster(tablename, column):
    try:
        if tablename in tables:
            table = tables[tablename]
            cluster_rules = table.clusters
            if column in cluster_rules:
                clustering = cluster_rules[column]
                cluster_id = request.json['clusterid']
                strings = request.json['strings']
                new_cluster = clustering.split_cluster(int(cluster_id), strings)
                return new_cluster, 200
        return "", 404
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/setdenialconstraint/<string:tablename>',  methods=["POST"])
def setdenialconstraint(tablename):
    try:
        if tablename in tables:
            table = tables[tablename]
            dc_id = request.json['id']
            if request.json['checked']:
                table.rules.add_denial_constraint(int(dc_id))
            else:
                table.rules.remove_denial_constraint(int(dc_id))
        return "", 200
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/cluster/<string:tablename>', methods=["GET"])
def cluster(tablename):
    try:
        if tablename in tables:
            table = tables[tablename]
            table.cluster_all_columns()
            return "", 200
        else:
            return "Table does not exist", 404
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/foreignkeys', methods=["GET"])
def foreignkeys():
    try:
        return render_template('foreignkeys.html',  tablenames=tablenames,
                               foreign_keys=foreign_keys.to_list_of_dicts()), 200
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/setforeignkey', methods=["POST"])
def setforeignkey():
    try:
        # print(int(request.json['id']), request.json['checked'])
        foreign_keys.select_foreign_key(int(request.json['id']), request.json['checked'])
        return "", 200
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/uniqueconstraint/<string:tablename>', methods=["POST"])
def add_or_delete_unique_constraint(tablename):
    try:
        if tablename in tables:
            table = tables[tablename]
            if request.json["action"] == "add":
                columns = request.json["data"]
                newID = table.rules.add_unique_constraint(columns)
                return str(newID), 200
            elif request.json["action"] == "delete":
                id = int(request.json["id"])
                table.rules.delete_unique_constraint(id)
                return '', 200
        else:
            return "Table does not exist", 404
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/setfunctionaldependency/<string:tablename>', methods=["POST"])
def setfunctionaldependency(tablename):
    try:
        if tablename in tables:
            table = tables[tablename]
            fd_id = int(request.json["id"])
            checked = request.json["checked"]
            print("Functional dependency with id", fd_id, ":", checked)
            table.rules.select_functional_dependency(fd_id, checked)
            return '', 200
        else:
            return "Table does not exist", 404
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/settings', methods=["GET", "POST"])
def settings():
    if request.method == "GET":
        return render_template('settings.html', tablenames=tablenames,
                               on_outlier_detect=global_settings.on_outlier_detect.value,
                               on_duplicate_detect=global_settings.on_duplicate_detect.value,
                               on_null_detect=global_settings.on_null_detect.value,
                               on_future_date_detect=global_settings.on_future_date_detect.value,
                               on_fk_violation=global_settings.on_foreign_key_violation.value,
                               on_dc_violation=global_settings.on_denial_constraint_violation.value,
                               on_fd_violation=global_settings.on_functional_dependency_violation.value,
                               date_format_codes=format_codes, date_format=global_settings.date_format_code,
                               fds_enabled=global_settings.enable_fds), 200
    elif request.method == "POST":
        try:
            if request.json["settingname"] == "outlieraction":
                action = int(request.json["action"])
                global_settings.set_outlier_action(action)
                for table_name in tables:
                    tables[table_name].rules.change_on_outlier_detect_action(action=action)
            elif request.json["settingname"] == "duplicateaction":
                action = int(request.json["action"])
                global_settings.set_duplicate_action(action)
            elif request.json["settingname"] == "nullaction":
                action = int(request.json["action"])
                global_settings.set_null_action(action)
                for table_name in tables:
                    tables[table_name].rules.change_on_null_detect_action(action)
            elif request.json["settingname"] == "futuredateaction":
                action = int(request.json["action"])
                global_settings.set_on_future_date_action(action)
                for table_name in tables:
                    tables[table_name].rules.change_on_future_date_detect_action(action)
            elif request.json["settingname"] == "foreignkeyaction":
                action = int(request.json["action"])
                global_settings.set_on_foreign_key_violation_action(action)
            elif request.json["settingname"] == "denialconstraintaction":
                action = int(request.json["action"])
                global_settings.set_on_denial_constraint_violation_action(action)
            elif request.json["settingname"] == "functionaldependencyaction":
                action = int(request.json["action"])
                global_settings.set_on_functional_dependency_violation_action(action)
            elif request.json["settingname"] == "dateformat":
                format = int(request.json["format"])
                global_settings.set_date_format_code(format)
                for table_name in tables:
                    tables[table_name].rules.change_date_format(format)
            return "", 200
        except Exception as e:
            print(e)
            return str(e), 500


@app.route('/clean/<string:tablename>', methods=["GET"])
def clean(tablename):
    try:
        if tablename in tables:
            table = tables[tablename]
            clean_table(global_settings, foreign_keys, table)
            return "Successfully cleaned table", 200
        else:
            return "Table does not exist", 404
    except Exception as e:
        print(e)
        traceback.print_exc()
        return str(e), 500


port = 5000
options, remainder = getopt.getopt(sys.argv[1:], "p:", ["port=", "enable-functional-dependencies"])
for opt, arg in options:
    if opt in ('-p', '--port'):
        port = int(arg)
    if opt in ['--enable-functional-dependencies']:
        print("Discovering functional dependencies...")
        for tablename in tablenames:
            tables[tablename].rules.functional_dependency_discovery.calc_fds()
        global_settings.enable_fds=True
        global_settings.set_on_functional_dependency_violation_action(1)  # flag

app.run(debug=False, port=port)
