import os
import json
import re
import copy

from db_helper import db_helper as db
from StatsProvider import StatsProvider


class Algorithm3C:

    def __init__(self, meciuri, path_for_logs):
        self.name = "PPG Difference Algorithm + Cote"
        self.description = """Acest algoritm ia doar meciurile de acasa pentru echipa ce urmeaza sa joace acasa si
        doar meciurile din deplasare pentru echipa ce urmeaza sa joace in deplasare. Se face acest lucru doarece performanta
        unei echipe intr-un meci depinde destul de mult de locul unde urmeaza sa joace (acasa sau in deplasare).
        Se cauta apoi cel mai slab adversar (cel mai mic PPGa) de la care echipa ce urmeaza sa joace acasa a luat bataie
        si cel mai slab adversar pe care l-a batut acasa. PPGa este cel curent, nu cel de la data meciului.
        Daca PPGa al echipei care urmeaza sa joace in deplasare este mai mic decat al celor doi cei mai slabi gasiti 
        anterior echipa ce joaca acasa se marcheaza ca posibila castigatoare.
        Se face acelasi lucru si pentru echipa ce urmeaza sa joace in deplasare cu singura dicerenta ca se cauta
        cei mai slabi adversari cu care s-a jucat in deplasare, nu acasa.
        Daca doar o echipa a fost marcata ca posibila castigatoare, aceea este sugerata pentru pariu (daca nici una
        sau ambele au fost marcate, nu este de ajutor prognoza).
        Diferenta fata de PPG Difference Algorithm consta in faptul ca acest algoritm ia in calcul si cotele echipelor.
        Daca echipa preconizata ca fiind castigatoare are cota mai mare decat adversara ei, nu va mai fi sugerata.
        """
        self.meciuri = meciuri
        self.path_for_logs = path_for_logs
        self.pattern = re.compile('[\W_]+', re.UNICODE)

    def analyze(self, competitie: str):
        """
        Calea pentru loguri se primeste la initializare pentru ca va fi aceeasi pentru fiecare thread.
        Meciurile se primesc sub forma de dictionar (json) la initializare intru cat nu se modifica in cursul analizei.
        :param competitie: Competitia de pe superbet
        :return: dict. Castigatorii pentru fiecare meci, sub forma de dictionar in care cheia va fi numarul meciului si valoarea va fi castigatorul preconizat
        """
        stats_provider = StatsProvider(competitie)

        winners = {competitie: {}}
        if competitie not in self.meciuri.keys():
            return winners

        for meci in self.meciuri[competitie]:
            home_team = self.meciuri[competitie][meci]["Home"]
            away_team = self.meciuri[competitie][meci]["Away"]
            home_team_matches = db.get_all_team_results_from_home(competitie, home_team)
            away_team_matches = db.get_all_team_results_from_away(competitie, away_team)

            home_team_max_won_ppga = 0  # Maxim poate fi 3 daca a castigat toate meciurile din deplasare
            home_team_min_won_ppga = 4  # Maxim poate fi 3 daca a castigat toate meciurile din deplasare
            home_team_max_lost_ppga = 0  # Maxim poate fi 3 daca a castigat toate meciurile din deplasare
            home_team_min_lost_ppga = 4  # Maxim poate fi 3 daca a castigat toate meciurile din deplasare

            for m in home_team_matches:
                stats_adversar = stats_provider.get_team_stats(m[5])
                if stats_adversar["Away"]["Total"]["PPG"] > 0:
                    if m[6] + m[8] > m[7] + m[9]:
                        if home_team_max_won_ppga < stats_adversar["Away"]["Total"]["PPG"]:
                            home_team_max_won_ppga = stats_adversar["Away"]["Total"]["PPG"]
                        if home_team_min_won_ppga > stats_adversar["Away"]["Total"]["PPG"]:
                            home_team_min_won_ppga = stats_adversar["Away"]["Total"]["PPG"]
                    if m[6] + m[8] < m[7] + m[9]:
                        if home_team_max_lost_ppga < stats_adversar["Away"]["Total"]["PPG"]:
                            home_team_max_lost_ppga = stats_adversar["Away"]["Total"]["PPG"]
                        if home_team_min_lost_ppga > stats_adversar["Away"]["Total"]["PPG"]:
                            home_team_min_lost_ppga = stats_adversar["Away"]["Total"]["PPG"]

            away_team_max_won_ppga = 0  # Maxim poate fi 3 daca a castigat toate meciurile din deplasare
            away_team_min_won_ppga = 4  # Maxim poate fi 3 daca a castigat toate meciurile din deplasare
            away_team_max_lost_ppga = 0  # Maxim poate fi 3 daca a castigat toate meciurile din deplasare
            away_team_min_lost_ppga = 4  # Maxim poate fi 3 daca a castigat toate meciurile din deplasare

            for m in away_team_matches:
                stats_adversar = stats_provider.get_team_stats(m[4])
                if stats_adversar["Home"]["Total"]["PPG"] > 0:
                    if m[7] + m[9] > m[6] + m[8]:
                        if away_team_max_won_ppga < stats_adversar["Home"]["Total"]["PPG"]:
                            away_team_max_won_ppga = stats_adversar["Home"]["Total"]["PPG"]
                        if away_team_min_won_ppga > stats_adversar["Home"]["Total"]["PPG"]:
                            away_team_min_won_ppga = stats_adversar["Home"]["Total"]["PPG"]
                    if m[7] + m[9] < m[6] + m[8]:
                        if away_team_max_lost_ppga < stats_adversar["Home"]["Total"]["PPG"]:
                            away_team_max_lost_ppga = stats_adversar["Home"]["Total"]["PPG"]
                        if away_team_min_lost_ppga > stats_adversar["Home"]["Total"]["PPG"]:
                            away_team_min_lost_ppga = stats_adversar["Home"]["Total"]["PPG"]

            try:
                home_team_stats = stats_provider.get_team_stats(home_team)
                away_team_stats = stats_provider.get_team_stats(away_team)
                home_team_ppg = home_team_stats["Home"]["Total"]["PPG"]
                away_team_ppg = away_team_stats["Away"]["Total"]["PPG"]

                home_team_wins = False
                if away_team_ppg < home_team_min_won_ppga:
                    home_team_wins = True
                away_team_wins = False
                if home_team_ppg < away_team_min_won_ppga:
                    away_team_wins = True

                if home_team_wins and not away_team_wins:
                    if self.meciuri[competitie][meci]['Cote']['1'] <= (self.meciuri[competitie][meci]['Cote']['2'] + 0.2):
                        winners[competitie][meci] = home_team
                if away_team_wins and not home_team_wins:
                    if self.meciuri[competitie][meci]['Cote']['2'] <= (self.meciuri[competitie][meci]['Cote']['1'] + 0.2):
                        winners[competitie][meci] = away_team
            except:
                pass
        return winners


