import os
import json
import re
import copy

from db_helper import db_helper as db
from StatsProvider import StatsProvider


class Algorithm6:

    def __init__(self, meciuri, path_for_logs):
        self.name = "Over/Under 2.5 tip 1"
        self.description = """Acest algoritm foloseste o modalitate de analiza luata de pe net (nu mai stiu exact de unde):
Hello!
My name is Vincent and I want to share my betting strategy with you. I play on over/under 2.5 goals in football matches like this:

I take into consideration the last 4 matches of each team involved in the current game (that's 8 matches in total).
If a game has ended with an over 2.5 score I give it +0.5 points.
If both teams scored in that match I give it another +0.75 points (even if the match ended under 2.5).
If the game ended under 2.5 I give it -0.5 points.
If one of the teams didn't score in the match (even if it was over 2.5) I give it -0.75 points.

In the end I sum up all those points and I get a positive or negative result. To give an example:

match results 4:2 2:1 2:2 0:0 2:0 2:1 3:1 3:0

For the above matches my calculation would look like this:

+0.5 +0.75 +0.5 +0.75 +0.5 +0.75 -0.5 -0.75 -0.5 -0.75 +0.5 +0.75 +0.5 +0.75+ 0.5- 0.75 =+3.5 points.

That would mean to put a 3.5/10 units bet on over 2.5 goals. The maximum results are +10 and -10 points. That would mean a certain over 2.5, respectively under 2.5 goals match.

I usually place a bet only if I get a minimum +/-5 points result. So, for example, if I get a +6 I place a 6/10 units bet on over 2.5 goals. 
        """
        self.meciuri = meciuri
        self.path_for_logs = path_for_logs
        self.pattern = re.compile('[\W_]+', re.UNICODE)
        self.treshold = 6
        self.only_home_away_maches = False

    def set_points_treshold(self, treshold: int):
        if treshold < 0 or treshold > 10:
            print('Treshold-ul trebuie sa fie intre 0 si 10! Default este 6!')
            return
        self.treshold = treshold


    def analyze(self, competitie: str):
        """
        Calea pentru loguri se primeste la initializare pentru ca va fi aceeasi pentru fiecare thread.
        Meciurile se primesc sub forma de dictionar (json) la initializare intru cat nu se modifica in cursul analizei.
        :param competitie: Competitia de pe superbet
        :return: dict. Castigatorii pentru fiecare meci, sub forma de dictionar in care cheia va fi numarul meciului si valoarea va fi castigatorul preconizat
        """
        # stats_provider = StatsProvider(competitie)

        winners = {competitie: {}}
        if competitie not in self.meciuri.keys():
            return winners

        for m in self.meciuri[competitie]:
            home_team = self.meciuri[competitie][m]["Home"]
            away_team = self.meciuri[competitie][m]["Away"]
            if self.only_home_away_maches:
                home_team_matches = db.get_all_team_results_from_home(competitie, home_team)
                if len(home_team_matches) < 4:
                    print('{} - {}\t  {} are mai putin de 4 meciuri jucate acasa! Incerc sa iau si meciurile din deplasare!'.format(home_team, away_team, home_team))
                    home_team_matches = db.get_all_team_results(competitie, home_team)

                away_team_matches = db.get_all_team_results_from_away(competitie, away_team)
                if len(away_team_matches) < 4:
                    print('{} - {}\t  {} are mai putin de 4 meciuri jucate acasa! Incerc sa iau si meciurile din deplasare!'.format(home_team, away_team, away_team))
                    away_team_matches = db.get_all_team_results(competitie, away_team)
            else:
                home_team_matches = db.get_all_team_results(competitie, home_team)
                away_team_matches = db.get_all_team_results(competitie, away_team)

            if len(home_team_matches) >= 4 and len(away_team_matches) >= 4:
                # Iau doar ultimele 4 meciuri. Meciurile le primesc in ordinea id-urilor deci si in ordinea cronologica
                # Nu ma intereseaza care din cele doua echipe a jucat un meci asa ca le pun intr-o lista comuna
                required_matches = home_team_matches[-4:] + away_team_matches[-4:]
                score = 0.0
                for match in required_matches:
                    # id, competitie, runda, id_meci, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score
                    if match[6] + match[7] + match[8] + match[9] > 2:
                        score += 0.5
                    else:
                        score -= 0.5
                    if (match[6] + match[8] > 0) and (match[7] + match[9] > 0):
                        score += 0.75
                    else:
                        score -= 0.75

                if abs(score) >= self.treshold:
                    if score < 0:
                        winners[competitie][m] = '{} - {} => UNDER 2.5 - score {}'.format(home_team, away_team, score)
                    else:
                        winners[competitie][m] = '{} - {} => OVER 2.5 - score {}'.format(home_team, away_team, score)
        return winners

