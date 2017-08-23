import json
import os
import copy
import sys
import time
import datetime
from tkinter import *
import ttk

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0

from db_helper import db_helper as db
from history import db_history as history


def get_results_folder():
    global _results_folder
    if _results_folder is None:
        script_path = os.path.dirname(os.path.realpath(__file__))
        data = datetime.datetime.now()
        _results_folder = os.path.join(script_path, str(data.day).zfill(2) + str(data.month).zfill(2) + str(data.year))
    return _results_folder


def wait_for_elem_by_css(elem):
    global driver
    try:
        _ = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, elem)))
    except:
        return False
    return True


def end_of_page(bottom_elem):
    we_d = bottom_elem.size
    x1 = bottom_elem.location["x"]
    y1 = bottom_elem.location["y"]
    width = 1581
    height = 816

    x = width
    y = height
    x2 = we_d['width'] + x1
    y2 = we_d['height'] + y1

    return x2 <= x and y2 <= y


def competition_defined(compet):
    global competitions_aliases
    if len(competitions_aliases.keys()) < 1:
        return False
    for c, v in competitions_aliases.items():
        if "Aliases" in competitions_aliases[c].keys():
            if compet in competitions_aliases[c]["Aliases"]:
                return c
    return False


main_window = None
alias_home = None
alias_away = None
combo_box_1 = None
combo_box_2 = None
ignored_compet = None


def alias_ok():
    global main_window
    global alias_home
    global alias_away
    global combo_box_1
    global combo_box_2
    alias_home = combo_box_1.get()
    alias_away = combo_box_2.get()
    if '-----' in alias_home:
        alias_home = None
    if '-----' in alias_away:
        alias_away = None
    main_window.destroy()


def alias_cancel():
    global alias_home
    global alias_away
    alias_home = None
    alias_away = None
    main_window.destroy()


def alias_ignore():
    global ignored_compet
    global not_interested_competitions
    not_interested_competitions.append(ignored_compet)
    with open('not_interested_competitions.txt', 'wt') as f:
        for l in not_interested_competitions:
            f.write(l.lower().strip() + '\n')
    ignored_compet = None
    main_window.destroy()


def get_team_alias_from_user(lista_ech, echipa_home, echipa_away, compet):
    """
    Aici ar trebui sa iau si echipa de pe flashscore sa incerc sa fac un match cu o echipa din lista.
    Daca match-ul este 100% aleg automat aliasul (desi nu ar trebui sa se intample pentru ca asta il adaug default
    la creearea cheii corespunzatoare in teams_aliases), daca nu, sa caut cel mai apropiat match si sa il sugerez.
    :param lista_ech:
    :return:
    """
    global main_window
    global alias_home
    global alias_away
    global combo_box_1
    global combo_box_2
    global ignored_compet
    global pattern

    ignored_compet = compet

    main_window = Tk()
    main_window.title('Aliasuri {} si {}'.format(echipa_home, echipa_away))
    Label(main_window, text='Competitie: {}'.format(compet)).grid(column=0, row=0)
    Label(main_window, text='Meci: {} - {}'.format(echipa_home, echipa_away)).grid(column=0, row=1)
    Label(main_window, text='{}'.format(echipa_home)).grid(column=0, row=2)
    Label(main_window, text='{}'.format(echipa_away)).grid(column=2, row=2)
    if len(lista_ech) == 0 or '----------' not in lista_ech[0]:
        lista_ech.insert(0, '----------')
    combo_box_1 = ttk.Combobox(main_window, values=tuple(lista_ech))
    combo_box_1.grid(column=1, row=2)
    combo_box_2 = ttk.Combobox(main_window, values=tuple(lista_ech))
    combo_box_2.grid(column=3, row=2)
    combo_box_1.set(lista_ech[0])
    combo_box_2.set(lista_ech[0])
    if echipa_home in lista_ech:
        combo_box_1.set(echipa_home)
    else:
        e_home = pattern.sub('', echipa_home)
        for ec in lista_ech:
            if e_home.lower() in pattern.sub('', ec):
                combo_box_1.set(ec)
                break

    if echipa_away in lista_ech:
        combo_box_2.set(echipa_away)
    else:
        e_home = pattern.sub('', echipa_home)
        for ec in lista_ech:
            if e_home.lower() in pattern.sub('', ec):
                combo_box_1.set(ec)
                break

    if alias_home is not None and alias_home in lista_ech:
        combo_box_1.set(alias_home)
    if alias_away is not None and alias_away in lista_ech:
        combo_box_2.set(alias_away)

    Button(main_window, text='OK', command=alias_ok).grid(column=1, row=3)
    Button(main_window, text='Cancel', command=alias_cancel).grid(column=3, row=3)
    Button(main_window, text='Ignore this competition', command=alias_ignore).grid(column=4, row=3)
    mainloop()


pattern = re.compile('[\W_]+', re.UNICODE)

chromedriver = "chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\atimofte\\AppData\\Local\\Google\\Chrome\\User Data")

results_folder = None
meciuri = None
meciuri_json = None

