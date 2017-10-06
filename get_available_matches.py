import os
import subprocess
import time
import json
import datetime
import copy
import traceback
import unicodedata
from queue import Queue

from db_helper import DBInterface
from stats_provider import StatsProvider
from constants import *
from Algorithm5 import Algorithm5
from Algorithm6 import Algorithm6

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


_results_folder = None
chromedriver = "chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\atimofte\\AppData\\Local\\Google\\Chrome\\User Data")


def wait_for_elem_by_css(driver, elem, timeout=2):
    try:
        _ = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, elem)))
    except Exception as e:
        # print(e.args)
        # traceback.print_tb(e.__traceback__)
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


def get_scores(driver, hover_element, interess_team):
    ht_fh_score = -1
    at_fh_score = -1
    ht_sh_score = -1
    at_sh_score = -1
    home_match = None

    if driver is None:
        return ht_fh_score, at_fh_score, ht_sh_score, at_sh_score, home_match
    ht_fh_id = "td[class='home p1 first ']"
    at_fh_id = "td[class='away p1 ']"
    ht_sh_id = "td[class='home ft first ']"
    at_sh_id = "td[class='away ft ']"

    split_score = True
    """
    Daca dureaza mai mult de cinci secunde ca selenium sa gaseasca un element, inseamna ca nu exista, si cauta in tot
    DOM-ul.
    Trebuie sa observ pentru fiecare meci si daca a fost jucat acasa sau in deplasare pentru ca e posibil ca unii
    algoritmi sa faca distinctie intre meciurile jucate acasa si cele jucate in deplasare.
    """
    timeout = 5
    for _ in range(20):
        if home_match is None:
            try:
                home_team_name = driver.find_element_by_css_selector("td[class='hometeam first ']").text
                if len(home_team_name.strip()):
                    if interess_team.lower().strip() in home_team_name.lower().strip():
                        home_match = True
                    else:
                        home_match = False
            except Exception as e:
                pass
        if split_score:
            if ht_fh_score == -1:
                init_time = int(time.time())
                try:
                    ht_fh_score = int(driver.find_element_by_css_selector(ht_fh_id).text)
                except:
                    new_time = int(time.time())
                    if (new_time - init_time) > timeout:
                        split_score = False
                    time.sleep(.1)
        else:
            print("Skiping ht_fh_score search!")
        if split_score:
            if at_fh_score == -1:
                try:
                    at_fh_score = int(driver.find_element_by_css_selector(at_fh_id).text)
                except:
                    time.sleep(.1)
        else:
            print("Skiping at_fh_score search!")

        if ht_sh_score == -1:
            try:
                ht_sh_score = int(driver.find_element_by_css_selector(ht_sh_id).text)
            except:
                time.sleep(.1)
        if at_sh_score == -1:
            try:
                at_sh_score = int(driver.find_element_by_css_selector(at_sh_id).text)
            except:
                time.sleep(.1)
        if split_score and ht_fh_score != -1 and at_fh_score != -1 and ht_sh_score != -1 and at_sh_score != -1 and home_match is not None:
            break
        elif (not split_score) and ht_sh_score != -1 and at_sh_score != -1 and home_match is not None:
            break
        time.sleep(.1)
        hover = ActionChains(driver).move_to_element(driver.find_element_by_css_selector('body'))
        hover.perform()
        time.sleep(.2)
        hover = ActionChains(driver).move_to_element(hover_element)
        hover.perform()
        time.sleep(.5)
    if ht_fh_score != -1 and ht_sh_score != -1:
        ht_sh_score = ht_sh_score - ht_fh_score
    if at_fh_score != -1 and at_sh_score != -1:
        at_sh_score = at_sh_score - at_fh_score
    try:
        driver.find_element(By.CSS_SELECTOR, "body").click()
    except Exception as e:
        pass
    return ht_fh_score, at_fh_score, ht_sh_score, at_sh_score, home_match


