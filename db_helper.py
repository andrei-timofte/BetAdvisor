import sqlite3
import os
import sys

from constants import *


class DBInterface:
    def __init__(self, db_file_name: str, table_name: str, columns: dict, primary_key: str,
                 create_only_if_not_exists=True):
        """
        Initializeaza o instanta specifica unei anumite baza de date.
        :param db_file_name: numele fisierului .db care va fi creat in path-ul scriptului
        :param table_name: numele tabelului din baza de date
        :param columns: o lista de tuple cau valorile (column_name, column_type)
        :param primary_key_index: indica acea coloana care reprezinta primary key
        :param create_only_if_not_exists: True daca nu se vrea rescrierea tabelei in cazul in care aceasta exista
        """
        self.db_file_name = db_file_name.split('.')[0]
        self.table_name = table_name
        self.primary_key = primary_key
        self.script_path = os.path.dirname(os.path.realpath(__file__))
        self.db_file = os.path.join(self.script_path, db_file_name)
        self.conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = self.conn.cursor()
        sql = self._construct_sql_statement(Constants.StatementTypes.CREATE_STATEMENT,
                                            columns,
                                            create_only_if_not_exists)
        c.execute(sql)
        c.close()
        self.conn.close()

    def _construct_sql_statement(self, statement_type: int, values: dict, create_if_not_exists=True):
        if statement_type == Constants.StatementTypes.CREATE_STATEMENT:
            sql = "create table " + ("if not exists " if create_if_not_exists else "") + self.table_name + "("
            for col_name, col_type in values.items():
                sql += col_name + " " + col_type + ", "
            return sql[:-2] + ")"
        elif statement_type == Constants.StatementTypes.INSERT_STATEMENT:
            keys = list(values.keys())
            vals = [values[keys[x]] for x in range(len(keys))]
            vals_str = ""
            for val in vals:
                if isinstance(val, int):
                    vals_str += "{},".format(val)
                else:
                    vals_str += "'{}',".format(val)
            vals_str = vals_str[:-1]
            sql = "insert into %s (%s) values (%s)" % (self.table_name, str(",".join(keys)), vals_str)
            return sql
        elif statement_type == Constants.StatementTypes.UPDATE_STATEMENT:
            sql = "update " + self.table_name + " set "
            keys = list(values.keys())
            vals = [values[keys[x]] for x in range(len(keys))]
            pk = 0
            expression = ""
            for i in range(len(keys)):
                if keys[i] != self.primary_key:
                    if isinstance(vals[i], int):
                        expression += "{} = {}, ".format(keys[i], vals[i])
                    else:
                        expression += "{} = '{}', ".format(keys[i], vals[i])
                else:
                    pk = i
            if isinstance(vals[pk], int):
                sql += (expression[:-2] if len(expression) > 2 else "") + " where {}={}".format(self.primary_key, vals[pk])
            else:
                sql += (expression[:-2] if len(expression) > 2 else "") + " where {}='{}'".format(self.primary_key, vals[pk])
            return sql
        elif statement_type == Constants.StatementTypes.DELETE_STATEMENT:
            if isinstance(values[list(values.keys())[0]], int):
                return "delete from {} where {} = {}".format(self.table_name, list(values.keys())[0], values[list(values.keys())[0]])
            return "delete from {} where {} = '{}'".format(self.table_name, list(values.keys())[0], values[list(values.keys())[0]])

    def get_records(self, record_name, record_id):
        if isinstance(record_id, int):
            sql = "select * from %s where %s = %d" % (self.table_name, record_name, record_id)
        else:
            sql = "select * from %s where %s = '%s'" % (self.table_name, record_name, record_id)

        self.conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = self.conn.execute(sql)
        results = []
        for row in cursor:
            results.append([x for x in row])
        cursor.close()
        self.conn.close()
        results.sort(key=lambda x: x[0])
        return results

    def record_exists(self, record_value, record_name=None, json_must_exist=True):
        if record_name is None:
            record_name = self.primary_key
        record = self.get_records(record_name, record_value)
        if len(record) < 1:
            return False
        if not json_must_exist:
            return True
        if not os.path.isfile('data\\{}'.format(record[0][5])):
            return False
        return True

    def insert_record(self, values: dict, update_if_exists=True, json_must_exist=True):
        """

        :param values: un dictionar cu coloanele si valorile acestora
        :param update_if_exists: Bool. Daca se doreste actualizarea datelor in cazul in care exista deja
        :param json_must_exist: Se trimite mai departe la verificarea existentei datelor. Ar trebui sa fie False in
                                algoritmi
        :return: None
        """
        if self.primary_key not in values.keys():
            return
        if not self.record_exists(values[self.primary_key], json_must_exist=json_must_exist):
            sql = self._construct_sql_statement(Constants.StatementTypes.INSERT_STATEMENT, values)
            print(sql)
            self.conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = self.conn.execute(sql)
            self.conn.commit()
            cursor.close()
            self.conn.close()
        elif update_if_exists:
            sql = self._construct_sql_statement(Constants.StatementTypes.UPDATE_STATEMENT, values)
            print(sql)
            self.conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = self.conn.execute(sql)
            self.conn.commit()
            cursor.close()
            self.conn.close()

    def delete_record(self, record_value, record_name=None):
        if record_name is None:
            record_name = self.primary_key
        sql = self._construct_sql_statement(Constants.StatementTypes.DELETE_STATEMENT, {record_name: record_value})
        print(sql)
        self.conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = self.conn.execute(sql)
        self.conn.commit()
        cursor.close()
        self.conn.close()
