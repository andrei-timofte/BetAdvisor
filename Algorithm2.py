import os
import json
import re
import copy

from db_helper import db_helper as db
from StatsProvider import StatsProvider


class Algorithm2:

    def __init__(self, meciuri, path_for_logs):
        self.name = "Old Algorithm"
        self.description = """Algoritmul acesta analizeaza meciurile de acasa pentru echipa ce urmeaza sa joace acasa si 
        meciurile din deplasare pentru echipa ce urmeaza sa joace in deplasare constituind un grafic pentru fiecare.
        In acest grafic se incrementeaza pozitia unei echipe ce a castigat un meci si se decrementeaza pozitia pentru 
        cazul in care a pierdut un meci. Daca graficele echipelor ce urmeaza sa joace nu se intersecteaza si au o 
        distanta finala intre indecsi, destul de mare fata de cate meciuri au jucat pana in prezent, se va considera
        echipa cu cel mai mare index ca fiind echipa castigatoare.
        Se numeste OLD Algorithm pentru ca l-am implementat in prima versiune a unui Betting Assistant."""
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
        winners = {competitie: {}}
        if competitie not in self.meciuri.keys():
            return winners
        for meci in self.meciuri[competitie]:
            home_team = self.meciuri[competitie][meci]["Home"]
            away_team = self.meciuri[competitie][meci]["Away"]
            home_team_home_matches = db.get_all_team_results_from_home(competitie, home_team)
            away_team_away_matches = db.get_all_team_results_from_away(competitie, away_team)

            home_team_graph = [0]
            for m in range(len(home_team_home_matches)):
                if home_team_home_matches[m][6] + home_team_home_matches[m][8] > home_team_home_matches[m][7] + home_team_home_matches[m][9]:
                    home_team_graph.append(home_team_graph[-1] + 1)
                elif home_team_home_matches[m][6] + home_team_home_matches[m][8] == home_team_home_matches[m][7] + home_team_home_matches[m][9]:
                    home_team_graph.append(home_team_graph[-1])
                else:
                    home_team_graph.append(home_team_graph[-1] - 1)

            away_team_graph = [0]
            for m in range(len(away_team_away_matches)):
                if away_team_away_matches[m][7] + away_team_away_matches[m][9] > away_team_away_matches[m][6] + away_team_away_matches[m][8]:
                    away_team_graph.append(away_team_graph[-1] + 1)
                elif away_team_away_matches[m][7] + away_team_away_matches[m][9] == away_team_away_matches[m][6] + away_team_away_matches[m][8]:
                    away_team_graph.append(away_team_graph[-1])
                else:
                    away_team_graph.append(away_team_graph[-1] - 1)

            overlapped = []
            bigger = -1
            for index in range(1, min(len(home_team_graph), len(away_team_graph))):
                if home_team_graph[index] > away_team_graph[index]:
                    if bigger == 2:
                        overlapped.append(1)
                    bigger = 1
                elif home_team_graph[index] < away_team_graph[index]:
                    if bigger == 1:
                        overlapped.append(1)
                    bigger = 2
                else:
                    bigger = 0
                    overlapped.append(1)

            # print(home_team_graph)
            # print(away_team_graph)
            # print(overlapped)

            if len(overlapped) < 2:
                # Cauta echipa cu cel mai mare index
                index = min(len(home_team_graph), len(away_team_graph)) - 1
                # Iau ca valoare ultimul index valid din cea mai scurta lista
                # Castigatoare va fi socotita echipa cu indexul mai mare decat adversara cu cel putin numarul de meciuri
                # luate in considerare
                if home_team_graph[index] > (away_team_graph[index] + index):
                    winners[competitie][meci] = home_team
                elif (home_team_graph[index] + index) < away_team_graph[index]:
                    winners[competitie][meci] = away_team
        return winners

