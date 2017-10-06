from algorithm import Algorithm
from constants import *


class Algorithm6(Algorithm):
    def run(self):
        self.name = "Over/Under 2.5 tip 1"
        self.description = """Acest algoritm foloseste o modalitate de analiza luata de pe net (nu mai stiu exact de unde):
Hello!
My name is Vincent and I want to share my betting strategy with you. I play on over/under 2.5 goals in football matches like this:

I take into consideration the last 4 matches of each team involved in the current game (that's 8 matches in total).
If a game has ended with an over 2.5 score I give it +0.5 points.
If both teams scored in that match I give it another +0.75 points (even if the match ended under 2.5).
If the game ended under 2.5 I give it -0.5 points.
If one of the teams didn't score in the match (even if it was over 2.5) I give it -0.75 points.

In the end I sum up all those points and I get a positive or negative result. To give an example:

match results 4:2 2:1 2:2 0:0 2:0 2:1 3:1 3:0

For the above matches my calculation would look like this:

+0.5 +0.75 +0.5 +0.75 +0.5 +0.75 -0.5 -0.75 -0.5 -0.75 +0.5 +0.75 +0.5 +0.75+ 0.5- 0.75 =+3.5 points.

That would mean to put a 3.5/10 units bet on over 2.5 goals. The maximum results are +10 and -10 points. That would mean a certain over 2.5, respectively under 2.5 goals match.

I usually place a bet only if I get a minimum +/-5 points result. So, for example, if I get a +6 I place a 6/10 units bet on over 2.5 goals. 
        """
        print(self.name)
        self.db_name = 'algorithm6.db'
        self.init_db()
        self.treshold = 6
        while True:
            val = self.queue.get()
            if val is None:
                return
            self.analyze(val)

    def analyze(self, match_info):
        print(self.name, "Analyzing: {}".format(match_info))
        match_id = list(match_info.keys())[0]
        if self.db.record_exists(int(match_id)):
            predictie = self.db.get_records(match_id)
            if predictie[-1] != 0:
                print(predictie[-1])
            print('Am deja analiza mecului cu id {}:{}'.format(match_id, 'Aici vine analiza!'))
        else:
            # Analiza propriu-zisa
            score = 0
            home_stats = match_info[match_id][0]['Stats']['Home_History']
            away_stats = match_info[match_id][0]['Stats']['Away_History']

            for match in home_stats[:4]:
                if sum(match[1:-1]) > 2:
                    score += 0.5
                else:
                    score -= 0.5
                if (match[1] + match[3]) > 0 and (match[2] + match[4]) > 0:
                    score += 0.75
                else:
                    score -= 0.75
            for match in away_stats[:4]:
                if sum(match[1:-1]) > 2:
                    score += 0.5
                else:
                    score -= 0.5
                if (match[1] + match[3]) > 0 and (match[2] + match[4]) > 0:
                    score += 0.75
                else:
                    score -= 0.75

            print(score)
            predict = Constants.Predictions.FULL_TIME_OVER_25 if (score >= abs(self.treshold) or
                                                                  score <= (-1 * abs(self.treshold))) else 0

            self.db.insert_record({'id_meci': match_id,
                                   'competitie': match_info[match_id][1][1],
                                   'home_team': match_info[match_id][1][2],
                                   'away_team': match_info[match_id][1][3],
                                   'match_date': match_info[match_id][1][4],
                                   'prediction': predict},
                                  json_must_exist=False)
            if predict > 0:
                print('PREDICTIE: {}'.format('PESTE 2,5' if score >= abs(self.treshold) else
                                             'SUB 2.5' if score <= (-1 * abs(self.treshold))
                                             else ''))
