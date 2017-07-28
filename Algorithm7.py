import os
import json
import re
import copy

from db_helper import db_helper as db
from StatsProvider import StatsProvider


class Algorithm7:

    def __init__(self, meciuri, path_for_logs):
        self.name = "Over/Under 2.5 tip 2 - NOT SO GOOD - tip 1 seams better"
        self.description = """Acest algoritm foloseste o modalitate de analiza luata de pe net (nu mai stiu exact de unde):
This is an Under/Over strategy

I'm afraid it look's a bit simple, but it has been quite profitable for me. As mentioned it's an under/over strategy and it's based only on statistics.

Let's imagine that there's a match between team A and team B. (A is the home team). First of all I will check what is team A's average
of goals scored and conceded at home. Let's say that team A scores 2.1 and concedes 1.20 - total of 3.30 goals average in team A's home games.
Then I will check what team B's average of goals scored and conceived in their away games is. Let's say that team B scores 1.75 avg. and
concedes 1.15 - a total of 2.90 goals avg. in team B's away games.
Then I take the two smallest numbers 1.15 + 1.20 = 2.35 - minimum goals in this match. In the same manner you find the maximum which is 3.85.
The avg. of the min/max is 3.10 which is much more the line of 2.50, so I will bet over in this game.
If I get an avg. of 2.70 or more I will bet over with high stakes. If it's between 2.50 and 2.70 I will decide by myself if the OVER bet is
worth a try, but it will definitely be with small stakes. If I get an average between 2.30 and 2.50 I will decide if the UNDER bet is worth
a try and it will definitely be with small stakes.
If I get an average of 2.30 or lower I will bet under with high stakes.
Of course, sometimes I don't necessarily bet on the 2.50 line. I might also bet on lines of 3.00, 2.00 and others.

I have already increased my bank by 50% in one month using this betting strategy and I will certainly continue increasing my betting bank further.
        """
        self.meciuri = meciuri
        self.path_for_logs = path_for_logs
        self.pattern = re.compile('[\W_]+', re.UNICODE)
        self.treshold = 0.2
        self.only_home_away_maches = True

    def set_average_treshold(self, treshold: int):
        if treshold < 0 or treshold > 10:
            print('Treshold-ul trebuie sa fie intre 0 si 10! Default este 0.2!')
            return
        self.treshold = treshold


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

        stats_provider = StatsProvider(competitie)

        for m in self.meciuri[competitie]:
            home_team = self.meciuri[competitie][m]["Home"]
            away_team = self.meciuri[competitie][m]["Away"]
            home_team_stats = stats_provider.get_team_stats(home_team)
            away_team_stats = stats_provider.get_team_stats(away_team)
            if home_team_stats is None or away_team_stats is None:
                continue
            home_team_gf_average = 0.0
            home_team_ga_average = 0.0
            away_team_gf_average = 0.0
            away_team_ga_average = 0.0
            enough_stats = True
            if self.only_home_away_maches:
                if home_team_stats['Home']['P'] < 4:
                    enough_stats = False
                else:
                    home_team_gf_average = home_team_stats['Home']['Total']['GF'] / home_team_stats['Home']['P']
                    home_team_ga_average = home_team_stats['Home']['Total']['GA'] / home_team_stats['Home']['P']
                if away_team_stats['Away']['P'] < 4:
                    enough_stats = False
                else:
                    away_team_gf_average = away_team_stats['Away']['Total']['GF'] / away_team_stats['Away']['P']
                    away_team_ga_average = away_team_stats['Away']['Total']['GA'] / away_team_stats['Away']['P']
            else:
                if home_team_stats['Total']['P'] < 4:
                    enough_stats = False
                else:
                    home_team_gf_average = home_team_stats['Total']['General']['GF'] / home_team_stats['Total']['P']
                    home_team_ga_average = home_team_stats['Total']['General']['GA'] / home_team_stats['Total']['P']
                if away_team_stats['Total']['P'] < 4:
                    enough_stats = False
                else:
                    away_team_gf_average = away_team_stats['Total']['General']['GF'] / away_team_stats['Total']['P']
                    away_team_ga_average = away_team_stats['Total']['General']['GA'] / away_team_stats['Total']['P']

            if enough_stats:
                score = (home_team_gf_average + home_team_ga_average + away_team_gf_average + away_team_ga_average) / 2
                if score < (2.5 - self.treshold):
                    winners[competitie][m] = ' => UNDER 2.5 - score {}'.format(score)
                elif score >= (2.5 + self.treshold):
                    winners[competitie][m] = ' => OVER 2.5 - score {}'.format(score)
        return winners

