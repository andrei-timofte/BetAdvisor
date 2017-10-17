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
                      'columns': {'id_meci': 'INT NOT NULL',
                                  'competitie': 'VARCHAR(30) NOT NULL',
                                  'home_team': 'VARCHAR(30) NOT NULL',
                                  'away_team': 'VARCHAR(30) NOT NULL',
                                  'match_date': 'DATE NOT NULL',
                                  'json_fname': 'VARCHAR(30),  PRIMARY KEY(id_meci, match_date)'},
                      'primary_key': 'id_meci',
                      'create_only_if_not_exists': True}
        results_db = {'db_file_name': 'results.db',
                      'table_name': 'results',
                      'columns': {'id_meci': 'INT NOT NULL',
                                  'home_team': 'VARCHAR(30) NOT NULL',
                                  'away_team': 'VARCHAR(30) NOT NULL',
                                  'ht_fh_score': 'INT NOT NULL',
                                  'at_fh_score': 'INT NOT NULL',
                                  'ht_sh_score': 'INT NOT NULL',
                                  'at_sh_score': 'INT NOT NULL',
                                  'match_date': 'DATE NOT NULL,  PRIMARY KEY(id_meci, match_date)'},
                      'primary_key': 'id_meci',
                      'create_only_if_not_exists': True}

        algorithm_db_columns = {'id_meci': 'INT NOT NULL',
                                'competitie': 'VARCHAR(30) NOT NULL',
                                'home_team': 'VARCHAR(30) NOT NULL',
                                'away_team': 'VARCHAR(30) NOT NULL',
                                'match_date': 'DATE NOT NULL',
                                'win_prediction': 'INT NOT NULL',
                                'score_prediction': 'INT NOT NULL',
                                'goals_prediction': 'INT NOT NULL,  PRIMARY KEY(id_meci, match_date)'}

    class Predictions:
        NO_PREDICTION = 0b0

        class Win:
            FULL_TIME_HOME_TEAM_WINS = 0b1
            FULL_TIME_AWAY_TEAM_WINS = 0b10
            FULL_TIME_DRAW_RESULT = 0b100
            FIRST_HALF_HOME_TEAM_WINS = 0b1000
            FIRST_HALF_AWAY_TEAM_WINS = 0b10000
            FIRST_HALF_DRAW_RESULT = 0b100000
            SECOND_HALF_HOME_TEAM_WINS = 0b1000000
            SECOND_HALF_AWAY_TEAM_WINS = 0b10000000
            SECOND_HALF_DRAW_RESULT = 0b100000000

        class Score:
            FULL_TIME_HOME_TEAM_SCORES = 0b1
            FULL_TIME_AWAY_TEAM_SCORES = 0b10
            FIRST_HALF_HOME_TEAM_SCORES = 0b100
            FIRST_HALF_AWAY_TEAM_SCORES = 0b1000
            SECOND_HALF_HOME_TEAM_SCORES = 0b10000
            SECOND_HALF_AWAY_TEAM_SCORES = 0b100000
            FULL_TIME_HOME_TEAM_NO_SCORE = 0b1000000
            FULL_TIME_AWAY_TEAM_NO_SCORE = 0b10000000
            FIRST_HALF_HOME_TEAM_NO_SCORE = 0b100000000
            FIRST_HALF_AWAY_TEAM_NO_SCORE = 0b1000000000
            SECOND_HALF_HOME_TEAM_NO_SCORE = 0b10000000000
            SECOND_HALF_AWAY_TEAM_NO_SCORE = 0b100000000000

        class Goals:
            FULL_TIME_OVER_05 = 0b1
            FULL_TIME_OVER_15 = 0b10
            FULL_TIME_OVER_25 = 0b100
            FULL_TIME_OVER_35 = 0b1000
            FIRST_HALF_OVER_05 = 0b10000
            FIRST_HALF_OVER_15 = 0b100000
            FIRST_HALF_OVER_25 = 0b1000000
            FIRST_HALF_OVER_35 = 0b10000000
            SECOND_HALF_OVER_05 = 0b100000000
            SECOND_HALF_OVER_15 = 0b1000000000
            SECOND_HALF_OVER_25 = 0b10000000000
            SECOND_HALF_OVER_35 = 0b100000000000
            FULL_TIME_UNDER_05 = 0b1000000000000
            FULL_TIME_UNDER_15 = 0b10000000000000
            FULL_TIME_UNDER_25 = 0b100000000000000
            FULL_TIME_UNDER_35 = 0b1000000000000000
            FIRST_HALF_UNDER_05 = 0b10000000000000000
            FIRST_HALF_UNDER_15 = 0b100000000000000000
            FIRST_HALF_UNDER_25 = 0b1000000000000000000
            FIRST_HALF_UNDER_35 = 0b10000000000000000000
            SECOND_HALF_UNDER_05 = 0b100000000000000000000
            SECOND_HALF_UNDER_15 = 0b1000000000000000000000
            SECOND_HALF_UNDER_25 = 0b10000000000000000000000
            SECOND_HALF_UNDER_35 = 0b100000000000000000000000