def load_matches():
    global edit_box_1
    global main_window
    global results_folder
    global meciuri
    global meciuri_json
    fis = edit_box_1.get()
    if len(fis) < 3:
        main_window.destroy()
        print('Nu s-a introdus calea valida pentru un fisier! S-a introdus "{}"!'.format(fis))
        exit(1)
    meciuri_json = fis
    results_folder = os.path.dirname(os.path.realpath(fis))
    main_window.destroy()

competitions_aliases = {}
teams_aliases = {}
not_interested_competitions = []


def get_results(meciuri_jso):
    global competitions_aliases
    global teams_aliases
    global not_interested_competitions
    global alias_home
    global alias_away
    results_folder = os.path.dirname(os.path.realpath(meciuri_jso))

    if meciuri_jso is None or not os.path.isfile(meciuri_jso):
        print('Nu am gasit fisierul {}!'.format(meciuri_jso))
        exit(1)

    driver = webdriver.Chrome(chromedriver, chrome_options=options)
    driver.get('http://www.flashscore.ro/fotbal')

    with open(meciuri_jso, 'rt') as f:
        meciuri = json.load(f)

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

    current_competitions = []

    for competitie in sorted(meciuri.keys()):
        if (competitie.strip().lower() + '\n') not in not_interested_competitions and \
                        competitie.strip().lower() not in not_interested_competitions:
            exists = competition_defined(competitie)
            if not isinstance(exists, str):
                print(
                    "stop - Opreste actualizarile\nignore - ignora aceasta competitie\nskip - ignora aceasta competite doar"
                    " la aceasta rulare\nENTER - cauta link-ul in adressbar-ul browser-ului!\n")
                link = str(input(
                    "Nu am gasit competitia {} definita! Introduceti link-ul catre aceasta competitie de pe "
                    "flashscore.ro. Trebuie sa contina 'flashscore.ro/fotbal/':\n".format(
                        competitie))).strip()
                if (len(str(link)) > 0) and ("flashscore.ro/fotbal/" in str(link)):
                    parti_link = link.rstrip('/').split('/')
                    comp_soccerstats = '-'.join([parti_link[-2].strip(), parti_link[-1].strip()])
                    print(comp_soccerstats)
                    if comp_soccerstats not in competitions_aliases.keys():
                        competitions_aliases[comp_soccerstats] = {}
                        competitions_aliases[comp_soccerstats]["Aliases"] = [competitie]
                        competitions_aliases[comp_soccerstats]["Link"] = link
                    else:
                        competitions_aliases[comp_soccerstats]["Aliases"].append(competitie)
                elif "ignore" == str(link).strip().lower():
                    print("Voi ignora de acum inainte competitia {}!".format(competitie))
                    not_interested_competitions.append(competitie)
                elif "stop" == str(link).strip().lower():
                    print(
                        "Ma opresc din actualizat competitiile! Competitiile neactualizate vor fi solicitate la "
                        "urmatoarea rulare!")
                    break
                elif "skip" == str(link).strip().lower():
                    print("Sar peste competitia {}! Se va cere actualizarea la urmatoarea rulare!".format(competitie))
                else:
                    link = str(driver.current_url).strip()
                    if (len(link) > 0) and ("flashscore.ro/fotbal/" in link):
                        parti_link = link.rstrip('/').split('/')
                        comp_soccerstats = '-'.join([parti_link[-2].strip(), parti_link[-1].strip()])
                        print(comp_soccerstats)
                        if comp_soccerstats not in competitions_aliases.keys():
                            competitions_aliases[comp_soccerstats] = {}
                            competitions_aliases[comp_soccerstats]["Aliases"] = [competitie]
                            competitions_aliases[comp_soccerstats]["Link"] = link
                            current_competitions.append(comp_soccerstats)
                        else:
                            competitions_aliases[comp_soccerstats]["Aliases"].append(competitie)

                    else:
                        print(
                            "Nu am primit un link cu format valid pentru competitia {}. Voi considera ca nu se doreste"
                            " introducerea unui link la acest moment si voi trece la urmatoarea competitie!".format(
                                competitie))
            else:
                print("Am gasit competitia {}. Datele pentru aceasta sunt: {}".format(competitie,
                                                                                      competitions_aliases[exists]))
                current_competitions.append(exists)

            # Aici ar fi fost OK sa parcurg echipele din competitia curenta sa le gasesc alias-ul
            # Nu pot face asta pentru ca inca nu am cules rezultatele si deci nu am numele echipelor de pe soccerstats
        else:
            print("Competitia {} nu prezinta interes! Gasita in not_interested_competitions.txt!".format(competitie))

        # break
        # TODO De scos break-ul de mai sus. L-am pus ca sa ia doar prima competitie


    if len(competitions_aliases.keys()) > 0:
        with open('competitions_aliases.json', 'wt') as f:
            json.dump(competitions_aliases, f)

    with open('not_interested_competitions.txt', 'wt') as f:
        for l in not_interested_competitions:
            f.write(l.lower().strip() + '\n')

    print("Am terminat de actualizat competitiile!\nIncepem cu echipele!")

    # gather = 'N'
    # if 'N' in gather:
    #     print('Nu culeg rezultatele curente pentru competitiile in curs.')
    # elif 'Y' in gather.upper():

    if not os.path.isfile(os.path.join(results_folder, 'archive_final.json')):
        total_competitii = len(current_competitions)
        curr_comp = 0
        for competitie in current_competitions:
            curr_comp += 1
            print("Competitie {}/{}".format(curr_comp, total_competitii))
            if competitie not in teams_aliases.keys():
                teams_aliases[competitie] = {}
        #         print("Adun rezultatele pentru competitia {}".format(competitie))
        #         # Incerc sa iau echipele din aceasta competitie
            print("Incerc sa iau echipele din aceasta competitie")
            count = 0
            ex = Exception()
            while count < 3:
                try:
                    driver.get(competitions_aliases[competitie]["Link"] + 'echipe/')
                    wait_for_elem_by_css('#tournament-page-participants > table:nth-child(1) > tbody:nth-child(3)')
                    tabel_echipe = driver.find_element_by_css_selector('#tournament-page-participants > table:nth-child(1) > tbody:nth-child(3)')
                    lista_elemente_echipe = tabel_echipe.find_elements(By.CSS_SELECTOR, "td[class='tp']")
                    for team in lista_elemente_echipe:
                        ht = str(team.text).replace("'", "`")
                        if ht not in teams_aliases[competitie].keys():
                            teams_aliases[competitie][ht] = [ht]
                        else:
                            if ht not in teams_aliases[competitie][ht]:
                                teams_aliases[competitie][ht].append(ht)
                        print(ht)
                    break
                except Exception as e:
                    ex = e
                    print('Exceptie la incercarea de a lua echipele ({})'.format(e.args))
                    count += 1
                    driver.refresh()
                    time.sleep(5)
            if count == 3:
                raise ex
    #
    #         count = 0
    #         ex = Exception()
    #         while count < 3:
    #             try:
    #                 driver.get(competitions_aliases[competitie]["Link"] + 'rezultate/')
    #                 break
    #             except Exception as e:
    #                 ex = e
    #                 print('Exceptie la incercarea de a lua rezultatele ({})'.format(e.args))
    #                 count += 1
    #         if count == 3:
    #             raise ex
    #
    #         wait_for_elem_by_css('table.soccer > tbody:nth-child(3)')  # tabelul cu rezultate
    #         more_games = True
    #         while more_games:
    #             more_games = False
    #             try:
    #                 more_results = driver.find_element_by_css_selector('#tournament-page-results-more > tbody > tr > td > a')
    #                 driver.execute_script('arguments[0].scrollIntoView();', more_results)
    #                 time.sleep(0.5)
    #                 more_results.click()
    #                 time.sleep(3)
    #                 more_games = True
    #             except:
    #                 pass
    #
    #         tabele_rezultate = driver.find_elements(By.CSS_SELECTOR, "table[class='soccer'")
    #         rezultate_elements_list = []
    #         for tabel in range(len(tabele_rezultate)):
    #             rezultate_tabel = tabele_rezultate[tabel].find_element_by_css_selector('tbody')
    #             rezultate_meciuri = rezultate_tabel.find_elements(By.CSS_SELECTOR, "tr")
    #             for i in range(len(rezultate_meciuri)):
    #                 if 'event_round' in rezultate_meciuri[i].get_attribute('class'):
    #                     if 'runda' in str(rezultate_meciuri[i].text).lower():
    #                         rezultate_elements_list.append(rezultate_meciuri[i].find_element(By.TAG_NAME, 'td').text)
    #                     else:
    #                         rezultate_elements_list.append('Runda X')
    #                 else:
    #                     rezultate_elements_list.append(rezultate_meciuri[i].get_attribute('id').split('_')[-1])
    #
    #         runda = 0
    #         for entry in range(len(rezultate_elements_list) - 1, -1, -1):
    #             if 'runda' in rezultate_elements_list[entry].lower():
    #                 try:
    #                     runda = int(rezultate_elements_list[entry].split()[-1])
    #                 except:
    #                     runda += 1
    #                     rezultate_elements_list[entry] = 'Runda ' + str(runda)
    #
    #         runda = 0
    #         for r in rezultate_elements_list:
    #             if 'runda' in r.lower():
    #                 runda = int(r.split()[-1])
    #             else:
    #                 if not db.match_has_results(r):
    #                     count = 0
    #                     ex = Exception()
    #                     while count < 3:
    #                         try:
    #                             driver.get('http://www.flashscore.ro/meci/{}/#sumar-meci'.format(r))
    #                             break
    #                         except Exception as e:
    #                             ex = e
    #                             print('Exceptie la incercarea de a lua rezultatele 2 ({})'.format(e.args))
    #                             count += 1
    #                     if count == 3:
    #                         raise ex
    #
    #                     wait_for_elem_by_css('.tname-home > span:nth-child(1) > a:nth-child(2)')
    #                     wait_for_elem_by_css('.tname-away > span:nth-child(1) > a:nth-child(1)')
    #                     home_team = ''
    #                     while len(home_team) == 0:
    #                         home_team = driver.find_element_by_css_selector(
    #                             '.tname-home > span:nth-child(1) > a:nth-child(2)').text
    #                         if len(home_team) == 0:
    #                             time.sleep(.5)
    #                     away_team = ''
    #                     while len(away_team) == 0:
    #                         away_team = driver.find_element_by_css_selector(
    #                             '.tname-away > span:nth-child(1) > a:nth-child(1)').text
    #                         if len(away_team) == 0:
    #                             time.sleep(.5)
    #                     home_team = home_team.replace("'", "`")
    #                     away_team = away_team.replace("'", "`")
    #                     if home_team not in teams_aliases[competitie].keys():
    #                         teams_aliases[competitie][home_team] = [home_team]
    #                     else:
    #                         if home_team not in teams_aliases[competitie][home_team]:
    #                             teams_aliases[competitie][home_team].append(home_team)
    #
    #                     if away_team not in teams_aliases[competitie].keys():
    #                         teams_aliases[competitie][away_team] = [away_team]
    #                     else:
    #                         if away_team not in teams_aliases[competitie][away_team]:
    #                             teams_aliases[competitie][away_team].append(away_team)
    #                     skip = False
    #                     try:
    #                         results_table = driver.find_element_by_css_selector('#parts > tbody')
    #                         rep_elems = results_table.find_elements(By.CSS_SELECTOR, "td[class='h-part'")
    #                         if len(rep_elems) < 2:
    #                             print("Meciul {} nu are rezultate pentru ambele reprize!")
    #                             skip = True
    #                         txts = []
    #                         for rep in rep_elems:
    #                             txts.append(rep.text.lower())
    #                         if 'repriza 1' not in txts or 'repriza 2' not in txts:
    #                             print("Meciul {} nu are rezultate pentru ambele reprize!".format(r))
    #                             skip = True
    #                     except:
    #                         skip = True
    #                         print('Exceptie la gasirea textelor pentru reprize!')
    #                     fh_ht_score = -1
    #                     fh_at_score = -1
    #                     sh_ht_score = -1
    #                     sh_at_score = -1
    #                     try:
    #                         fh_ht_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p1_home'").text)
    #                     except:
    #                         pass
    #                     try:
    #                         fh_at_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p1_away'").text)
    #                     except:
    #                         pass
    #                     try:
    #                         sh_ht_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p2_home'").text)
    #                     except:
    #                         pass
    #                     try:
    #                         sh_at_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p2_away'").text)
    #                     except:
    #                         pass
    #
    #                     if not skip:
    #                         if fh_ht_score == -1 or fh_at_score == -1 or sh_ht_score == -1 or sh_at_score == -1:
    #                             try:
    #                                 info = driver.find_element_by_css_selector('#info-row > td > span > span.text')
    #                                 # Am gasit informatii despre joc cum ca s-ar fi anulat sau amanat. Nu-l mai iau in considerare
    #                                 skip = True
    #                             except:
    #                                 if fh_ht_score == -1:
    #                                     print('Nu am putut lua scorul pentru {} pentru prima repriza a meciului {} - {} id={} '
    #                                           'si nu am gasit info! Pun 0!'.format(home_team, home_team, away_team, r))
    #                                     fh_ht_score = 0
    #                                 if fh_at_score == -1:
    #                                     print('Nu am putut lua scorul pentru {} pentru prima repriza a meciului {} - {} id={} '
    #                                           'si nu am gasit info! Pun 0!'.format(away_team, home_team, away_team, r))
    #                                     fh_at_score = 0
    #                                 if sh_ht_score == -1:
    #                                     print('Nu am putut lua scorul pentru {} pentru a doua repriza a meciului {} - {} id={} '
    #                                           'si nu am gasit info! Pun 0!'.format(home_team, home_team, away_team, r))
    #                                     sh_ht_score = 0
    #                                 if sh_at_score == -1:
    #                                     print('Nu am putut lua scorul pentru {} pentru a doua repriza a meciului {} - {} id={} '
    #                                           'si nu am gasit info! Pun 0!'.format(away_team, home_team, away_team, r))
    #                                     sh_at_score = 0
    #                                 pass
    #                     if skip:
    #                         print('Sar peste meciul {} - {} id={}. Nu am putut lua scorul pentru '
    #                               'ambele reprize!'.format(home_team, away_team, r))
    #                     else:
    #                         db.add_match(competitie,
    #                                      runda,
    #                                      r,
    #                                      home_team,
    #                                      away_team,
    #                                      fh_ht_score,
    #                                      fh_at_score,
    #                                      sh_ht_score,
    #                                      sh_at_score)

    # driver.quit()

    if len(competitions_aliases.keys()) > 0:
        with open('competitions_aliases.json', 'wt') as f:
            json.dump(competitions_aliases, f)
    with open('not_interested_competitions.txt', 'wt') as f:
        for l in not_interested_competitions:
            f.write(l.lower().strip() + '\n')

    # Am pus si aici o salvare a aliasurilor echipelor pentru ca e posibil sa se modifice la actualizarea competitiilor
    if len(teams_aliases.keys()) > 0:
        with open('teams_aliases.json', 'wt') as f:
            json.dump(teams_aliases, f)


    for competitie in meciuri.keys():
        if (competitie.strip().lower() + '\n') not in not_interested_competitions and \
                        competitie.strip().lower() not in not_interested_competitions:
            exists = competition_defined(competitie)
            # Exists este False daca nu am gasit competitia si str (numele competitiei de pe soccerstats daca am gasit-o)
            # Avand in vedere ca tocmai am parcurs competitiile, exists == False este posibil doar daca am oprit parcurgerea
            # competitiilor sau am dat skip la asta
            if isinstance(exists, str):
                # Am competitia definita
                # Codul de mai jos se ruleaza la parcurgerea competitiilor
                lista_echipe = db.get_competition_teams(exists)
                # Adaug la lista echipelor si acele echipe care nu figureaza in baza de date pentru ca nu au nici un
                # meci jucat pana in prezent. Acele echipe au fost culese la adunarea rezultatelor

                if exists in teams_aliases.keys() and len(teams_aliases[exists].keys()) > 0:
                    lista_echipe.extend(teams_aliases[exists].keys())
                    lista_echipe = sorted([x for x in set(lista_echipe)])

                if exists not in teams_aliases.keys():
                    teams_aliases[exists] = {}
                for echipa in lista_echipe:
                    if echipa not in teams_aliases[exists].keys():
                        teams_aliases[exists][echipa] = [echipa]

                for index in meciuri[competitie]:
                    echipa_home = meciuri[competitie][index]["Home"]
                    echipa_away = meciuri[competitie][index]["Away"]
                    alias_home = None
                    for echipa in teams_aliases[exists].keys():
                        if echipa_home in teams_aliases[exists][echipa]:
                            alias_home = echipa
                            break

                    alias_away = None
                    for echipa in teams_aliases[exists].keys():
                        if echipa_away in teams_aliases[exists][echipa]:
                            alias_away = echipa
                            break
                    # De optimizat: metoda separata + o singura parcurgere a teams_aliases, desi nu stiu cat de
                    # time-consuming este

                    if (alias_away is None) or (alias_home is None):
                        # Am o echipa care nu are aliasul gasit
                        # Fac verificarea de mai sus pentru a evita constituirea listei de echipe inutil
                        get_team_alias_from_user(lista_echipe, echipa_home, echipa_away, competitie)
                        if alias_home is not None and len(alias_home) > 0:
                            teams_aliases[exists][alias_home].append(echipa_home)
                        if alias_away is not None and len(alias_away) > 0:
                            teams_aliases[exists][alias_away].append(echipa_away)
            else:
                # Nu am competitia definita
                print('Competitia {} nu este definita! Fie s-a sarit peste ea la actualizare fie s-a dorit oprirea '
                      'actualizarilor! Sar si aici peste ea!'.format(competitie))
    if len(teams_aliases.keys()) > 0:
        with open('teams_aliases.json', 'wt') as f:
            json.dump(teams_aliases, f)


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
                    # meciuri_soccerstats[exists][m]['Cote'] = meciuri[k][m]['Cote']

    with open(os.path.join(results_folder, 'meciuri_soccerstats.json'), 'wt') as f:
        json.dump(meciuri_soccerstats, f)

    if os.path.isfile('teams_aliases.json'):
        with open('teams_aliases.json', 'rt') as f:
            teams_aliases = json.load(f)
    archive = {}
    if os.path.isfile(os.path.join(results_folder, 'archive_partial.json')):
        with open(os.path.join(results_folder, 'archive_partial.json'), 'rt') as f:
            archive = json.load(f)
    else:
        for competitie in meciuri.keys():
            if (competitie.strip().lower() + '\n') not in not_interested_competitions and \
                            competitie.strip().lower() not in not_interested_competitions:
                exists = competition_defined(competitie)
                # Exists este False daca nu am gasit competitia si str (numele competitiei de pe soccerstats daca am gasit-o)
                # Avand in vedere ca tocmai am parcurs competitiile, exists == False este posibil doar daca am oprit parcurgerea
                # competitiilor sau am dat skip la asta
                if isinstance(exists, str):
                    print(competitie)
                    # archive[exists] = {}
                    link = competitions_aliases[exists]['Link'] + 'meciuri/'

                    count = 0
                    ex = Exception()
                    while count < 3:
                        try:
                            driver.get(link)
                            break
                        except Exception as e:
                            ex = e
                            print('Exceptie la incercarea de a lua meciurile ({})'.format(e.args))
                            count += 1
                            driver.refresh()
                            time.sleep(5)

                    if count == 3:
                        raise ex

                    wait_for_elem_by_css('table.soccer > tbody:nth-child(3)')
                    try:
                        tabel_meciuri = driver.find_element_by_css_selector('table.soccer > tbody:nth-child(3)')
                    except:
                        continue
                    meciuri_viitoare = tabel_meciuri.find_elements(By.CSS_SELECTOR, 'tr')
                    max_meciuri = len(meciuri_viitoare)
                    for tr_meci in range(min(10, max_meciuri)):
                        tr_meci = meciuri_viitoare[tr_meci]
                        for m in meciuri[competitie]:
                            echipa_home = get_team_name_from_alias(exists, meciuri[competitie][m]['Home'])
                            echipa_away = get_team_name_from_alias(exists, meciuri[competitie][m]['Away'])
                            try:
                                id = tr_meci.get_attribute('id')
                                id = id.split('_')[-1]
                                home_team = tr_meci.find_element(By.CSS_SELECTOR, "span[class='padr'").text
                                away_team = tr_meci.find_element(By.CSS_SELECTOR, "span[class='padl'").text
                                # print(home_team + ' - ' + echipa_home)
                                # print(away_team + ' - ' + echipa_away)
                                if (home_team.strip() in echipa_home) and (away_team.strip() in echipa_away):
                                    if exists not in archive.keys():
                                        archive[exists] = {}
                                    archive[exists][m] = {}
                                    archive[exists][m]['Home'] = echipa_home
                                    archive[exists][m]['Away'] = echipa_away
                                    archive[exists][m]['MatchID'] = id
                                    print(archive[exists][m])
                            except:
                                pass
        print(archive)
        with open(os.path.join(results_folder, 'archive_partial.json'), 'wt') as f:
            json.dump(archive, f)

    total_meciuri = 0
    for _, v in archive.items():
        total_meciuri += len(v.keys())

    if os.path.isfile(os.path.join(results_folder, 'archive_final.json')):
        with open(os.path.join(results_folder, 'archive_final.json'), 'rt') as f:
            final_archive = json.load(f)
    else:
        final_archive = copy.deepcopy(archive)

    curr_meci = 0
    while len(archive.keys()):
        competitie = list(archive.keys())[0]
    # for competitie in archive.keys():
        print('Archive - {}'.format(competitie))
        while len(archive[competitie].keys()):
            m = list(archive[competitie].keys())[0]
        # for m in archive[competitie].keys():
            curr_meci += 1
            print("Meci {}/{}".format(curr_meci, total_meciuri))
            count = 0
            ex = Exception()
            while count < 3:
                try:
                    driver.get('http://www.flashscore.ro/meci/{}/#h2h;home'.format(archive[competitie][m]['MatchID']))
                    break
                except Exception as e:
                    ex = e
                    print('Exceptie la incercarea de a lua meciurile ({})'.format(e.args))
                    count += 1
                    driver.refresh()
                    time.sleep(5)

            if count == 3:
                raise ex
            wait_for_elem_by_css('.tname-home > span:nth-child(1) > a:nth-child(2)')
            wait_for_elem_by_css('.tname-away > span:nth-child(1) > a:nth-child(1)')
            home_team = ''
            while len(home_team) == 0:
                home_team = driver.find_element_by_css_selector(
                    '.tname-home > span:nth-child(1) > a:nth-child(2)').text
                if len(home_team) == 0:
                    time.sleep(.5)
            away_team = ''
            while len(away_team) == 0:
                away_team = driver.find_element_by_css_selector(
                    '.tname-away > span:nth-child(1) > a:nth-child(1)').text
                if len(away_team) == 0:
                    time.sleep(.5)
            print('Istoric home {} - {}'.format(home_team, away_team))
            wait_for_elem_by_css('#tab-h2h-home > table:nth-child(1) > tbody:nth-child(3)')  # tabelul cu rezultate
            tabel_rezultate_home = driver.find_element(By.CSS_SELECTOR, "#tab-h2h-home > table:nth-child(1) > tbody:nth-child(3)")
            rezultate_home = tabel_rezultate_home.find_elements(By.CSS_SELECTOR, 'tr[class]')
            iduri_rezultate_home = []
            for rez in range(min(10, len(rezultate_home))):
                if 'highlight' in rezultate_home[rez].get_attribute('class'):
                    id = rezultate_home[rez].get_attribute('onclick').split('(')[-1].split("'")[1].split('_')[-1]
                    iduri_rezultate_home.append(id)
            final_archive[competitie][m]['IDuri_Home'] = copy.deepcopy(iduri_rezultate_home)

            print('Istoric away {} - {}'.format(home_team, away_team))
            count = 0
            ex = Exception()
            while count < 3:
                try:
                    driver.get('http://www.flashscore.ro/meci/{}/#h2h;away'.format(archive[competitie][m]['MatchID']))
                    break
                except Exception as e:
                    ex = e
                    print('Exceptie la incercarea de a lua meciurile ({})'.format(e.args))
                    count += 1
                    driver.refresh()
                    time.sleep(5)

            if count == 3:
                raise ex
            wait_for_elem_by_css('.tname-home > span:nth-child(1) > a:nth-child(2)')
            wait_for_elem_by_css('.tname-away > span:nth-child(1) > a:nth-child(1)')
            home_team = ''
            while len(home_team) == 0:
                home_team = driver.find_element_by_css_selector(
                    '.tname-home > span:nth-child(1) > a:nth-child(2)').text
                if len(home_team) == 0:
                    time.sleep(.5)
            away_team = ''
            while len(away_team) == 0:
                away_team = driver.find_element_by_css_selector(
                    '.tname-away > span:nth-child(1) > a:nth-child(1)').text
                if len(away_team) == 0:
                    time.sleep(.5)
            wait_for_elem_by_css('table.h2h_away:nth-child(1) > tbody:nth-child(3)')  # tabelul cu rezultate
            tabel_rezultate_away = driver.find_element(By.CSS_SELECTOR, "table.h2h_away:nth-child(1) > tbody:nth-child(3)")
            rezultate_away = tabel_rezultate_away.find_elements(By.CSS_SELECTOR, 'tr[class]')
            iduri_rezultate_away = []
            for rez in range(min(10, len(rezultate_away))):
                if 'highlight' in rezultate_away[rez].get_attribute('class'):
                    id = rezultate_away[rez].get_attribute('onclick').split('(')[-1].split("'")[1].split('_')[-1]
                    iduri_rezultate_away.append(id)
            final_archive[competitie][m]['IDuri_Away'] = copy.deepcopy(iduri_rezultate_away)

            print('Istoric H2H {} - {}'.format(home_team, away_team))
            wait_for_elem_by_css('#tab-h2h-away > table:nth-child(2) > tbody:nth-child(3)')  # tabelul cu rezultate
            tabel_rezultate_h2h = driver.find_element(By.CSS_SELECTOR, "#tab-h2h-away > table:nth-child(2) > tbody:nth-child(3)")
            rezultate_h2h = tabel_rezultate_h2h.find_elements(By.CSS_SELECTOR, 'tr[class]')
            iduri_rezultate_h2h = []
            for rez in range(min(10, len(rezultate_h2h))):
                if 'highlight' in rezultate_h2h[rez].get_attribute('class'):
                    id = rezultate_h2h[rez].get_attribute('onclick').split('(')[-1].split("'")[1].split('_')[-1]
                    iduri_rezultate_h2h.append(id)
            final_archive[competitie][m]['IDuri_H2H'] = copy.deepcopy(iduri_rezultate_h2h)

            # Acum iau rezultatul pentru aceste meciuri din arhiva
            print('Meciuri home_team...')
            for r in final_archive[competitie][m]['IDuri_Home']:
                if history.get_match(r) is None:
                    count = 0
                    ex = Exception()
                    while count < 3:
                        try:
                            driver.get('http://www.flashscore.ro/meci/{}/#sumar-meci'.format(r))
                            break
                        except Exception as e:
                            ex = e
                            print('Exceptie la incercarea de a lua meciurile ({})'.format(e.args))
                            count += 1
                            driver.refresh()
                            time.sleep(5)

                    if count == 3:
                        raise ex
                    wait_for_elem_by_css('.tname-home > span:nth-child(1) > a:nth-child(2)')
                    wait_for_elem_by_css('.tname-away > span:nth-child(1) > a:nth-child(1)')
                    home_team = ''
                    while len(home_team) == 0:
                        home_team = driver.find_element_by_css_selector(
                            '.tname-home > span:nth-child(1) > a:nth-child(2)').text
                        if len(home_team) == 0:
                            time.sleep(.5)
                    away_team = ''
                    while len(away_team) == 0:
                        away_team = driver.find_element_by_css_selector(
                            '.tname-away > span:nth-child(1) > a:nth-child(1)').text
                        if len(away_team) == 0:
                            time.sleep(.5)
                    home_team = home_team.replace("'", "`")
                    away_team = away_team.replace("'", "`")
                    print('Istoric home {} - {}'.format(home_team, away_team))
                    fh_ht_score = -1
                    fh_at_score = -1
                    sh_ht_score = -1
                    sh_at_score = -1
                    try:
                        results_table = driver.find_element_by_css_selector('#parts > tbody:nth-child(1)')
                    except:
                        continue
                    try:
                        fh_ht_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p1_home'").text)
                    except:
                        pass
                    try:
                        fh_at_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p1_away'").text)
                    except:
                        pass
                    try:
                        sh_ht_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p2_home'").text)
                    except:
                        pass
                    try:
                        sh_at_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p2_away'").text)
                    except:
                        pass
                    # if 'Rezultate_Home' not in final_archive[competitie][m].keys():
                    #     final_archive[competitie][m]['Rezultate_Home'] = []
                    # final_archive[competitie][m]['Rezultate_Home'].append([home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score])
                    history.add_match(r, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score)
                # else:
                #     print('Am deja infomatiile pentru id={}'.format(r))

            # Acum iau rezultatul pentru aceste meciuri din arhiva
            print('Meciuri away_team...')
            for r in final_archive[competitie][m]['IDuri_Away']:
                if history.get_match(r) is None:
                    count = 0
                    ex = Exception()
                    while count < 3:
                        try:
                            driver.get('http://www.flashscore.ro/meci/{}/#sumar-meci'.format(r))
                            break
                        except Exception as e:
                            ex = e
                            print('Exceptie la incercarea de a lua meciurile ({})'.format(e.args))
                            count += 1
                            driver.refresh()
                            time.sleep(5)

                    if count == 3:
                        raise ex
                    wait_for_elem_by_css('.tname-home > span:nth-child(1) > a:nth-child(2)')
                    wait_for_elem_by_css('.tname-away > span:nth-child(1) > a:nth-child(1)')
                    home_team = ''
                    while len(home_team) == 0:
                        home_team = driver.find_element_by_css_selector(
                            '.tname-home > span:nth-child(1) > a:nth-child(2)').text
                        if len(home_team) == 0:
                            time.sleep(.5)
                    away_team = ''
                    while len(away_team) == 0:
                        away_team = driver.find_element_by_css_selector(
                            '.tname-away > span:nth-child(1) > a:nth-child(1)').text
                        if len(away_team) == 0:
                            time.sleep(.5)
                    home_team = home_team.replace("'", "`")
                    away_team = away_team.replace("'", "`")
                    print('Istoric away {} - {}'.format(home_team, away_team))

                    fh_ht_score = -1
                    fh_at_score = -1
                    sh_ht_score = -1
                    sh_at_score = -1
                    try:
                        results_table = driver.find_element_by_css_selector('#parts > tbody:nth-child(1)')
                    except:
                        continue
                    try:
                        fh_ht_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p1_home'").text)
                    except:
                        pass
                    try:
                        fh_at_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p1_away'").text)
                    except:
                        pass
                    try:
                        sh_ht_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p2_home'").text)
                    except:
                        pass
                    try:
                        sh_at_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p2_away'").text)
                    except:
                        pass
                    # if 'Rezultate_Away' not in final_archive[competitie][m].keys():
                    #     final_archive[competitie][m]['Rezultate_Away'] = []
                    # final_archive[competitie][m]['Rezultate_Away'].append([home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score])
                    history.add_match(r, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score)
                # else:
                #     print('Am deja infomatiile pentru id={}'.format(r))



            # Acum iau rezultatul pentru aceste meciuri din arhiva
            print('Meciuri H2H...')
            for r in final_archive[competitie][m]['IDuri_H2H']:
                if history.get_match(r) is None:
                    count = 0
                    ex = Exception()
                    while count < 3:
                        try:
                            driver.get('http://www.flashscore.ro/meci/{}/#sumar-meci'.format(r))
                            break
                        except Exception as e:
                            ex = e
                            print('Exceptie la incercarea de a lua meciurile ({})'.format(e.args))
                            count += 1
                            driver.refresh()
                            time.sleep(5)

                    if count == 3:
                        raise ex
                    wait_for_elem_by_css('.tname-home > span:nth-child(1) > a:nth-child(2)')
                    wait_for_elem_by_css('.tname-away > span:nth-child(1) > a:nth-child(1)')
                    home_team = ''
                    tick = 0
                    while len(home_team) == 0 and tick < 120:
                        home_team = driver.find_element_by_css_selector(
                            '.tname-home > span:nth-child(1) > a:nth-child(2)').text
                        if len(home_team) == 0:
                            time.sleep(.5)
                            tick += 1
                    if len(home_team) == 0:
                        continue
                    away_team = ''
                    tick = 0
                    while len(away_team) == 0 and tick < 120:
                        away_team = driver.find_element_by_css_selector(
                            '.tname-away > span:nth-child(1) > a:nth-child(1)').text
                        if len(away_team) == 0:
                            time.sleep(.5)
                            tick += 1
                    if len(away_team) == 0:
                        continue
                    home_team = home_team.replace("'", "`")
                    away_team = away_team.replace("'", "`")
                    print('Istoric H2H {} - {}'.format(home_team, away_team))

                    fh_ht_score = -1
                    fh_at_score = -1
                    sh_ht_score = -1
                    sh_at_score = -1
                    try:
                        results_table = driver.find_element_by_css_selector('#parts > tbody:nth-child(1)')
                    except:
                        continue
                    try:
                        fh_ht_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p1_home'").text)
                    except:
                        pass
                    try:
                        fh_at_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p1_away'").text)
                    except:
                        pass
                    try:
                        sh_ht_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p2_home'").text)
                    except:
                        pass
                    try:
                        sh_at_score = int(results_table.find_element(By.CSS_SELECTOR, "span[class='p2_away'").text)
                    except:
                        pass
                    # if 'Rezultate_H2H' not in final_archive[competitie][m].keys():
                    #     final_archive[competitie][m]['Rezultate_H2H'] = []
                    # final_archive[competitie][m]['Rezultate_H2H'].append([home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score])
                    history.add_match(r, home_team, away_team, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score)
                # else:
                #     print('Am deja infomatiile pentru id={}'.format(r))

            archive[competitie].pop(m, None)
            with open(os.path.join(results_folder, 'archive_partial.json'), 'wt') as f:
                json.dump(archive, f)

            with open(os.path.join(results_folder, 'archive_final.json'), 'wt') as f:
                json.dump(final_archive, f)

        archive.pop(competitie, None)
        with open(os.path.join(results_folder, 'archive_partial.json'), 'wt') as f:
            json.dump(archive, f)

    with open(os.path.join(results_folder, 'archive_final.json'), 'wt') as f:
        json.dump(final_archive, f)


    driver.quit()
    return 0