def get_h2h_results(driver, selector):
    if driver is None or selector is None:
        return [], [], []
    ht_wins = []
    draws = []
    at_wins = []

    """
    Se pare ca odata afisat elementul hover acesta persista in DOM.
    Astfel, la verificarea urmatoarei statistici, daca nu exista elementul hover, va fi gasit primul si 
    implicit se vor returna aceleasi valori.
    De parca nu era destul, se pare ca hover-ul are aceeasi clasa ca si card-ul Istoric DAR DOAR IN ANUMITE CAZURI.
    IN PLUS si parintele ambelor elemente are aceeasi clasa. 
    Solutia pe care am gasit-o a fost sa caut BUNICUL card-ului Isoric si sa iau acel element care nu are aceeasi 
    clasa.
    
    """
    # Home team wins
    for z in range(10):
        try:
            if z == 0:
                h2h_element = driver.find_element_by_css_selector(selector)
                htw_element = h2h_element.find_element(By.CSS_SELECTOR, "td[class='center first ']")
                driver.execute_script('arguments[0].scrollIntoView();', htw_element)
                try:
                    _ = htw_element.find_element_by_class_name('hoverstate')
                except NoSuchElementException:
                    # Nu are hover deci are valoarea 0
                    break
                hover = ActionChains(driver).move_to_element(htw_element)
                hover.perform()
                time.sleep(.5)
            elif z >= 5:
                succes = False
                if wait_for_elem_by_css(driver, "table[class='normaltable history ']"):
                    tab_istoric_list = driver.find_elements(By.CSS_SELECTOR, "table[class='normaltable history ']")
                    for tab_istoric in tab_istoric_list:
                        if tab_istoric.is_displayed():
                            parentof_parent = tab_istoric.find_element_by_xpath('..').find_element_by_xpath('..')
                            if "view team_history_details_view_wrap" not in parentof_parent.get_attribute('class'):
                                ht_wins_cnt = len(tab_istoric.find_elements(By.CSS_SELECTOR, "span[class='teams']"))
                                if ht_wins_cnt > 0:
                                    date_list = tab_istoric.find_elements(By.CSS_SELECTOR, "td[class='datetime']")
                                    for data in date_list:
                                        ht_wins.append(data.text)
                                succes = True
                                break
                else:
                    h2h_element = driver.find_element_by_css_selector(selector)
                    htw_element = h2h_element.find_element(By.CSS_SELECTOR, "td[class='center first ']")
                    driver.execute_script('arguments[0].scrollIntoView();', htw_element)
                    hover = ActionChains(driver).move_to_element(htw_element)
                    hover.perform()
                    time.sleep(.5)
                if succes:
                    break
            else:
                time.sleep(.1)
        except Exception as e:
            # print(e.args)
            # traceback.print_tb(e.__traceback__)
            time.sleep(.1)
        time.sleep(.1)

    # Draws
    for z in range(10):
        try:
            if z == 0:
                h2h_element = driver.find_element_by_css_selector(selector)
                draws_element = h2h_element.find_element(By.CSS_SELECTOR, "td[class='center ']")
                driver.execute_script('arguments[0].scrollIntoView();', draws_element)
                try:
                    _ = draws_element.find_element_by_class_name('hoverstate')
                except NoSuchElementException:
                    # Nu are hover deci are valoarea 0
                    break
                hover = ActionChains(driver).move_to_element(draws_element)
                hover.perform()
                time.sleep(.5)
            elif z >= 5:
                succes = False
                if wait_for_elem_by_css(driver, "table[class='normaltable history ']"):
                    tab_istoric_list = driver.find_elements(By.CSS_SELECTOR, "table[class='normaltable history ']")
                    for tab_istoric in tab_istoric_list:
                        if tab_istoric.is_displayed():
                            parentof_parent = tab_istoric.find_element_by_xpath('..').find_element_by_xpath('..')
                            if "view team_history_details_view_wrap" not in parentof_parent.get_attribute('class'):
                                draws_cnt = len(tab_istoric.find_elements(By.CSS_SELECTOR, "span[class='teams']"))
                                if draws_cnt > 0:
                                    date_list = tab_istoric.find_elements(By.CSS_SELECTOR, "td[class='datetime']")
                                    for data in date_list:
                                        draws.append(data.text)
                                succes = True
                                break
                else:
                    h2h_element = driver.find_element_by_css_selector(selector)
                    draws_element = h2h_element.find_element(By.CSS_SELECTOR, "td[class='center ']")
                    driver.execute_script('arguments[0].scrollIntoView();', draws_element)
                    hover = ActionChains(driver).move_to_element(draws_element)
                    hover.perform()
                    time.sleep(.5)
                if succes:
                    break
            else:
                time.sleep(.1)
        except Exception as e:
            # print(e.args)
            # traceback.print_tb(e.__traceback__)
            time.sleep(.1)
        time.sleep(.1)

    # Away team wins
    for z in range(10):
        try:
            if z == 0:
                h2h_element = driver.find_element_by_css_selector(selector)
                atw_element = h2h_element.find_element(By.CSS_SELECTOR, "td[class='center last ']")
                driver.execute_script('arguments[0].scrollIntoView();', atw_element)
                try:
                    _ = atw_element.find_element_by_class_name('hoverstate')
                except NoSuchElementException:
                    # Nu are hover deci are valoarea 0
                    break
                hover = ActionChains(driver).move_to_element(atw_element)
                hover.perform()
                time.sleep(.5)
            elif z >= 5:
                succes = False
                if wait_for_elem_by_css(driver, "table[class='normaltable history ']"):
                    tab_istoric_list = driver.find_elements(By.CSS_SELECTOR, "table[class='normaltable history ']")
                    for tab_istoric in tab_istoric_list:
                        if tab_istoric.is_displayed():
                            parentof_parent = tab_istoric.find_element_by_xpath('..').find_element_by_xpath('..')
                            if "view team_history_details_view_wrap" not in parentof_parent.get_attribute('class'):
                                at_wins_cnt = len(tab_istoric.find_elements(By.CSS_SELECTOR, "span[class='teams']"))
                                if at_wins_cnt > 0:
                                    date_list = tab_istoric.find_elements(By.CSS_SELECTOR, "td[class='datetime']")
                                    for data in date_list:
                                        at_wins.append(data.text)
                                succes = True
                                break
                else:
                    h2h_element = driver.find_element_by_css_selector(selector)
                    atw_element = h2h_element.find_element(By.CSS_SELECTOR, "td[class='center last ']")
                    driver.execute_script('arguments[0].scrollIntoView();', atw_element)
                    hover = ActionChains(driver).move_to_element(atw_element)
                    hover.perform()
                    time.sleep(.5)
                if succes:
                    break
            else:
                time.sleep(.1)
        except Exception as e:
            # print(e.args)
            # traceback.print_tb(e.__traceback__)
            time.sleep(.1)
        time.sleep(.1)
    return ht_wins, draws, at_wins


