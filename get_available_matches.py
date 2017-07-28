import os
import sys
import time
import json
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from selenium.webdriver.chrome.options import Options


_results_folder = None
chromedriver = "chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\atimofte\\AppData\\Local\\Google\\Chrome\\User Data")


def get_results_folder():
    global _results_folder
    if _results_folder is None:
        script_path = os.path.dirname(os.path.realpath(__file__))
        data = datetime.datetime.now()
        _results_folder = os.path.join(script_path, str(data.day).zfill(2) + str(data.month).zfill(2) + str(data.year))
    return _results_folder


def wait_for_elem_by_css(elem):
    try:
        _ = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, elem)))
    except:
        return False
    return True


def end_of_page(bottom_elem):
    weD = bottom_elem.size
    x1 = bottom_elem.location["x"]
    y1 = bottom_elem.location["y"]
    width = 1581
    height = 816

    x = width
    y = height
    x2 = weD['width'] + x1
    y2 = weD['height'] + y1

    return (x2 <= x and y2 <= y)


def get_matches():
    driver = webdriver.Chrome(chromedriver, chrome_options=options)
    driver.implicitly_wait(10)

    pagina = '.custom-filter > li:nth-child({}) > a:nth-child(1)'

    driver.get('https://www.superbet.ro/pariuri-sportive')

    not_interested_competitions = []
    if os.path.isfile('not_interested_competitions.txt'):
        with open('not_interested_competitions.txt', 'rt') as f:
            not_interested_competitions = f.readlines()

    if not os.path.isdir(get_results_folder()):
        os.mkdir(get_results_folder())
    meciuri = {}
    meci = 0

    for pag in range(1, 10):
        driver.execute_script("window.scrollTo(0, 0);")
        wait_for_elem_by_css(pagina.format(pag))
        pag_elem = driver.find_element_by_css_selector(pagina.format(pag))
        if 'toate' not in str(pag_elem.text).lower():
            pag_elem.click()

            but_sporturi = '#sportsinfilter-TGlobal_Sportfilter_Sportsinfilter_XActor > span:nth-child(1) > div:nth-child(2) > button:nth-child(1)'
            but_sport = '.open > ul:nth-child(2) > li:nth-child({}) > a:nth-child(1) > label:nth-child(1)'

            wait_for_elem_by_css(but_sporturi)
            driver.find_element_by_css_selector(but_sporturi).click()
            time.sleep(1)
            wait_for_elem_by_css('.open > ul:nth-child(2)')
            sports_elem = driver.find_element_by_css_selector('.open > ul:nth-child(2)')
            sports = sports_elem.find_elements(By.CSS_SELECTOR, 'li')
            nr_sporturi = len(sports)
            football_exists = False
            wait_for_elem_by_css(but_sport.format(1))
            for i in range(0, nr_sporturi):
                # if wait_for_elem_by_css(sports[i]):
                #     sport_elem = driver.find_element_by_css_selector(but_sport.format(i))
                # if len(str(sport_elem.text).lower().strip()) < 2:
                #     break
                tmp = sports[i].find_element(By.CSS_SELECTOR, 'a')
                tmp2 = tmp.find_element(By.CSS_SELECTOR, 'label')
                if 'fotbal' == str(tmp2.text).lower().strip():
                    sports[i].click()
                    football_exists = True
                    break
            if football_exists:
                bottom_elem = driver.find_element_by_css_selector('.footer-copy > p:nth-child(3)')
                prev_loc = bottom_elem.location["y"]
                count = 0
                body = driver.find_element_by_css_selector('body')
                for i in range(60):
                    body.send_keys(Keys.PAGE_DOWN)
                    if bottom_elem.location["y"] == prev_loc:
                        if count == 10:
                            # Ma duc la sfarsitul paginii pentru ca uneori nu se face scroll pana jos
                            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                            break
                        count += 1
                    prev_loc = bottom_elem.location["y"]
                    time.sleep(.5)

                all_competitions = driver.find_elements(By.CSS_SELECTOR, "div[class='tour']")
                nr_competitions = len(all_competitions)
                step = 10
                index = 0
                while index < nr_competitions:
                    for c in range(index, index + step):
                        if c >= nr_competitions:
                            break
                        all_competitions = driver.find_elements(By.CSS_SELECTOR, "div[class='tour']")
                        competition = all_competitions[c]
                # for competition in all_competitions:
                        competition_name = competition.find_element(By.CSS_SELECTOR, "h1[class='match-title-header'").text
                        if (str(competition_name).lower().strip() in not_interested_competitions):
                            print("Competitie care nu prezinta interes, gasita in not_interested_competitions.txt : " +
                                  str(competition_name))
                        elif str(competition_name).lower().strip().startswith('int. '):
                            print("Competitie care nu prezinta interes (meciuri internationale) : " +
                                  str(competition_name))
                        elif str(competition_name).lower().strip().startswith('int.-'):
                            print("Competitie care nu prezinta interes (meciuri internationale) : " +
                                  str(competition_name))
                        elif str(competition_name).lower().strip().endswith('(f)'):
                            print("Competitie care nu prezinta interes (fotbal feminin) : " +
                                  str(competition_name))
                        elif str(competition_name).lower().strip().startswith('int '):
                            print("Competitie care nu prezinta interes (meciuri internationale) : " +
                                  str(competition_name))
                        else:
                            # Iau toate tabelele cu cote
                            cote_btn = competition.find_element(By.CSS_SELECTOR, 'button')
                            driver.execute_script('arguments[0].scrollIntoView();', competition)
                            body = driver.find_element_by_css_selector('body')
                            for _ in range(5):
                                body.send_keys(Keys.ARROW_UP)
                                time.sleep(.5)
                            cote_btn.click()
                            cote_btn = competition.find_element(By.CSS_SELECTOR,
                                                                "ul[class='multiselect-container dropdown-menu']")
                            toate = cote_btn.find_element(By.CSS_SELECTOR, "input[value='multiselect-all']")
                            toate.click()
                            time.sleep(2)
                            # time.sleep(2)
                            # body.click()

                            cote_dict = {}
                            tabele_cote = competition.find_elements(By.CSS_SELECTOR, "table[class='offer']")
                            nr_tabele = len(tabele_cote)
                            skip_competition = False
                            for t in range(nr_tabele):
                                if skip_competition:
                                    break
                                all_competitions = driver.find_elements(By.CSS_SELECTOR, "div[class='tour']")
                                if c > nr_competitions:
                                    break
                                competition = all_competitions[c]
                                tabele_cote = competition.find_elements(By.CSS_SELECTOR, "table[class='offer']")
                                tab = tabele_cote[t]
                                time.sleep(.1)
                                tip_cote = tab.find_element(By.CSS_SELECTOR, "td[class='bettype']").text.strip()  # Final, DGNG etc.
                                optiuni_elem = tab.find_elements(By.CSS_SELECTOR, 'td[data-original-title]')  # '1' 'X' '2' '1r 1' etc
                                lista_optiuni = []
                                for opt in range(len(optiuni_elem)):
                                    lista_optiuni.append(optiuni_elem[opt].text.strip())

                                meci = 0
                                all_matches = tab.find_elements(By.CSS_SELECTOR, "tr[data-match]")
                                for m in all_matches:
                                    echipe = m.find_element_by_css_selector(css_selector="span[class='match-name']")

                                    txt = echipe.text
                                    if ':' in txt or '(F)' in txt:
                                        print('Match in progress or female team... ' + txt)
                                    else:
                                        if str(competition_name).strip() not in meciuri.keys():
                                            meciuri[str(competition_name).strip()] = {}
                                            print("Competitie: " + str(competition_name).strip())
                                        meci += 1
                                        if str(meci) not in meciuri[str(competition_name).strip()].keys():
                                            meciuri[str(competition_name).strip()][str(meci)] = {}
                                        # print(txt)
                                            echipa1, echipa2 = txt.split(' - ', 1)
                                            meciuri[str(competition_name).strip()][str(meci)]['Home'] = str(echipa1)
                                            meciuri[str(competition_name).strip()][str(meci)]['Away'] = str(echipa2)

                                        # print(txt, " ", )
                                        if 'Cote' not in meciuri[str(competition_name).strip()][str(meci)].keys():
                                            meciuri[str(competition_name).strip()][str(meci)]['Cote'] = {}
                                        if tip_cote not in meciuri[str(competition_name).strip()][str(meci)]['Cote'].keys():
                                            meciuri[str(competition_name).strip()][str(meci)]['Cote'][tip_cote] = {}

                                        cote_list = []
                                        for g in m.find_elements(By.CSS_SELECTOR, "td[class='odd']"):
                                            # print(g.text)
                                            cote_list.append(g.text)
                                        # 1
                                        for cota in range(len(cote_list)):
                                            meciuri[str(competition_name).strip()][str(meci)]['Cote'][tip_cote][lista_optiuni[cota]] = cote_list[cota]
                                # for k, v in meciuri[str(competition_name).strip()][str(meci)]['Cote'].items():
                                #     print(k + ' - ' + str(v))
                    index += step
                    all_competitions = driver.find_elements(By.CSS_SELECTOR, "div[class='tour']")
                    nr_competitions = len(all_competitions)

                    with open(os.path.join(get_results_folder(), 'meciuri.json'), 'wt') as f:
                        json.dump(meciuri, f)


        else:
            break

    driver.quit()

    with open(os.path.join(get_results_folder(), 'meciuri.json'), 'wt') as f:
        json.dump(meciuri, f)

    return os.path.join(get_results_folder(), 'meciuri.json')