#
#
#
#     def record_exists(self):
#         return
#
#         c = self.conn.cursor()
#         sql = create_statement
#         c.execute(sql)
#         c.close()
#         self.conn.close()
#         self.conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
#
#     def create_table(self, table_name, create_statement, ):
#         sql = "create table if not exists meciuri (id_meci integer PRIMARY KEY NOT NULL, competitie VARCHAR(30) NOT NULL, home_team VARCHAR(30) NOT NULL, away_team VARCHAR(30) NOT NULL, data_meci DATE NOT NULL)"
#
#     def get_record(self, selector):
#         sql = "select * from meciuri where id_meci = %d" % (id_meci)
#         cursor = self.conn.execute(sql)
#         results = []
#         for row in cursor:
#             results.append([x for x in row])
#         cursor.close()
#         results.sort(key=lambda x: x[0])
#         return results
#
#     def match_has_results(self, id_meci):
#         sql = "select * from meciuri where id_meci = %d" % (id_meci)
#         cursor = self.conn.execute(sql)
#         results = []
#         for row in cursor:
#             results.append([x for x in row])
#         return len(results) > 0
#
#     def add_match(self, id_meci, competitie, home_team, away_team, date):
#         if not self.match_has_results(id_meci):
#             sql = "insert into meciuri(id_meci, competitie, home_team, away_team, data_meci) VALUES (%d, '%s', '%s', '%s', '%s')" % (
#             id_meci, competitie, home_team, away_team, str(date))
#             print(sql)
#             cursor = self.conn.execute(sql)
#             self.conn.commit()
#             cursor.close()
#         else:
#             sql = "update meciuri set competitie = '%s', home_team = '%s', away_team = '%s', data_meci = %d where id_meci = %d" % (
#             competitie, home_team, away_team, date, id_meci)
#             print(sql)
#             cursor = self.conn.execute(sql)
#             self.conn.commit()
#             cursor.close()
#
#     def delete_match(self, id_meci):
#         if not self.match_has_results(id_meci):
#             return
#         sql = "delete from meciuri where id_meci = %d" % (id_meci)
#         print(sql)
#         cursor = self.conn.execute(sql)
#         self.conn.commit()
#         cursor.close()
#
#
# db_helper = DBInterface()