def get_teams_ranks_and_stats(driver, selector):
    result = {"1": {"Pos": 0,
                    "J": 0,
                    "V": 0,
                    "E": 0,
                    "I": 0,
                    "GF": 0,
                    "GA": 0,
                    "Pts": 0},
              "2": {"Pos": 0,
                    "J": 0,
                    "V": 0,
                    "E": 0,
                    "I": 0,
                    "GF": 0,
                    "GA": 0,
                    "Pts": 0}
              }
    if driver is None or selector is None:
        return result

    team1 = driver.find_element_by_css_selector('td.legend:nth-child(1) > p:nth-child(1)').text
    try:
        wait_for_elem_by_css(driver, selector)
        div_clasament = driver.find_element_by_css_selector(selector)
    except Exception as e:
        print('Nu am gasit cardul cu istoricul echipelor! - Meci de cupa sau international?')
        return result
    try:
        body = div_clasament.find_element(By.CSS_SELECTOR, 'tbody')
        body.click()  # Incerc sa fac tooltip-ul (hover element) afisat anterior sa dispara
        linii = body.find_elements(By.CSS_SELECTOR, 'tr')
        for l in linii:
            curr_team = l.find_element(By.CSS_SELECTOR, "td[class='team ']").text
            if curr_team.lower() in team1.lower():
                tn = "1"
            else:
                tn = "2"
            result[tn]["Pos"] = int(l.find_element(By.CSS_SELECTOR, "td[class='pos first ']").text)
            result[tn]["J"] = int(l.find_element(By.CSS_SELECTOR, "td[class='played ']").text)
            result[tn]["V"] = int(l.find_element(By.CSS_SELECTOR, "td[class='win ']").text)
            result[tn]["E"] = int(l.find_element(By.CSS_SELECTOR, "td[class='draw ']").text)
            result[tn]["I"] = int(l.find_element(By.CSS_SELECTOR, "td[class='lose ']").text)
            result[tn]["Pts"] = int(l.find_element(By.CSS_SELECTOR, "td[class='points last ']").text)
            goluri = l.find_element(By.CSS_SELECTOR, "td[class='goals ']").text
            result[tn]["GF"] = int(goluri.split(':')[0])
            result[tn]["GA"] = int(goluri.split(':')[1])
    except Exception as e:
        # print(e.args)
        # traceback.print_tb(e.__traceback__)
        print('Nu am gasit cardul cu istoricul echipelor! - Meci de cupa sau international?')
    return result