def win_to_str(what):
    result = 'WIN - '
    if what == Constants.Predictions.NO_PREDICTION:
        result += 'No prediction '
    if what & Constants.Predictions.Win.FULL_TIME_HOME_TEAM_WINS:
        result += 'Home team wins match '
    if what & Constants.Predictions.Win.FULL_TIME_AWAY_TEAM_WINS:
        result += 'Away team wins match '
    if what & Constants.Predictions.Win.FULL_TIME_DRAW_RESULT:
        result += 'Draw match '
    if what & Constants.Predictions.Win.FIRST_HALF_HOME_TEAM_WINS:
        result += 'Home team wins 1st half '
    if what & Constants.Predictions.Win.FIRST_HALF_AWAY_TEAM_WINS:
        result += 'Away team wins 1st half '
    if what & Constants.Predictions.Win.FIRST_HALF_DRAW_RESULT:
        result += 'Draw 1st half '
    if what & Constants.Predictions.Win.SECOND_HALF_HOME_TEAM_WINS:
        result += 'Home team wins 2nd half '
    if what & Constants.Predictions.Win.SECOND_HALF_AWAY_TEAM_WINS:
        result += 'Away team wins 2nd half '
    if what & Constants.Predictions.Win.SECOND_HALF_DRAW_RESULT:
        result += 'Draw 2nd half '
    if len(result) == 6:
        result += 'UNDEFINED'
    return result


def score_to_str(what):
    result = 'SCORE - '
    if what == Constants.Predictions.NO_PREDICTION:
        result += 'No prediction '
    if what == Constants.Predictions.Score.FULL_TIME_HOME_TEAM_SCORES:
        result += 'Home team scores in match '
    if what == Constants.Predictions.Score.FULL_TIME_AWAY_TEAM_SCORES:
        result += 'Away team scores in match '
    if what == Constants.Predictions.Score.FIRST_HALF_HOME_TEAM_SCORES:
        result += 'Home team scores in 1st half '
    if what == Constants.Predictions.Score.FIRST_HALF_AWAY_TEAM_SCORES:
        result += 'Away team scores in 1st half '
    if what == Constants.Predictions.Score.SECOND_HALF_HOME_TEAM_SCORES:
        result += 'Home team scores in 2nd half '
    if what == Constants.Predictions.Score.SECOND_HALF_AWAY_TEAM_SCORES:
        result += 'Away team scores in 2nd half '
    if what == Constants.Predictions.Score.FULL_TIME_HOME_TEAM_NO_SCORE:
        result += 'Home team doesn`t scores in match '
    if what == Constants.Predictions.Score.FULL_TIME_AWAY_TEAM_NO_SCORE:
        result += 'Away team doesn`t scores in match '
    if what == Constants.Predictions.Score.FIRST_HALF_HOME_TEAM_NO_SCORE:
        result += 'Home team doesn`t scores in 1st half '
    if what == Constants.Predictions.Score.FIRST_HALF_AWAY_TEAM_NO_SCORE:
        result += 'Away team doesn`t scores in 1st half '
    if what == Constants.Predictions.Score.SECOND_HALF_HOME_TEAM_NO_SCORE:
        result += 'Home team doesn`t scores in 2nd half '
    if what == Constants.Predictions.Score.SECOND_HALF_AWAY_TEAM_NO_SCORE:
        result += 'Away team doesn`t scores in 2nd half '
    if len(result) == 8:
        result += 'UNDEFINED'
    return result


