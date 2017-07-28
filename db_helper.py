import sqlite3
import os
import sys


class DBHelper:
    def __init__(self):
        self.script_path = os.path.dirname(os.path.realpath(__file__))
        self.db_file = os.path.join(self.script_path, 'rezultate.db')
        self.conn = sqlite3.connect(self.db_file)
        c = self.conn.cursor()
        sql = "create table if not exists rezultate (id integer PRIMARY KEY NOT NULL, competitie VARCHAR(30) NOT NULL, runda integer, id_meci VARCHAR(20) UNIQUE NOT NULL, home_team VARCHAR(30) NOT NULL, away_team VARCHAR(30) NOT NULL, fh_ht_score integer NOT NULL, fh_at_score integer NOT NULL, sh_ht_score integer NOT NULL, sh_at_score integer NOT NULL)"
        c.execute(sql)
        c.close()
        self.conn.close()
        self.conn = sqlite3.connect(self.db_file)

    def get_all_team_results(self, competitie, echipa):
        sql = "select * from rezultate where competitie = '%s' and (home_team = '%s' or away_team = '%s') ORDER BY id" % (competitie, echipa, echipa)
        cursor = self.conn.execute(sql)
        results = []
        for row in cursor:
            results.append([x for x in row])
        cursor.close()
        results.sort(key=lambda x: x[2])
        return results

    def get_all_team_results_from_home(self, competitie, echipa):
        sql = "select * from rezultate where competitie = '%s' and home_team = '%s' ORDER BY id" % (competitie, echipa)
        cursor = self.conn.execute(sql)
        results = []
        for row in cursor:
            results.append([x for x in row])
        cursor.close()
        results.sort(key=lambda x: x[2])
        return results

    def get_all_team_results_from_away(self, competitie, echipa):
        sql = "select * from rezultate where competitie = '%s' and away_team = '%s' ORDER BY id" % (competitie, echipa)
        cursor = self.conn.execute(sql)
        results = []
        for row in cursor:
            results.append([x for x in row])
        cursor.close()
        results.sort(key=lambda x: x[2])
        return results

    def match_has_results(self, id_meci):
        sql = "select count(*) from rezultate where id_meci = '%s'" % (id_meci)
        cursor = self.conn.execute(sql)
        result = int(cursor.fetchone()[0])
        cursor.close()
        return 1 == result

    def add_match(self, competitie, runda, id_meci, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score):
        if not self.match_has_results(id_meci):
            sql = "insert into rezultate(competitie, runda, id_meci, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score) VALUES ('%s', %d, '%s', '%s', '%s', %d, %d, %d, %d)" % (competitie, runda, id_meci, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score)
            print(sql)
            cursor = self.conn.execute(sql)
            self.conn.commit()
            cursor.close()
        else:
            sql = "update rezultate set runda = %d, home_team = '%s', away_team = '%s', fh_ht_score = %d, fh_at_score = %d, sh_ht_score = %d, sh_at_score = %d where competitie = '%s' and id_meci = '%s'" % (runda, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score, competitie, id_meci)
            print(sql)
            cursor = self.conn.execute(sql)
            self.conn.commit()
            cursor.close()

    def get_competition_teams(self, competitie):
        results = []
        sql = "select distinct home_team from rezultate where competitie = '%s'" % competitie
        cursor = self.conn.execute(sql)
        for r in cursor:
            results.append(r[0])
        cursor.close()

        # Pentru cazul in care competitia este la inceput si o echipa a jucat doar in deplasare
        sql = "select distinct away_team from rezultate where competitie = '%s'" % competitie
        cursor = self.conn.execute(sql)
        for r in cursor:
            results.append(r[0])
        cursor.close()
        results = [x for x in set(results)]
        return sorted(results)

    def get_competition_all_matches(self, competitie):
        results = []
        sql = "select home_team, away_team, runda, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score from rezultate where competitie = '%s'" % competitie
        cursor = self.conn.execute(sql)
        for r in cursor:
            results.append([x for x in r])
        cursor.close()
        results.sort(key=lambda x: x[2])
        return results

    def set_year(self, year):
        # self.script_path = os.path.dirname(os.path.realpath(__file__))
        self.conn.close()
        self.db_file = os.path.join(self.script_path, 'rezultate_arhiva_{}.db'.format(year))
        self.conn = sqlite3.connect(self.db_file)
        c = self.conn.cursor()
        sql = "create table if not exists rezultate (id integer PRIMARY KEY NOT NULL, competitie VARCHAR(30) NOT NULL, runda integer, id_meci VARCHAR(20) UNIQUE NOT NULL, home_team VARCHAR(30) NOT NULL, away_team VARCHAR(30) NOT NULL, fh_ht_score integer NOT NULL, fh_at_score integer NOT NULL, sh_ht_score integer NOT NULL, sh_at_score integer NOT NULL)"
        c.execute(sql)
        c.close()
        self.conn.close()
        self.conn = sqlite3.connect(self.db_file)
        print('Am setat anul rezultatelor in DB ca fiind {} si baza de date va fi salvata in {}'.format(year, self.db_file))

    def reset_year(self):
        self.conn.close()
        self.db_file = os.path.join(self.script_path, 'rezultate.db')
        self.conn = sqlite3.connect(self.db_file)
        c = self.conn.cursor()
        sql = "create table if not exists rezultate (id integer PRIMARY KEY NOT NULL, competitie VARCHAR(30) NOT NULL, runda integer, id_meci VARCHAR(20) UNIQUE NOT NULL, home_team VARCHAR(30) NOT NULL, away_team VARCHAR(30) NOT NULL, fh_ht_score integer NOT NULL, fh_at_score integer NOT NULL, sh_ht_score integer NOT NULL, sh_at_score integer NOT NULL)"
        c.execute(sql)
        c.close()
        self.conn.close()
        self.conn = sqlite3.connect(self.db_file)
        print('Am resetat anul rezultatelor in DB si baza de date va fi salvata in {}'.format(self.db_file))


db_helper = DBHelper()