def get_over_under_stats(driver):
    result = {
        "1":
            {"T":
                 {"0.5": -1, "1.5": -1, "2.5": -1, "3.5": -1},
             "R1":
                 {"0.5": -1, "1.5": -1, "2.5": -1, "3.5": -1},
             "R2":
                 {"0.5": -1, "1.5": -1, "2.5": -1, "3.5": -1}
             },
        "2":
            {"T":
                 {"0.5": -1, "1.5": -1, "2.5": -1, "3.5": -1},
             "R1":
                 {"0.5": -1, "1.5": -1, "2.5": -1, "3.5": -1},
             "R2":
                 {"0.5": -1, "1.5": -1, "2.5": -1, "3.5": -1}
             }
    }

    if driver is None:
        return result

    under_over_card_id = "div[class='view newoverunder headtohead_twoteams_newoverunder']"
    dropdown_id = "div[class='sb-wrapper']"

    total_text = "Peste/Sub Final"
    r1_text = "Peste/Sub Repriza 1"
    r2_text = "Peste/Sub Repriza 2"

    over_under_id = "div[class='tabs navtabs']"

    wait_for_elem_by_css(driver, under_over_card_id)
    try:
        card = driver.find_element_by_css_selector(under_over_card_id)
    except Exception as e:
        # print(e.args)
        # traceback.print_tb(e.__traceback__)
        print('Nu am gasit card-ul pentru Over/Under! - Meci de Cupa sau meci international?')
        return result

    dropdown = card.find_element(By.CSS_SELECTOR, dropdown_id)
    dropdown.click()
    click = False
    time.sleep(.5)
    opt_list_elem = dropdown.find_element(By.CSS_SELECTOR, "ul[class='slickselect']")
    option_list = opt_list_elem.find_elements(By.CSS_SELECTOR, "li")

    for option in option_list:
        if click:
            card = driver.find_element_by_css_selector(under_over_card_id)
            dropdown = card.find_element(By.CSS_SELECTOR, dropdown_id)
            dropdown.click()
            time.sleep(.5)

        current_option_text = option.text
        option.click()
        click = True
        key = "N/A"
        if total_text.lower() in current_option_text.lower():
            key = "T"
        elif r1_text.lower() in current_option_text.lower():
            key = "R1"
        elif r2_text.lower() in current_option_text.lower():
            key = "R2"

        over_under_element = card.find_element(By.CSS_SELECTOR, over_under_id)
        over_under_options = over_under_element.find_elements(By.CSS_SELECTOR, "div[class='htab']")
        no_options = len(over_under_options)
        for over_under_option_no in range(no_options):
            try:
                card = driver.find_element_by_css_selector(under_over_card_id)
                over_under_element = card.find_element(By.CSS_SELECTOR, over_under_id)
                over_under_options = over_under_element.find_elements(By.CSS_SELECTOR, "div[class='htab']")
                over_under_option = over_under_options[over_under_option_no]
                sub_key = over_under_option.text
                over_under_option.click()
                time.sleep(2)  # TODO De vazut daca poate fi indepartat sleep-ul asta si inlocuit cu ceva safe
                # Iau doar stats pentru PESTE, cele de UNDER pot fi deduse (100 - PESTE = UNDER)
                team1_stats_element = card.find_element(By.CSS_SELECTOR, "div[class='team1']")
                team2_stats_element = card.find_element(By.CSS_SELECTOR, "div[class='team2']")
                t1over_el = team1_stats_element.find_element(By.CSS_SELECTOR, "div[class='over']")
                t1_percent_element = t1over_el.find_element(By.CSS_SELECTOR, "span[class='numbers']")
                t1over_percent = float(t1_percent_element.text.split('(')[1].split('%')[0])
                t2over_el = team2_stats_element.find_element(By.CSS_SELECTOR, "div[class='over']")
                t2_percent_element = t2over_el.find_element(By.CSS_SELECTOR, "span[class='numbers']")
                t2over_percent = float(t2_percent_element.text.split('(')[1].split('%')[0])
                result["1"][key][sub_key] = t1over_percent
                result["2"][key][sub_key] = t2over_percent
            except Exception as e:
                # Exista statistici doar pe total goluri per meci, nu neaparat pe fiecare repriza
                # print(e.args)
                # traceback.print_tb(e.__traceback__)
                time.sleep(.1)
    return result


