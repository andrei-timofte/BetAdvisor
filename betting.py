import os
# import sys
import get_available_matches
import add_missing_links_and_aliasses
import analyzer
import time
import subprocess
import traceback
import json
import datetime


def kill_chrome():
    try:
        output = subprocess.check_output('taskkill /t /f /im chrome.exe', shell=True)
        print(output)
    except Exception as e:
        print(e.args)
        traceback.print_tb(e.__traceback__)
        pass


script_path = os.path.dirname(os.path.realpath(__file__))
data = datetime.datetime.now()
_results_folder = os.path.join(script_path, str(data.day).zfill(2) + str(data.month).zfill(2) + str(data.year))

if os.path.isfile(os.path.join(_results_folder, 'predictions.json')):
    with open(os.path.join(_results_folder, 'predictions.json'), 'rt') as f:
        predictions = json.load(f)
    for k in sorted(predictions.keys()):
        print('=' * 160)
        print('{}'.format(k))
        print('=' * 160)
        for v in sorted(predictions[k].keys()):
            print('-' * 160)
            print(v)
            print('-' * 160)
            for match in predictions[k][v]:
                print('{} - {}  ->  {}'.format(match[0], match[1], match[2]))
            print()
    print('=' * 160)
    print()
else:
    kill_chrome()
    meciuri_json = None
    # meciuri_json = r'd:\#BetAdvisor\21082017\meciuri.json'
    # meciuri_json = get_available_matches.get_matches()
    while meciuri_json is None:
        try:
            meciuri_json = get_available_matches.get_matches()
        except Exception as e:
            print(e.args)
            traceback.print_tb(e.__traceback__)
            kill_chrome()
            time.sleep(3)
            pass
    success = -1
    while -1 == success:
        try:
            success = add_missing_links_and_aliasses.get_results(meciuri_json)
        except Exception as e:
            print(e.args)
            traceback.print_tb(e.__traceback__)
            kill_chrome()
            time.sleep(3)

    results_folder = os.path.dirname(os.path.realpath(meciuri_json))

    success = -1
    while -1 == success:
        try:
            success = analyzer.analyze_matches(meciuri_json)
            if os.path.isfile(os.path.join(results_folder, 'predictions.json')):
                with open(os.path.join(results_folder, 'predictions.json'), 'rt') as f:
                    predictions = json.load(f)
                for k in sorted(predictions.keys()):
                    print('=' * 160)
                    print('{}'.format(k))
                    print('=' * 160)
                    for v in sorted(predictions[k].keys()):
                        print('-' * 160)
                        print(v)
                        print('-' * 160)
                        for match in predictions[k][v]:
                            print('{} - {}  ->  {}'.format(match[0], match[1], match[2]))
                        print()
                print('=' * 160)
                print()
        except Exception as e:
            print(e.args)
            traceback.print_tb(e.__traceback__)
            pass

