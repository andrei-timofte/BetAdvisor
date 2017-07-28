import os
import json
import re
import copy

from db_helper import db_helper as db
from StatsProvider import StatsProvider


class Algorithm5:

    def __init__(self, meciuri, path_for_logs):
        self.name = "Professional Gambler Algorithm"
        self.description = """Acest algoritm se uita la meciurile de acasa ale echipei ce urmeaza sa joace acasa in meciul
        de analizat, la meciurile din deplasare ale echipei ce urmeaza sa joace in deplasare si la meciurile H2H.
        Calculeaza cotele folosind media armonica a rezultatelor anterioare si le compara cu cotele oferite de 
        superbet.ro. In functie de diferentele in minus sau in plus fata de cotele reale (cele obtinute prin media
        armonica) face predictii pentru meciul analizat.
        Daca superbet.ro nu are in oferta un anumit tip de pariu (de ex. total goluri repriza 2) atunci se afiseaza
        doar recomandarea fara a se compara cu acea cota pentru a obtine Value Per Bet.
        """
        self.meciuri = meciuri
        self.path_for_logs = path_for_logs
        self.pattern = re.compile('[\W_]+', re.UNICODE)
        self.treshold = 75

    def set_probab_treshold(self, treshold: int):
        if treshold < 0 or treshold > 100:
            print('Treshold-ul trebuie sa fie intre 0 si 100! Default este 75!')
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
        match_archive = {}
        if os.path.isfile(os.path.join(self.path_for_logs, 'archive_final.json')):
            with open(os.path.join(self.path_for_logs, 'archive_final.json'), 'rt') as f:
                match_archive = json.load(f)
        # Nu se poate ca un meci sa existe in match_archive si sa nu existe in self.meciuri
        # deoarece match_archive este obtinut prin iterarea self.meciuri
        # Se poate insa sa nu aiba oferta pentru un anumit tip de pariu
        # for competitie in match_archive.keys():
            # print('PGA  - ' + competitie)
        if competitie not in match_archive.keys():
            return winners
        for m in match_archive[competitie]:
            home_prediction = {}
            away_prediction = {}
            if 'FINAL' in self.meciuri[competitie][m]['Cote']:
                home_matches = len(match_archive[competitie][m]['Rezultate_Home'])
                away_matches = len(match_archive[competitie][m]['Rezultate_Away'])

                home_wins = sum([1 if (x[2] + x[4]) > (x[3] + x[5]) else 0 for x in match_archive[competitie][m]['Rezultate_Home']])
                home_draws = sum([1 if (x[2] + x[4]) == (x[3] + x[5]) else 0 for x in match_archive[competitie][m]['Rezultate_Home']])
                home_lost = sum([1 if (x[2] + x[4]) < (x[3] + x[5]) else 0 for x in match_archive[competitie][m]['Rezultate_Home']])

                away_wins = sum([1 if (x[2] + x[4]) < (x[3] + x[5]) else 0 for x in match_archive[competitie][m]['Rezultate_Away']])
                away_draws = sum([1 if (x[2] + x[4]) == (x[3] + x[5]) else 0 for x in match_archive[competitie][m]['Rezultate_Away']])
                away_lost = sum([1 if (x[2] + x[4]) > (x[3] + x[5]) else 0 for x in match_archive[competitie][m]['Rezultate_Away']])

                # Complic lucrurile mai jos pentru a ma asigura ca am doar 2 zecimale dupa virgula
                hw_prob = float(int(float(home_wins / home_matches) * 10000) / 100)
                hw_real_odd = float(int((1/hw_prob) * 10000) / 100)
                hd_prob = float(int(float(home_draws / home_matches) * 10000) / 100)
                hd_real_odd = float(int((1/hd_prob) * 10000) / 100)
                hl_prob = float(int(float(home_lost / home_matches) * 10000) / 100)
                if hl_prob > 0:
                    hl_real_odd = float(int((1/hl_prob) * 10000) / 100)
                else:
                    hl_real_odd = 100

                aw_prob = float(int(float(away_wins / away_matches) * 10000) / 100)
                if aw_prob > 0:
                    aw_real_odd = float(int((1/aw_prob) * 10000) / 100)
                ad_prob = float(int(float(away_draws / away_matches) * 10000) / 100)
                if ad_prob > 0:
                    ad_real_odd = float(int((1/ad_prob) * 10000) / 100)
                else:
                    ad_real_odd = 100
                al_prob = float(int(float(away_lost / away_matches) * 10000) / 100)
                if al_prob > 0:
                    al_real_odd = float(int((1/al_prob) * 10000) / 100)

                if hw_prob >= self.treshold:
                    if 'FINAL' not in home_prediction.keys():
                        home_prediction['FINAL'] = {}
                    if 'Win' not in home_prediction['FINAL'].keys():
                        home_prediction['FINAL']['Win'] = {}
                    home_prediction['FINAL']['Win']['Probab'] = hw_prob
                    home_prediction['FINAL']['Win']['Odd'] = hw_real_odd

                if hd_prob >= self.treshold:
                    if 'FINAL' not in home_prediction.keys():
                        home_prediction['FINAL'] = {}
                    if 'Draw' not in home_prediction['FINAL'].keys():
                        home_prediction['FINAL']['Draw'] = {}
                    home_prediction['FINAL']['Draw']['Probab'] = hd_prob
                    home_prediction['FINAL']['Draw']['Odd'] = hd_real_odd

                if hl_prob >= self.treshold:
                    if 'FINAL' not in home_prediction.keys():
                        home_prediction['FINAL'] = {}
                    if 'Lose' not in home_prediction['FINAL'].keys():
                        home_prediction['FINAL']['Lose'] = {}
                    home_prediction['FINAL']['Lose']['Probab'] = hl_prob
                    home_prediction['FINAL']['Lose']['Odd'] = hl_real_odd

                if aw_prob >= self.treshold:
                    if 'FINAL' not in away_prediction.keys():
                        away_prediction['FINAL'] = {}
                    if 'Win' not in away_prediction['FINAL'].keys():
                        away_prediction['FINAL']['Win'] = {}
                    away_prediction['FINAL']['Win']['Probab'] = aw_prob
                    away_prediction['FINAL']['Win']['Odd'] = aw_real_odd

                if ad_prob >= self.treshold:
                    if 'FINAL' not in away_prediction.keys():
                        away_prediction['FINAL'] = {}
                    if 'Draw' not in away_prediction['FINAL'].keys():
                        away_prediction['FINAL']['Draw'] = {}
                    away_prediction['FINAL']['Draw']['Probab'] = ad_prob
                    away_prediction['FINAL']['Draw']['Odd'] = ad_real_odd

                if al_prob >= self.treshold:
                    if 'FINAL' not in away_prediction.keys():
                        away_prediction['FINAL'] = {}
                    if 'Lose' not in away_prediction['FINAL'].keys():
                        away_prediction['FINAL']['Lose'] = {}
                    away_prediction['FINAL']['Lose']['Probab'] = al_prob
                    away_prediction['FINAL']['Lose']['Odd'] = al_real_odd


            if r'PRIMA REPRIZ\u0102' in self.meciuri[competitie][m]['Cote']:
                home_matches = len(match_archive[competitie][m]['Rezultate_Home'])
                away_matches = len(match_archive[competitie][m]['Rezultate_Away'])

                home_wins = sum([1 if x[2] > x[3] else 0 for x in match_archive[competitie][m]['Rezultate_Home']])
                home_draws = sum([1 if x[2] == x[3] else 0 for x in match_archive[competitie][m]['Rezultate_Home']])
                home_lost = sum([1 if x[2] < x[3] else 0 for x in match_archive[competitie][m]['Rezultate_Home']])

                away_wins = sum([1 if x[2] < x[3] else 0 for x in match_archive[competitie][m]['Rezultate_Away']])
                away_draws = sum([1 if x[2] == x[3] else 0 for x in match_archive[competitie][m]['Rezultate_Away']])
                away_lost = sum([1 if x[2] > x[3] else 0 for x in match_archive[competitie][m]['Rezultate_Away']])

                # Complic lucrurile mai jos pentru a ma asigura ca am doar 2 zecimale dupa virgula
                hw_prob = float(int(float(home_wins / home_matches) * 10000) / 100)
                hw_real_odd = float(int((1/hw_prob) * 10000) / 100)
                hd_prob = float(int(float(home_draws / home_matches) * 10000) / 100)
                hd_real_odd = float(int((1/hd_prob) * 10000) / 100)
                hl_prob = float(int(float(home_lost / home_matches) * 10000) / 100)
                hl_real_odd = float(int((1/hl_prob) * 10000) / 100)

                aw_prob = float(int(float(away_wins / away_matches) * 10000) / 100)
                aw_real_odd = float(int((1/aw_prob) * 10000) / 100)
                ad_prob = float(int(float(away_draws / away_matches) * 10000) / 100)
                ad_real_odd = float(int((1/ad_prob) * 10000) / 100)
                al_prob = float(int(float(away_lost / away_matches) * 10000) / 100)
                al_real_odd = float(int((1/al_prob) * 10000) / 100)

                if hw_prob >= self.treshold:
                    if r'PRIMA REPRIZ\u0102' not in home_prediction.keys():
                        home_prediction[r'PRIMA REPRIZ\u0102'] = {}
                    if 'Win' not in home_prediction[r'PRIMA REPRIZ\u0102'].keys():
                        home_prediction[r'PRIMA REPRIZ\u0102']['Win'] = {}
                    home_prediction[r'PRIMA REPRIZ\u0102']['Win']['Probab'] = hw_prob
                    home_prediction[r'PRIMA REPRIZ\u0102']['Win']['Odd'] = hw_real_odd
                if hd_prob >= self.treshold:
                    if r'PRIMA REPRIZ\u0102' not in home_prediction.keys():
                        home_prediction[r'PRIMA REPRIZ\u0102'] = {}
                    if 'Draw' not in home_prediction[r'PRIMA REPRIZ\u0102'].keys():
                        home_prediction[r'PRIMA REPRIZ\u0102']['Draw'] = {}
                    home_prediction[r'PRIMA REPRIZ\u0102']['Draw']['Probab'] = hd_prob
                    home_prediction[r'PRIMA REPRIZ\u0102']['Draw']['Odd'] = hd_real_odd
                if hl_prob >= self.treshold:
                    if r'PRIMA REPRIZ\u0102' not in home_prediction.keys():
                        home_prediction[r'PRIMA REPRIZ\u0102'] = {}
                    if 'Lose' not in home_prediction[r'PRIMA REPRIZ\u0102'].keys():
                        home_prediction[r'PRIMA REPRIZ\u0102']['Lose'] = {}
                    home_prediction[r'PRIMA REPRIZ\u0102']['Lose']['Probab'] = hl_prob
                    home_prediction[r'PRIMA REPRIZ\u0102']['Lose']['Odd'] = hl_real_odd

                if aw_prob >= self.treshold:
                    if r'PRIMA REPRIZ\u0102' not in away_prediction.keys():
                        away_prediction[r'PRIMA REPRIZ\u0102'] = {}
                    if 'Win' not in away_prediction[r'PRIMA REPRIZ\u0102'].keys():
                        away_prediction[r'PRIMA REPRIZ\u0102']['Win'] = {}
                    away_prediction[r'PRIMA REPRIZ\u0102']['Win']['Probab'] = aw_prob
                    away_prediction[r'PRIMA REPRIZ\u0102']['Win']['Odd'] = aw_real_odd
                if ad_prob >= self.treshold:
                    if r'PRIMA REPRIZ\u0102' not in away_prediction.keys():
                        away_prediction[r'PRIMA REPRIZ\u0102'] = {}
                    if 'Draw' not in away_prediction[r'PRIMA REPRIZ\u0102'].keys():
                        away_prediction[r'PRIMA REPRIZ\u0102']['Draw'] = {}
                    away_prediction[r'PRIMA REPRIZ\u0102']['Draw']['Probab'] = ad_prob
                    away_prediction[r'PRIMA REPRIZ\u0102']['Draw']['Odd'] = ad_real_odd
                if al_prob >= self.treshold:
                    if r'PRIMA REPRIZ\u0102' not in away_prediction.keys():
                        away_prediction[r'PRIMA REPRIZ\u0102'] = {}
                    if 'Lose' not in away_prediction[r'PRIMA REPRIZ\u0102'].keys():
                        away_prediction[r'PRIMA REPRIZ\u0102']['Lose'] = {}
                    away_prediction[r'PRIMA REPRIZ\u0102']['Lose']['Probab'] = al_prob
                    away_prediction[r'PRIMA REPRIZ\u0102']['Lose']['Odd'] = al_real_odd

            if r'A DOUA REPRIZ\u0102' in self.meciuri[competitie][m]['Cote']:
                home_matches = len(match_archive[competitie][m]['Rezultate_Home'])
                away_matches = len(match_archive[competitie][m]['Rezultate_Away'])

                home_wins = sum([1 if x[4] > x[5] else 0 for x in match_archive[competitie][m]['Rezultate_Home']])
                home_draws = sum([1 if x[4] == x[5] else 0 for x in match_archive[competitie][m]['Rezultate_Home']])
                home_lost = sum([1 if x[4] < x[5] else 0 for x in match_archive[competitie][m]['Rezultate_Home']])

                away_wins = sum([1 if x[4] < x[5] else 0 for x in match_archive[competitie][m]['Rezultate_Away']])
                away_draws = sum([1 if x[4] == x[5] else 0 for x in match_archive[competitie][m]['Rezultate_Away']])
                away_lost = sum([1 if x[4] > x[5] else 0 for x in match_archive[competitie][m]['Rezultate_Away']])

                # Complic lucrurile mai jos pentru a ma asigura ca am doar 2 zecimale dupa virgula
                hw_prob = float(int(float(home_wins / home_matches) * 10000) / 100)
                hw_real_odd = float(int((1/hw_prob) * 10000) / 100)
                hd_prob = float(int(float(home_draws / home_matches) * 10000) / 100)
                hd_real_odd = float(int((1/hd_prob) * 10000) / 100)
                hl_prob = float(int(float(home_lost / home_matches) * 10000) / 100)
                hl_real_odd = float(int((1/hl_prob) * 10000) / 100)

                aw_prob = float(int(float(away_wins / away_matches) * 10000) / 100)
                aw_real_odd = float(int((1/aw_prob) * 10000) / 100)
                ad_prob = float(int(float(away_draws / away_matches) * 10000) / 100)
                ad_real_odd = float(int((1/ad_prob) * 10000) / 100)
                al_prob = float(int(float(away_lost / away_matches) * 10000) / 100)
                al_real_odd = float(int((1/al_prob) * 10000) / 100)

                if hw_prob >= self.treshold:
                    if r'A DOUA REPRIZ\u0102' not in home_prediction.keys():
                        home_prediction[r'A DOUA REPRIZ\u0102'] = {}
                    if 'Win' not in home_prediction[r'A DOUA REPRIZ\u0102'].keys():
                        home_prediction[r'A DOUA REPRIZ\u0102']['Win'] = {}
                    home_prediction[r'A DOUA REPRIZ\u0102']['Win']['Probab'] = hw_prob
                    home_prediction[r'A DOUA REPRIZ\u0102']['Win']['Odd'] = hw_real_odd
                if hd_prob >= self.treshold:
                    if r'A DOUA REPRIZ\u0102' not in home_prediction.keys():
                        home_prediction[r'A DOUA REPRIZ\u0102'] = {}
                    if 'Draw' not in home_prediction[r'A DOUA REPRIZ\u0102'].keys():
                        home_prediction[r'A DOUA REPRIZ\u0102']['Draw'] = {}
                    home_prediction[r'A DOUA REPRIZ\u0102']['Draw']['Probab'] = hd_prob
                    home_prediction[r'A DOUA REPRIZ\u0102']['Draw']['Odd'] = hd_real_odd
                if hl_prob >= self.treshold:
                    if r'A DOUA REPRIZ\u0102' not in home_prediction.keys():
                        home_prediction[r'A DOUA REPRIZ\u0102'] = {}
                    if 'Lose' not in home_prediction[r'A DOUA REPRIZ\u0102'].keys():
                        home_prediction[r'A DOUA REPRIZ\u0102']['Lose'] = {}
                    home_prediction[r'A DOUA REPRIZ\u0102']['Lose']['Probab'] = hl_prob
                    home_prediction[r'A DOUA REPRIZ\u0102']['Lose']['Odd'] = hl_real_odd

                if aw_prob >= self.treshold:
                    if r'A DOUA REPRIZ\u0102' not in away_prediction.keys():
                        away_prediction[r'A DOUA REPRIZ\u0102'] = {}
                    if 'Win' not in away_prediction[r'A DOUA REPRIZ\u0102'].keys():
                        away_prediction[r'A DOUA REPRIZ\u0102']['Win'] = {}
                    away_prediction[r'A DOUA REPRIZ\u0102']['Win']['Probab'] = aw_prob
                    away_prediction[r'A DOUA REPRIZ\u0102']['Win']['Odd'] = aw_real_odd
                if ad_prob >= self.treshold:
                    if r'A DOUA REPRIZ\u0102' not in away_prediction.keys():
                        away_prediction[r'A DOUA REPRIZ\u0102'] = {}
                    if 'Draw' not in away_prediction[r'A DOUA REPRIZ\u0102'].keys():
                        away_prediction[r'A DOUA REPRIZ\u0102']['Draw'] = {}
                    away_prediction[r'A DOUA REPRIZ\u0102']['Draw']['Probab'] = ad_prob
                    away_prediction[r'A DOUA REPRIZ\u0102']['Draw']['Odd'] = ad_real_odd
                if al_prob >= self.treshold:
                    if r'A DOUA REPRIZ\u0102' not in away_prediction.keys():
                        away_prediction[r'A DOUA REPRIZ\u0102'] = {}
                    if 'Lose' not in away_prediction[r'A DOUA REPRIZ\u0102'].keys():
                        away_prediction[r'A DOUA REPRIZ\u0102']['Lose'] = {}
                    away_prediction[r'A DOUA REPRIZ\u0102']['Lose']['Probab'] = al_prob
                    away_prediction[r'A DOUA REPRIZ\u0102']['Lose']['Odd'] = al_real_odd

            if 'DGNG' in self.meciuri[competitie][m]['Cote']:
                home_matches = len(match_archive[competitie][m]['Rezultate_Home'])
                away_matches = len(match_archive[competitie][m]['Rezultate_Away'])

                home_goals = sum([1 if (x[2] > 0) or (x[4] > 0) else 0 for x in match_archive[competitie][m]['Rezultate_Home']])
                home_no_goals = sum([1 if (x[2] == 0) and (x[4] == 0) else 0 for x in match_archive[competitie][m]['Rezultate_Home']])

                away_goals = sum([1 if (x[3] > 0) or (x[5] > 0) else 0 for x in match_archive[competitie][m]['Rezultate_Away']])
                away_no_goals = sum([1 if (x[3] == 0) and (x[5] == 0) else 0 for x in match_archive[competitie][m]['Rezultate_Away']])

                # Complic lucrurile mai jos pentru a ma asigura ca am doar 2 zecimale dupa virgula
                hg_prob = float(int(float(home_goals / home_matches) * 10000) / 100)
                hg_real_odd = float(int((1/hg_prob) * 10000) / 100)
                hng_prob = float(int(float(home_no_goals / home_matches) * 10000) / 100)
                if hng_prob > 0:
                    hng_real_odd = float(int((1/hng_prob) * 10000) / 100)
                else:
                    hng_real_odd = 100

                ag_prob = float(int(float(away_goals / away_matches) * 10000) / 100)
                ag_real_odd = float(int((1/ag_prob) * 10000) / 100)
                ang_prob = float(int(float(away_no_goals / away_matches) * 10000) / 100)
                ang_real_odd = float(int((1/ang_prob) * 10000) / 100)

                if hg_prob >= self.treshold:
                    if 'DGNG' not in home_prediction.keys():
                        home_prediction['DGNG'] = {}
                    if 'DG' not in home_prediction['DGNG'].keys():
                        home_prediction['DGNG']['DG'] = {}
                    home_prediction['DGNG']['DG']['Probab'] = hg_prob
                    home_prediction['DGNG']['DG']['Odd'] = hg_real_odd
                if hng_prob >= self.treshold:
                    if 'DGNG' not in home_prediction.keys():
                        home_prediction['DGNG'] = {}
                    if 'NDG' not in home_prediction['DGNG'].keys():
                        home_prediction['DGNG']['NDG'] = {}
                    home_prediction['DGNG']['NDG']['Probab'] = hng_prob
                    home_prediction['DGNG']['NDG']['Odd'] = hng_real_odd

                if ag_prob >= self.treshold:
                    if 'DGNG' not in away_prediction.keys():
                        away_prediction['DGNG'] = {}
                    if 'DG' not in away_prediction['DGNG'].keys():
                        away_prediction['DGNG']['DG'] = {}
                    away_prediction['DGNG']['DG']['Probab'] = ag_prob
                    away_prediction['DGNG']['DG']['Odd'] = ag_real_odd
                if ang_prob >= self.treshold:
                    if 'DGNG' not in away_prediction.keys():
                        away_prediction['DGNG'] = {}
                    if 'NDG' not in away_prediction['DGNG'].keys():
                        away_prediction['DGNG']['NDG'] = {}
                    away_prediction['DGNG']['NDG']['Probab'] = ang_prob
                    away_prediction['DGNG']['NDG']['Odd'] = ang_real_odd

                # R1
                home_goals = sum([1 if x[2] > 0 else 0 for x in match_archive[competitie][m]['Rezultate_Home']])
                home_no_goals = sum([1 if x[2] == 0 else 0 for x in match_archive[competitie][m]['Rezultate_Home']])

                away_goals = sum([1 if x[3] > 0 else 0 for x in match_archive[competitie][m]['Rezultate_Away']])
                away_no_goals = sum([1 if x[3] == 0 else 0 for x in match_archive[competitie][m]['Rezultate_Away']])

                # Complic lucrurile mai jos pentru a ma asigura ca am doar 2 zecimale dupa virgula
                hg_prob = float(int(float(home_goals / home_matches) * 10000) / 100)
                hg_real_odd = float(int((1/hg_prob) * 10000) / 100)
                hng_prob = float(int(float(home_no_goals / home_matches) * 10000) / 100)
                hng_real_odd = float(int((1/hng_prob) * 10000) / 100)

                ag_prob = float(int(float(away_goals / away_matches) * 10000) / 100)
                ag_real_odd = float(int((1/ag_prob) * 10000) / 100)
                ang_prob = float(int(float(away_no_goals / away_matches) * 10000) / 100)
                ang_real_odd = float(int((1/ang_prob) * 10000) / 100)

                if hg_prob >= self.treshold:
                    if 'DGNG' not in home_prediction.keys():
                        home_prediction['DGNG'] = {}
                    if 'DG1' not in home_prediction['DGNG'].keys():
                        home_prediction['DGNG']['DG1'] = {}
                    home_prediction['DGNG']['DG1']['Probab'] = hg_prob
                    home_prediction['DGNG']['DG1']['Odd'] = hg_real_odd
                if hng_prob >= self.treshold:
                    if 'DGNG' not in home_prediction.keys():
                        home_prediction['DGNG'] = {}
                    if 'NDG1' not in home_prediction['DGNG'].keys():
                        home_prediction['DGNG']['NDG1'] = {}
                    home_prediction['DGNG']['NDG1']['Probab'] = hng_prob
                    home_prediction['DGNG']['NDG1']['Odd'] = hng_real_odd

                if ag_prob >= self.treshold:
                    if 'DGNG' not in away_prediction.keys():
                        away_prediction['DGNG'] = {}
                    if 'DG1' not in away_prediction['DGNG'].keys():
                        away_prediction['DGNG']['DG1'] = {}
                    away_prediction['DGNG']['DG1']['Probab'] = ag_prob
                    away_prediction['DGNG']['DG1']['Odd'] = ag_real_odd
                if ang_prob >= self.treshold:
                    if 'DGNG' not in away_prediction.keys():
                        away_prediction['DGNG'] = {}
                    if 'NDG1' not in away_prediction['DGNG'].keys():
                        away_prediction['DGNG']['NDG1'] = {}
                    away_prediction['DGNG']['NDG1']['Probab'] = ang_prob
                    away_prediction['DGNG']['NDG1']['Odd'] = ang_real_odd

                # R2
                home_goals = sum([1 if x[4] > 0 else 0 for x in match_archive[competitie][m]['Rezultate_Home']])
                home_no_goals = sum([1 if x[4] == 0 else 0 for x in match_archive[competitie][m]['Rezultate_Home']])

                away_goals = sum([1 if x[5] > 0 else 0 for x in match_archive[competitie][m]['Rezultate_Away']])
                away_no_goals = sum([1 if x[5] == 0 else 0 for x in match_archive[competitie][m]['Rezultate_Away']])

                # Complic lucrurile mai jos pentru a ma asigura ca am doar 2 zecimale dupa virgula
                hg_prob = float(int(float(home_goals / home_matches) * 10000) / 100)
                hg_real_odd = float(int((1/hg_prob) * 10000) / 100)
                hng_prob = float(int(float(home_no_goals / home_matches) * 10000) / 100)
                hng_real_odd = float(int((1/hng_prob) * 10000) / 100)

                ag_prob = float(int(float(away_goals / away_matches) * 10000) / 100)
                ag_real_odd = float(int((1/ag_prob) * 10000) / 100)
                ang_prob = float(int(float(away_no_goals / away_matches) * 10000) / 100)
                ang_real_odd = float(int((1/ang_prob) * 10000) / 100)

                if hg_prob >= self.treshold:
                    if 'DGNG' not in home_prediction.keys():
                        home_prediction['DGNG'] = {}
                    if 'DG2' not in home_prediction['DGNG'].keys():
                        home_prediction['DGNG']['DG2'] = {}
                    home_prediction['DGNG']['DG2']['Probab'] = hg_prob
                    home_prediction['DGNG']['DG2']['Odd'] = hg_real_odd
                if hng_prob >= self.treshold:
                    if 'DGNG' not in home_prediction.keys():
                        home_prediction['DGNG'] = {}
                    if 'NDG2' not in home_prediction['DGNG'].keys():
                        home_prediction['DGNG']['NDG2'] = {}
                    home_prediction['DGNG']['NDG2']['Probab'] = hng_prob
                    home_prediction['DGNG']['NDG2']['Odd'] = hng_real_odd

                if ag_prob >= self.treshold:
                    if 'DGNG' not in away_prediction.keys():
                        away_prediction['DGNG'] = {}
                    if 'DG2' not in away_prediction['DGNG'].keys():
                        away_prediction['DGNG']['DG2'] = {}
                    away_prediction['DGNG']['DG2']['Probab'] = ag_prob
                    away_prediction['DGNG']['DG2']['Odd'] = ag_real_odd
                if ang_prob >= self.treshold:
                    if 'DGNG' not in away_prediction.keys():
                        away_prediction['DGNG'] = {}
                    if 'NDG2' not in away_prediction['DGNG'].keys():
                        away_prediction['DGNG']['NDG2'] = {}
                    away_prediction['DGNG']['NDG2']['Probab'] = ang_prob
                    away_prediction['DGNG']['NDG2']['Odd'] = ang_real_odd

            if len(home_prediction.keys()) > 0:
                if competitie not in winners.keys():
                    winners[competitie] = {}
                if m not in winners[competitie].keys():
                    winners[competitie][m] = {}
                winners[competitie][m]['HOME_PREDS'] = copy.deepcopy(home_prediction)
            if len(away_prediction.keys()) > 0:
                if competitie not in winners.keys():
                    winners[competitie] = {}
                if m not in winners[competitie].keys():
                    winners[competitie][m] = {}
                winners[competitie][m]['AWAY_PREDS'] = copy.deepcopy(away_prediction)
        return winners