def get_next_match_fname(id_meci: str):
    if not os.path.isfile('data\\{}.json'.format(id_meci)):
        return '{}.json'.format(id_meci)
    cnt = 1
    while os.path.isfile('data\\{}_{}.json'.format(id_meci, cnt)):
        cnt += 1
    return '{}_{}.json'.format(id_meci, cnt)


def kill_chrome():
    try:
        output = subprocess.check_output('taskkill /t /f /im chrome.exe', shell=True)
        print(output)
    except Exception as e:
        print(e.args)
        traceback.print_tb(e.__traceback__)
        pass


if __name__ == '__main__':
    kill_chrome()
    if not os.path.isdir('results'):
        os.makedirs('data', exist_ok=True)
    driver = webdriver.Chrome(chromedriver, chrome_options=options)
    driver.implicitly_wait(10)

    pagina = '.custom-filter > li:nth-child({}) > a:nth-child(1)'

    count = 0
    ex = Exception()
    while count < 3:
        try:
            driver.get('https://www.superbet.ro/pariuri-sportive')
            break
        except Exception as e:
            ex = e
            print('Exceptie la incercarea de a lua rezultatele ({})'.format(e.args))
            count += 1
    if count == 3:
        raise ex

    Constants.meciuri_db = DBInterface(db_file_name=Constants.DatabasesInfo.meciuri_db['db_file_name'],
                                       table_name=Constants.DatabasesInfo.meciuri_db['table_name'],
                                       columns=Constants.DatabasesInfo.meciuri_db['columns'],
                                       primary_key=Constants.DatabasesInfo.meciuri_db['primary_key'],
                                       create_only_if_not_exists=Constants.DatabasesInfo.meciuri_db[
                                           'create_only_if_not_exists'])

    Constants.results_db = DBInterface(db_file_name=Constants.DatabasesInfo.results_db['db_file_name'],
                                       table_name=Constants.DatabasesInfo.results_db['table_name'],
                                       columns=Constants.DatabasesInfo.results_db['columns'],
                                       primary_key=Constants.DatabasesInfo.results_db['primary_key'],
                                       create_only_if_not_exists=Constants.DatabasesInfo.results_db[
                                           'create_only_if_not_exists'])

    q = Queue(maxsize=-1)  # Marime infinita pentru coada
    stats_prov = StatsProvider(q)
    stats_prov.start()
    algorithms = [Algorithm5, Algorithm6]
    for algor in algorithms:
        alg = algor()
        alg.start()
        stats_prov.algorithms.append(alg)

    for pag in range(1, 10):
        driver.execute_script("window.scrollTo(0, 0);")
        wait_for_elem_by_css(driver, pagina.format(pag))
        pag_elem = driver.find_element_by_css_selector(pagina.format(pag))
        if 'toate' not in str(pag_elem.text).lower():
            data_str = pag_elem.text
            data_meciuri = datetime.datetime.strptime(data_str.split()[0] + '.{}'.format(datetime.datetime.now().year),
                                                      '%d.%m.%Y').date()
            pag_elem.click()
            but_sporturi = '#sportsinfilter-TGlobal_Sportfilter_Sportsinfilter_XActor > span:nth-child(1) > div:nth-child(2) > button:nth-child(1)'
            but_sport = '.open > ul:nth-child(2) > li:nth-child({}) > a:nth-child(1) > label:nth-child(1)'

            wait_for_elem_by_css(driver, but_sporturi)
            driver.find_element_by_css_selector(but_sporturi).click()
            wait_for_elem_by_css(driver, '.open > ul:nth-child(2)')
            sports_elem = driver.find_element_by_css_selector('.open > ul:nth-child(2)')
            sports = sports_elem.find_elements(By.CSS_SELECTOR, 'li')
            nr_sporturi = len(sports)
            football_exists = False
            wait_for_elem_by_css(driver, but_sport.format(1))
            for i in range(0, nr_sporturi):
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
                    time.sleep(.1)

                all_competitions = driver.find_elements(By.CSS_SELECTOR, "div[class='tour']")
                nr_competitions = len(all_competitions)
                step = 5
                index = 0
                main_window_handle = driver.current_window_handle
                while index < nr_competitions:
                    for c in range(index, index + step):
                        if c >= nr_competitions:
                            break
                        all_competitions = driver.find_elements(By.CSS_SELECTOR, "div[class='tour']")
                        competition = all_competitions[c]
                        competition_name = competition.find_element(By.CSS_SELECTOR,
                                                                    "h1[class='match-title-header'").text
                        if str(competition_name).lower().strip().endswith('(f)'):
                            print("Competitie care nu prezinta interes (fotbal feminin) : " +
                                  str(competition_name))
                        else:
                            tabele_cote = competition.find_elements(By.CSS_SELECTOR, "table[class='offer']")
                            nr_tabele = len(tabele_cote)
                            skip_competition = False
                            for t in range(nr_tabele):
                                if skip_competition:
                                    break
                                tab = tabele_cote[t]
                                all_matches = tab.find_elements(By.CSS_SELECTOR, "tr[data-match]")
                                for m in all_matches:
                                    id_meci = m.find_element(By.CSS_SELECTOR, "span[class='single']").text
                                    if Constants.meciuri_db.record_exists(record_value=id_meci):
                                        print("Am cules deja statistica pentru meciul cu id-ul {}".format(id_meci))
                                        stats_prov.queue.put(id_meci)
                                        continue
                                    echipe = m.find_element_by_css_selector(css_selector="span[class='match-name']")
                                    txt = echipe.text
                                    if ':' in txt:
                                        print("Meci in desfasurare {}! Sar peste el!".format(txt))
                                        continue
                                    echipa1, echipa2 = txt.split(' - ', 1)
                                    echipa1 = echipa1.replace("'", "`")
                                    echipa2 = echipa2.replace("'", "`")
                                    if ':' in txt or '(F)' in txt:
                                        print('Match in progress or female team... ' + txt)
                                    else:
                                        print("Competitie: " + str(competition_name).strip())
                                        meci_json = {}
                                        print("{}: {}".format(id_meci, txt))
                                        try:
                                            stats_elem = m.find_element_by_css_selector(
                                                css_selector="td[class='stats']")
                                            # Folosesc javascript pentru a da click pe element pentru ca e posibil
                                            # sa nu fie afisat in fereastra ci sa fie mai sus in pagina
                                            driver.execute_script("arguments[0].click()", stats_elem)
                                            driver.switch_to.window(driver.window_handles[1])
                                            driver.maximize_window()
                                            meci_json['Stats'] = {}
                                            meci_json["Stats"]["Home_History"] = []
                                            meci_json["Stats"]["Away_History"] = []
                                            h_team = driver.find_element_by_css_selector(
                                                'div.left:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').text
                                            a_team = driver.find_element_by_css_selector(
                                                '.h2h_teamselect2 > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').text
                                            print(h_team)
                                            print(a_team)
                                            tab_tendency = driver.find_element_by_css_selector(
                                                "div[class='tendencyteam1']")
                                            prev_stats = tab_tendency.find_elements(By.CSS_SELECTOR, 'li[class]')
                                            for tend in prev_stats:
                                                curr_tend = []
                                                tend_txt = unicodedata.normalize('NFKD', tend.text).encode('ASCII',
                                                                                                           'ignore').decode(
                                                    'utf-8')
                                                print(tend_txt)
                                                if len(tend_txt.strip()) < 1:
                                                    print("Skiping current tendency element - 0 length text!")
                                                    continue
                                                curr_tend.append(tend_txt)
                                                success = False
                                                while not success:
                                                    hover = ActionChains(driver).move_to_element(tend)
                                                    hover.perform()
                                                    tick = 0
                                                    while (
                                                            not wait_for_elem_by_css(driver,
                                                                                     "td[class='home ft first ']",
                                                                                     5)) and tick < 5:
                                                        hover = ActionChains(driver).move_to_element(tend)
                                                        hover.perform()
                                                        tick += 1
                                                        time.sleep(.5)
                                                    if tick == 5:
                                                        print("!" * 100)
                                                        print(
                                                            "Nu am reusit sa fac hover peste acest element! Incercarea nr. {}".format(
                                                                tick))
                                                        print("!" * 100)
                                                        break
                                                    else:
                                                        ht_fh, at_fh, ht_sh, at_sh, loc = get_scores(driver, tend, h_team)
                                                        if ht_sh != -1 and at_sh != -1 and (
                                                                    (ht_fh != -1 and at_fh != -1) or (
                                                                                ht_fh == -1 and at_fh == -1)):
                                                            success = True
                                                            print("{}:{}".format(ht_fh, at_fh))
                                                            print("{}:{}".format(ht_sh, at_sh))
                                                            curr_tend.append(ht_fh)
                                                            curr_tend.append(at_fh)
                                                            curr_tend.append(ht_sh)
                                                            curr_tend.append(at_sh)
                                                            curr_tend.append(loc)
                                                            if loc:
                                                                print('Home match')
                                                            else:
                                                                print('Away match')
                                                            meci_json['Stats']['Home_History'].append(
                                                                copy.deepcopy(curr_tend))
                                            print('#' * 100)
                                            tab_tendency = driver.find_element_by_css_selector(
                                                "div[class='tendencyteam2']")
                                            prev_stats = tab_tendency.find_elements(By.CSS_SELECTOR, 'li[class]')
                                            for tend in prev_stats:
                                                curr_tend = []
                                                tend_txt = unicodedata.normalize('NFKD', tend.text).encode('ASCII',
                                                                                                           'ignore').decode(
                                                    'utf-8')
                                                print(tend_txt)
                                                if len(tend_txt.strip()) < 1:
                                                    print("Skiping current tendency element - 0 length text!")
                                                    continue
                                                curr_tend.append(tend_txt)
                                                success = False
                                                while not success:
                                                    hover = ActionChains(driver).move_to_element(tend)
                                                    hover.perform()
                                                    tick = 0
                                                    while (
                                                            not wait_for_elem_by_css(driver,
                                                                                     "td[class='home ft first ']",
                                                                                     5)) and tick < 5:
                                                        hover = ActionChains(driver).move_to_element(tend)
                                                        hover.perform()
                                                        tick += 1
                                                        time.sleep(.5)
                                                    if tick == 5:
                                                        print("!" * 100)
                                                        print(
                                                            "Nu am reusit sa fac hover peste acest element! Incercarea nr. {}".format(
                                                                tick))
                                                        print("!" * 100)
                                                        break
                                                    else:
                                                        ht_fh, at_fh, ht_sh, at_sh, loc = get_scores(driver, tend, a_team)
                                                        if ht_sh != -1 and at_sh != -1 and (
                                                                    (ht_fh != -1 and at_fh != -1) or (
                                                                                ht_fh == -1 and at_fh == -1)):
                                                            success = True
                                                            print("{}:{}".format(ht_fh, at_fh))
                                                            print("{}:{}".format(ht_sh, at_sh))
                                                            curr_tend.append(ht_fh)
                                                            curr_tend.append(at_fh)
                                                            curr_tend.append(ht_sh)
                                                            curr_tend.append(at_sh)
                                                            curr_tend.append(loc)
                                                            if loc:
                                                                print('Home match')
                                                            else:
                                                                print('Away match')
                                                            meci_json['Stats']['Away_History'].append(
                                                                copy.deepcopy(curr_tend))
                                            meci_json['Stats']['H2H_History'] = {}
                                            wait_for_elem_by_css(driver,
                                                                 "div[class='couch_headtohead_historygraph']")
                                            ht_wins, draws, at_wins = get_h2h_results(driver,
                                                                                      "div[class='couch_headtohead_historygraph']")
                                            print("H2H: \n{}\n{}\n{}\n\n".format(ht_wins, draws, at_wins))
                                            meci_json['Stats']['H2H_History']['Home_Wins'] = copy.deepcopy(ht_wins)
                                            meci_json['Stats']['H2H_History']['Draws'] = copy.deepcopy(draws)
                                            meci_json['Stats']['H2H_History']['Away_Wins'] = copy.deepcopy(at_wins)
                                            ranks = get_teams_ranks_and_stats(driver,
                                                                              "div.headtohead_twoteams_leaguetable")
                                            print("{} stats: {}".format(echipa1, ranks["1"]))
                                            print("{} stats: {}".format(echipa2, ranks["2"]))
                                            meci_json['Stats']['Home_Stats'] = copy.deepcopy(ranks["1"])
                                            meci_json['Stats']['Away_Stats'] = copy.deepcopy(ranks["2"])
                                            print()
                                            over_under_stats = get_over_under_stats(driver)
                                            print(over_under_stats)
                                            meci_json['Stats']['Home_Over_Under'] = copy.deepcopy(over_under_stats["1"])
                                            meci_json['Stats']['Away_Over_Under'] = copy.deepcopy(over_under_stats["2"])
                                            json_fname = get_next_match_fname(id_meci)
                                            with open('data\\' + json_fname, 'wt') as f:
                                                json.dump(meci_json, f)
                                            Constants.meciuri_db.insert_record(values={'id_meci': id_meci,
                                                                                       'competitie': competition_name,
                                                                                       'home_team': echipa1,
                                                                                       'away_team': echipa2,
                                                                                       'match_date': data_meciuri,
                                                                                       'json_fname': json_fname},
                                                                               update_if_exists=True)
                                            stats_prov.queue.put(id_meci)
                                        except Exception as e:
                                            # print(e.args)
                                            # traceback.print_tb(e.__traceback__)
                                            print(
                                                "Nu am gasit elementul STATS pentru meciul {} - {}".format(echipa1,
                                                                                                           echipa2))
                                            # meciuri[str(pag)][str(competition_name).strip()].pop(id_meci, None)
                                        finally:
                                            driver.switch_to.window(main_window_handle)
                                break
                    index += step
                    all_competitions = driver.find_elements(By.CSS_SELECTOR, "div[class='tour']")
                    nr_competitions = len(all_competitions)

        else:
            print("Am terminat de cules meciurile si statisticile de astazi!")
            # TODO Aici trebuie sa incep sa culeg eventualele rezultate ale meciurilor culese anterior
            break

    driver.quit()

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
   http://stats.betradar.com/s4/?clientid=242&fragment=h2h#2_1,3_152,22_1,5_43592,9_headtohead,7_25730,178_279423
"""
