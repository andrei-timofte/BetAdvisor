import os
import json
import re
import threading
from queue import Queue
from db_helper import DBInterface
from constants import *


class Algorithm(threading.Thread):
    def __init__(self, reanalyze):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.daemon = True
        self.name = "Algorithm Base class"
        self.description = """Algorithm Base class"""
        self.pattern = re.compile('[\W_]+', re.UNICODE)
        self.treshold = 75
        self.queue = Queue(maxsize=-1)
        self.db = None
        self.db_name = 'algorithm.db'
        self.reanalyze = reanalyze

    def init_db(self):
        self.db = DBInterface(db_file_name=self.db_name,
                              table_name='results',
                              columns=Constants.DatabasesInfo.algorithm_db_columns,
                              primary_key='id_meci',
                              create_only_if_not_exists=True)

    def analyze(self, match_info):
        print(self.name, "Analyzing: {}".format(match_info))

    @staticmethod
    def odds_from_percentage(percentage):
        if percentage > 0:
            return float(int((1 / percentage) * 10000) / 10000)
        return 1.00
