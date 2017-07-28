import os
import json
import re
import copy

from db_helper import db_helper as db
from StatsProvider import StatsProvider


class Algorithm4:

    def __init__(self, meciuri, path_for_logs):
        self.name = "Similarity Algorithm"
        self.description = """Acest algoritm cauta in meciurile echipei de acasa echipa cu statisticile cele mai
        apropiate de echipa cu care urmeaza sa joace si da pronosticul in functie de rezultatul acelui meci.
        Face acelasi lucru si pentru echipa ce urmeaza sa joace in deplasare.
        Daca ambele algoritmuri dau ca si castigatoare aceeasi echipa atunci aceea va fi sugerata.
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
            try:
                home_team_matches = db.get_all_team_results_from_home(competitie, home_team)
                away_team_matches = db.get_all_team_results_from_away(competitie, away_team)
                home_team_stats = stats_provider.get_team_stats(home_team)
                away_team_stats = stats_provider.get_team_stats(away_team)

                # Home team history based prediction
                home_team_opponents = []
                for m in home_team_matches:
                    home_team_opponents.append(stats_provider.get_team(m[5]))

                opponents_stats_list = []
                opponents_list = []
                for team in range(len(home_team_opponents)):
                    opponent_stats = home_team_opponents[team].get_away_stats()
                    diff_stats = [abs(away_team_stats["Away"]["Total"]["W"] - opponent_stats["Total"]["W"]),
                                  abs(away_team_stats["Away"]["Total"]["D"] - opponent_stats["Total"]["D"]),
                                  abs(away_team_stats["Away"]["Total"]["L"] - opponent_stats["Total"]["L"]),
                                  abs(away_team_stats["Away"]["Total"]["GF"] - opponent_stats["Total"]["GF"]),
                                  abs(away_team_stats["Away"]["Total"]["GA"] - opponent_stats["Total"]["GA"]),
                                  abs(away_team_stats["Away"]["Total"]["PPG"] - opponent_stats["Total"]["PPG"])]
                    opponents_stats_list.append(diff_stats)
                    opponents_list.append(home_team_opponents[team].name)

                min_diff_stats = 99999
                selected_opponent = None
                for stats in range(len(opponents_stats_list)):
                    total_diff = sum(opponents_stats_list[stats])
                    if min_diff_stats > total_diff:
                        min_diff_stats = total_diff
                        selected_opponent = opponents_list[stats]

                pronostic_home = ""
                if selected_opponent is not None:
                    for m in home_team_matches:
                        if selected_opponent == m[5]:
                            if m[6] + m[8] > m[7] + m[9]:
                                pronostic_home = "1"
                            elif m[6] + m[8] == m[7] + m[9]:
                                pronostic_home = "X"
                            else:
                                pronostic_home = "2"
                            break

                # Away team history based prediction
                away_team_opponents = []
                for m in away_team_matches:
                    away_team_opponents.append(stats_provider.get_team(m[4]))

                opponents_stats_list = []
                opponents_list = []
                for team in range(len(away_team_opponents)):
                    opponent_stats = away_team_opponents[team].get_home_stats()
                    diff_stats = [abs(home_team_stats["Home"]["Total"]["W"] - opponent_stats["Total"]["W"]),
                                  abs(home_team_stats["Home"]["Total"]["D"] - opponent_stats["Total"]["D"]),
                                  abs(home_team_stats["Home"]["Total"]["L"] - opponent_stats["Total"]["L"]),
                                  abs(home_team_stats["Home"]["Total"]["GF"] - opponent_stats["Total"]["GF"]),
                                  abs(home_team_stats["Home"]["Total"]["GA"] - opponent_stats["Total"]["GA"]),
                                  abs(home_team_stats["Home"]["Total"]["PPG"] - opponent_stats["Total"]["PPG"])]
                    opponents_stats_list.append(diff_stats)
                    opponents_list.append(away_team_opponents[team].name)

                min_diff_stats = 99999
                selected_opponent = None
                for stats in range(len(opponents_stats_list)):
                    total_diff = sum(opponents_stats_list[stats])
                    if min_diff_stats > total_diff:
                        min_diff_stats = total_diff
                        selected_opponent = opponents_list[stats]

                pronostic_away = ""
                if selected_opponent is not None:
                    for m in away_team_matches:
                        if selected_opponent == m[4]:
                            if m[7] + m[9] > m[6] + m[8]:
                                pronostic_away = "2"
                            elif m[7] + m[9] == m[6] + m[8]:
                                pronostic_away = "X"
                            else:
                                pronostic_away = "1"
                            break

                if pronostic_home in pronostic_away:
                    if "1" in pronostic_home:
                        winners[competitie][meci] = home_team
                    elif "X" in pronostic_home:
                        winners[competitie][meci] = "X"
                    else:
                        winners[competitie][meci] = away_team
            except:
                pass
        return winners