def goals_to_str(what):
    result = 'GOALS - '
    if what == Constants.Predictions.NO_PREDICTION:
        result += 'No prediction '
    if what == Constants.Predictions.Goals.FULL_TIME_OVER_05:
        result += 'Over 0.5 goals in match '
    if what == Constants.Predictions.Goals.FULL_TIME_OVER_15:
        result += 'Over 1.5 goals in match '
    if what == Constants.Predictions.Goals.FULL_TIME_OVER_25:
        result += 'Over 2.5 goals in match '
    if what == Constants.Predictions.Goals.FULL_TIME_OVER_35:
        result += 'Over 3.5 goals in match '
    if what == Constants.Predictions.Goals.FIRST_HALF_OVER_05:
        result += 'Over 0.5 goals in 1st half '
    if what == Constants.Predictions.Goals.FIRST_HALF_OVER_15:
        result += 'Over 1.5 goals in 1st half '
    if what == Constants.Predictions.Goals.FIRST_HALF_OVER_25:
        result += 'Over 2.5 goals in 1st half '
    if what == Constants.Predictions.Goals.FIRST_HALF_OVER_35:
        result += 'Over 3.5 goals in 1st half '
    if what == Constants.Predictions.Goals.SECOND_HALF_OVER_05:
        result += 'Over 0.5 goals in 2nd half '
    if what == Constants.Predictions.Goals.SECOND_HALF_OVER_15:
        result += 'Over 1.5 goals in 2nd half '
    if what == Constants.Predictions.Goals.SECOND_HALF_OVER_25:
        result += 'Over 2.5 goals in 2nd half '
    if what == Constants.Predictions.Goals.SECOND_HALF_OVER_35:
        result += 'Over 3.5 goals in 2nd half '
    if what == Constants.Predictions.Goals.FULL_TIME_UNDER_05:
        result += 'Under 0.5 goals in match '
    if what == Constants.Predictions.Goals.FULL_TIME_UNDER_15:
        result += 'Under 1.5 goals in match '
    if what == Constants.Predictions.Goals.FULL_TIME_UNDER_25:
        result += 'Under 2.5 goals in match '
    if what == Constants.Predictions.Goals.FULL_TIME_UNDER_35:
        result += 'Under 3.5 goals in match '
    if what == Constants.Predictions.Goals.FIRST_HALF_UNDER_05:
        result += 'Under 0.5 goals in 1st half '
    if what == Constants.Predictions.Goals.FIRST_HALF_UNDER_15:
        result += 'Under 1.5 goals in 1st half '
    if what == Constants.Predictions.Goals.FIRST_HALF_UNDER_25:
        result += 'Under 2.5 goals in 1st half '
    if what == Constants.Predictions.Goals.FIRST_HALF_UNDER_35:
        result += 'Under 3.5 goals in 1st half '
    if what == Constants.Predictions.Goals.SECOND_HALF_UNDER_05:
        result += 'Under 0.5 goals in 2nd half '
    if what == Constants.Predictions.Goals.SECOND_HALF_UNDER_15:
        result += 'Under 1.5 goals in 2nd half '
    if what == Constants.Predictions.Goals.SECOND_HALF_UNDER_25:
        result += 'Under 2.5 goals in 2nd half '
    if what == Constants.Predictions.Goals.SECOND_HALF_UNDER_35:
        result += 'Under 3.5 goals in 2nd half '
    if len(result) == 8:
        result += 'UNDEFINED'
    return result
