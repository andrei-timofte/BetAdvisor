import os
import threading
import json

from constants import *


class StatsProvider(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue
        self.daemon = True
        # self.receive_messages = args[0]
        self.data_cache = []
        self.algorithms = []

    def run(self):
        print(threading.currentThread().getName())
        while True:
            val = self.queue.get()
            if val is None:
                # Se opreste thread-ul daca se pune un None in coada. Asta ca sa nu am un event separat
                return
            self.do_thing_with_message(val)

    def do_thing_with_message(self, message):
        new_match = Constants.meciuri_db.get_records(Constants.meciuri_db.primary_key, message)
        # new_match ar trebui sa aiba len >=0 <=1
        if len(new_match) > 0:
            print(new_match[0])
            json_file = 'data\\{}'.format(new_match[0][5])
            if os.path.isfile(json_file):
                with open(json_file, 'rt') as f:
                    new_info = json.load(f)
                to_analyze = dict()
                to_analyze[message] = [new_info, new_match[0]]
                with Constants.lock:
                    print(to_analyze)
                    self.data_cache.append(to_analyze)
                    # print(threading.currentThread().getName(), "Received {}".format(message))
                    # while len(self.data_cache) > 100:
                    #     self.data_cache.pop(0)
                for algorithm in self.algorithms:
                    algorithm.queue.put(to_analyze)
