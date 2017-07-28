import os
import sys
import json

from db_helper import db_helper as db
from Algorithm1 import Algorithm1
from Algorithm2 import Algorithm2
from Algorithm3 import Algorithm3
from Algorithm2_1 import Algorithm2C
from Algorithm3_1 import Algorithm3C
from Algorithm4 import Algorithm4
from Algorithm5 import Algorithm5
from Algorithm6 import Algorithm6
from Algorithm7 import Algorithm7


def competition_defined(compet):
    global competitions_aliases
    if len(competitions_aliases.keys()) < 1:
        return False
    for c, _ in competitions_aliases.items():
        if "Aliases" in competitions_aliases[c].keys():
            if compet in competitions_aliases[c]["Aliases"]:
                return c
    return False


def get_team_name_from_alias(competitie, echipa):
    global teams_aliases
    if len(teams_aliases.keys()) == 0:
        return None
    if competitie not in teams_aliases.keys():
        return None
    for team in teams_aliases[competitie].keys():
        if echipa in teams_aliases[competitie][team]:
            return team
    return None

competitions_aliases = {}
teams_aliases = {}
not_interested_competitions = []
meciuri_soccerstats = {}


# if len(sys.argv) < 2:
#     print("Trebuie sa primesc ca parametru fisierul meciuri.json pe care trebuie sa-l analizez!")
#     exit(1)
def analyze_matches(matches_path):
    results_folder = os.path.dirname(os.path.realpath(matches_path))
    global competitions_aliases
    global teams_aliases
    global not_interested_competitions
    global meciuri_soccerstats
    competitions_aliases = {}
    if os.path.isfile('competitions_aliases.json'):
        with open('competitions_aliases.json', 'rt') as f:
            competitions_aliases = json.load(f)

    teams_aliases = {}
    if os.path.isfile('teams_aliases.json'):
        with open('teams_aliases.json', 'rt') as f:
            teams_aliases = json.load(f)

    not_interested_competitions = []
    if os.path.isfile('not_interested_competitions.txt'):
        with open('not_interested_competitions.txt', 'rt') as f:
            not_interested_competitions = f.readlines()


    with open(matches_path, 'rt') as f:
        meciuri = json.load(f)
    """
    Trebuie sa refac meciurile folosind aliasurile competitiilor si echipelor pentru a putea fi folosite mai rapid de
    algoritmii de analiza. Daca nu fac asta, fiecare algoritm va cauta aliasul fiecarei echipe la fiecare iteratie.
    Crescand numarul de algoritmi va creste si numarul operatiilor inutile.
    Fac asta aici o singura data si apoi trimit la fiecare algoritm variabila meciuri actualizata cu aliasurile 
    transformand totul intr-un search.
    """
    meciuri_soccerstats = {}

    for k, v in meciuri.items():
        exists = competition_defined(k)
        if isinstance(exists, str):
            for m in meciuri[k].keys():  # index
                echipa_home = get_team_name_from_alias(exists, meciuri[k][m]['Home'])
                echipa_away = get_team_name_from_alias(exists, meciuri[k][m]['Away'])
                if echipa_home is None or echipa_away is None:
                    print('Nu am gasit echipele pentru aliasul/aliasurile {} si {}\nCompetitie soccerstats {}'
                          '\nCompetitie superbet {}'.format(meciuri[k][m]['Home'], meciuri[k][m]['Away'], exists, k))
                else:
                    if exists not in meciuri_soccerstats.keys():
                        meciuri_soccerstats[exists] = {}
                    meciuri_soccerstats[exists][m] = {}
                    meciuri_soccerstats[exists][m]['Home'] = echipa_home
                    meciuri_soccerstats[exists][m]['Away'] = echipa_away
                    meciuri_soccerstats[exists][m]['Cote'] = meciuri[k][m]['Cote']

    with open(os.path.join(results_folder, 'meciuri_soccerstats.json'), 'wt') as f:
        json.dump(meciuri_soccerstats, f)

    """
    In lista algoritmi ar trebui sa salvez obiecte de tip class care expun o metoda ce primeste ca argumente
    doua echipe team_home si team_away si un fisier de rezultate si intoarce un rezultat.
    Saaaaaaaauuuuuu: As putea face o clasa ce primeste ca argumente o lista de meciuri (cu cele doua echipe aferente)
    si ruleaza algoritmul pe intreaga competitie.
    """
    # algoritmi = [
    #     Algorithm6(meciuri_soccerstats, results_folder)
    # ]

    algoritmi = [Algorithm1(meciuri_soccerstats, results_folder),
                 Algorithm2(meciuri_soccerstats, results_folder),
                 Algorithm2C(meciuri_soccerstats, results_folder),
                 Algorithm3(meciuri_soccerstats, results_folder),
                 Algorithm3C(meciuri_soccerstats, results_folder),
                 Algorithm4(meciuri_soccerstats, results_folder),
                 Algorithm5(meciuri_soccerstats, results_folder),
                 Algorithm6(meciuri_soccerstats, results_folder),
                 Algorithm7(meciuri_soccerstats, results_folder)
                 ]

    result = {}

    for competitie in meciuri.keys():
        if (competitie.strip().lower() + '\n') not in not_interested_competitions and \
                        competitie.strip().lower() not in not_interested_competitions:
            exists = competition_defined(competitie)
            if not isinstance(exists, str):
                print("Competitia {} nu a fost filtrata si nici ignorata (probabil s-a dat skip la filtrare). "
                      "Nu o voi analiza!".format(competitie))
            else:
                for alg in algoritmi:
                    if 'TEST' not in alg.name:
                        accepts_treshold = getattr(alg, "set_probab_treshold", None)
                        if callable(accepts_treshold):
                            alg.set_probab_treshold(85)
                        accepts_points_treshold = getattr(alg, "set_points_treshold", None)
                        if callable(accepts_points_treshold):
                            alg.set_points_treshold(7)
                        accepts_average_treshold = getattr(alg, "set_average_treshold", None)
                        if callable(accepts_average_treshold):
                            alg.set_average_treshold(0.5)
                        winners = alg.analyze(exists)
                        if len(winners[exists].keys()) > 0:
                            # print('='*160)
                            # print('{} - {}'.format(alg.name, exists))
                            # print('-'*160)
                            for k, v in winners[exists].items():
                                # if 'FINAL' in meciuri_soccerstats[exists][k]['Cote'].keys():
                                #     print('{} - {} -> {}'.format(meciuri_soccerstats[exists][k]['Home'] + ' ' + str(meciuri_soccerstats[exists][k]['Cote']['FINAL']['1']),
                                #                                  meciuri_soccerstats[exists][k]['Away'] + ' ' + str(meciuri_soccerstats[exists][k]['Cote']['FINAL']['2']),
                                #                                  v))
                                # else:
                                #     if isinstance(v, dict):
                                #         if len(v.keys()) > 0:
                                #             print('{} - {} -> {}'.format(meciuri_soccerstats[exists][k]['Home'],
                                #                                          meciuri_soccerstats[exists][k]['Away'],
                                #                                          v))
                                #     else:
                                #         if len(v) > 0:
                                #             print('{} - {} -> {}'.format(meciuri_soccerstats[exists][k]['Home'],
                                #                                          meciuri_soccerstats[exists][k]['Away'],
                                #                                          v))
                                if alg.name not in result.keys():
                                    result[alg.name] = {}
                                if exists not in result[alg.name].keys():
                                    result[alg.name][exists] = []
                                result[alg.name][exists].append([meciuri_soccerstats[exists][k]['Home'],
                                                                 meciuri_soccerstats[exists][k]['Away'],
                                                                 v])

                            # print('='*160)
                            # print()
    with open(os.path.join(results_folder, 'predictions.json'), 'wt') as f:
        json.dump(result, f)
    return 0