# TODO
"""
1. Server - primeste conexiuni, fork, verifica nivelul credentialelor, ofera informatiile la care 
   un client are dreptul.
2. Gatherer - Ia meciurile disponibile de pe superbet.ro, ia cotele, cauta datele fiecarei echipe, 
   trimite mail catre administrator cu lista echipelor pentru care nu s-au putut
   culege datele si motivul (element negasit in pagina, pagina negasita, eroare la accesarea 
   paginii, pagina nedefinita pentru echipa etc.).
3. Analyzer - Ruleaza algorimii implementati pentru fiecare meci si salveaza rezultatele intr-un 
   folder sau intr-o baza de date. Semnaleaza server-ului cand are date noi.
   Optional: analiza rezultatelor prognozate - ce algoritm este mai bun (cele mai multe reusite), 
   cate meciuri din X au fost prognozate corect etc.
4. WatchDog - Se asigura ca cele 3 procese de mai sus nu au crapat (exit code != 0). Daca au crapat 
   incearca repornirea acestora de maxim 3 ori. Pentru fiecare problema trimite mail la admin.
   
5. Client - Foloseste credentiale pentru conectarea la server, primeste datele pe care are dreptul 
   sa le primeasca pe baza nevelului credentialelor oferite si le afiseaza.
   Optional: metode de selectare a celor mai "bune" meciuri - cele mai profitabile (cu cotele cele 
             mai mari), cele mai "sigure" (cu scorul cel mai bun), mediu (scoruri medii), arata doar
             meciuri suficient cat sa se depaseasca o cota totala sau un nivel al profitului 
             prestabilit.
   Probabil ca va fi implementat in C#.
"""
