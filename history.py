import sqlite3
import os
import sys


class History:
    def __init__(self):
        self.script_path = os.path.dirname(os.path.realpath(__file__))
        self.db_file = os.path.join(self.script_path, 'istoric.db')
        self.conn = sqlite3.connect(self.db_file)
        c = self.conn.cursor()
        sql = "create table if not exists istoric(id_meci VARCHAR(20) PRIMARY KEY NOT NULL, home_team VARCHAR(30) NOT NULL, away_team VARCHAR(30) NOT NULL, fh_ht_score integer NOT NULL, fh_at_score integer NOT NULL, sh_ht_score integer NOT NULL, sh_at_score integer NOT NULL)"
        c.execute(sql)
        c.close()
        self.conn.close()
        self.conn = sqlite3.connect(self.db_file)

    def get_match(self, id_meci):
        sql = "select home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score from istoric where id_meci = '%s' " % (id_meci)
        cursor = self.conn.execute(sql)
        row = cursor.fetchone()
        if row is None:
            return None
        return [row[i] for i in range(6)]

    def add_match(self, id_meci, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score):
        sql = "insert into istoric(id_meci, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score) VALUES ('%s', '%s', '%s', %d, %d, %d, %d)" % (
        id_meci, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score)
        print(sql)
        try:
            cursor = self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e.__traceback__)
            print(e.args)
        try:
            cursor.close()
        except:
            pass

    def get_matches(self, id_list):
        if not isinstance(id_list, list):
            raise Exception('get_matches - Vreau o lista de ID-uri!')
        result = []
        for id_match in id_list:
            rez = self.get_match(id_match)
            if rez is not None:
                result.append(rez)
        return result

db_history = History()
