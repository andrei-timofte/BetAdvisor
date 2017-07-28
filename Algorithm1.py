import os
import json
import re

from StatsProvider import StatsProvider


class Algorithm1:

    def __init__(self, meciuri, path_for_logs):
        self.name = "TEST Algoritmul 1"
        self.description = """Algoritm de test generic pentru clasa Algorithm"""
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
        # print("Ar trebui sa analizez competitia {} si meciurile {}".format(competitie, ['{} - {}'.format(self.meciuri[competitie][x]['Home'], self.meciuri[competitie][x]['Away']) for x in self.meciuri[competitie] ] ))
        fis_rezultate = os.path.join(self.path_for_logs, self.pattern.sub('', competitie) + '_history.json')
        stats_provider = StatsProvider(fis_rezultate, competitie)

        winners = {competitie: {}}

        for meci in self.meciuri[competitie]:
            home_team = self.meciuri[competitie][meci]["Home"]
            away_team = self.meciuri[competitie][meci]["Away"]
            meci_stats = stats_provider.report_stats(home_team, away_team)
            # print(meci_stats)
            if meci_stats['AllTeamsFinalStats'][home_team]['Total']['Pts'] > meci_stats['AllTeamsFinalStats'][away_team]['Total']['Pts']:
                winners[competitie][meci] = home_team
            elif meci_stats['AllTeamsFinalStats'][home_team]['Total']['Pts'] < meci_stats['AllTeamsFinalStats'][away_team]['Total']['Pts'] + 2:
                winners[competitie][meci] = away_team
        return winners

