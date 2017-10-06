import threading


class Constants:
    lock = threading.Lock()
    meciuri_db = None
    results_db = None

    class StatementTypes:
        CREATE_STATEMENT = 0
        INSERT_STATEMENT = 1
        UPDATE_STATEMENT = 2
        DELETE_STATEMENT = 2

    class DatabasesInfo:
        meciuri_db = {'db_file_name': 'meciuri.db',
                      'table_name': 'meciuri',
                      'columns': {'id_meci': 'INT NOT NULL PRIMARY KEY',
                                  'competitie': 'VARCHAR(30) NOT NULL',
                                  'home_team': 'VARCHAR(30) NOT NULL',
                                  'away_team': 'VARCHAR(30) NOT NULL',
                                  'match_date': 'DATE NOT NULL',
                                  'json_fname': 'VARCHAR(30)'},
                      'primary_key': 'id_meci',
                      'create_only_if_not_exists': True}
        results_db = {'db_file_name': 'results.db',
                      'table_name': 'results',
                      'columns': {'id_meci': 'INT NOT NULL PRIMARY KEY',
                                  'home_team': 'VARCHAR(30) NOT NULL',
                                  'away_team': 'VARCHAR(30) NOT NULL',
                                  'ht_fh_score': 'INT NOT NULL',
                                  'at_fh_score': 'INT NOT NULL',
                                  'ht_sh_score': 'INT NOT NULL',
                                  'at_sh_score': 'INT NOT NULL',
                                  'match_date': 'DATE NOT NULL'},
                      'primary_key': 'id_meci',
                      'create_only_if_not_exists': True}

        algorithm_db_columns = {'id_meci': 'INT NOT NULL PRIMARY KEY',
                                'competitie': 'VARCHAR(30) NOT NULL',
                                'home_team': 'VARCHAR(30) NOT NULL',
                                'away_team': 'VARCHAR(30) NOT NULL',
                                'match_date': 'DATE NOT NULL',
                                'prediction': 'INT NOT NULL'}

    class Predictions:
        FULL_TIME_HOME_TEAM_WINS = 0b1
        FULL_TIME_AWAY_TEAM_WINS = 0b10
        FULL_TIME_DRAW_RESULT = 0b100
        FIRST_HALF_HOME_TEAM_WINS = 0b1000
        FIRST_HALF_AWAY_TEAM_WINS = 0b10000
        FIRST_HALF_DRAW_RESULT = 0b100000
        SECOND_HALF_HOME_TEAM_WINS = 0b1000000
        SECOND_HALF_AWAY_TEAM_WINS = 0b10000000
        SECOND_HALF_DRAW_RESULT = 0b100000000
        FULL_TIME_HOME_TEAM_SCORES = 0b1000000000
        FULL_TIME_AWAY_TEAM_SCORES = 0b10000000000
        FIRST_HALF_HOME_TEAM_SCORES = 0b100000000000
        FIRST_HALF_AWAY_TEAM_SCORES = 0b1000000000000
        SECOND_HALF_HOME_TEAM_SCORES = 0b10000000000000
        SECOND_HALF_AWAY_TEAM_SCORES = 0b100000000000000
        FULL_TIME_HOME_TEAM_NO_SCORE = 0b1000000000000000
        FULL_TIME_AWAY_TEAM_NO_SCORE = 0b10000000000000000
        FIRST_HALF_HOME_TEAM_NO_SCORE = 0b100000000000000000
        FIRST_HALF_AWAY_TEAM_NO_SCORE = 0b1000000000000000000
        SECOND_HALF_HOME_TEAM_NO_SCORE = 0b10000000000000000000
        SECOND_HALF_AWAY_TEAM_NO_SCORE = 0b100000000000000000000
        FULL_TIME_OVER_05 = 0b1000000000000000000000
        FULL_TIME_OVER_15 = 0b10000000000000000000000
        FULL_TIME_OVER_25 = 0b100000000000000000000000
        FULL_TIME_OVER_35 = 0b1000000000000000000000000
        FIRST_HALF_OVER_05 = 0b10000000000000000000000000
        FIRST_HALF_OVER_15 = 0b100000000000000000000000000
        FIRST_HALF_OVER_25 = 0b1000000000000000000000000000
        FIRST_HALF_OVER_35 = 0b10000000000000000000000000000
        SECOND_HALF_OVER_05 = 0b100000000000000000000000000000
        SECOND_HALF_OVER_15 = 0b1000000000000000000000000000000
        SECOND_HALF_OVER_25 = 0b10000000000000000000000000000000
        SECOND_HALF_OVER_35 = 0b100000000000000000000000000000000
