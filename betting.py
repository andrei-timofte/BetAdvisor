import os
import sys
import get_available_matches
import add_missing_links_and_aliasses
import analyzer
import time
import subprocess
import datetime
import json


try:
    output = subprocess.check_output('taskkill /t /f /im chrome.exe', shell=True)
    print(output)
except:
    pass
meciuri_json = None
# meciuri_json = r'd:\Indie\Betting\26072017\meciuri.json'
while meciuri_json is None:
    try:
        meciuri_json = get_available_matches.get_matches()
    except:
        try:
            output = subprocess.check_output('taskkill /t /f /im chrome.exe', shell=True)
            print(output)
        except:
            pass
        time.sleep(3)
        pass
success = -1
# success = add_missing_links_and_aliasses.get_results(meciuri_json)
while -1 == success:
    try:
        success = add_missing_links_and_aliasses.get_results(meciuri_json)
    except:
        try:
            output = subprocess.check_output('taskkill /t /f /im chrome.exe', shell=True)
            print(output)
        except:
            pass
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
    except:
        pass

