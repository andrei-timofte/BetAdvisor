import os
import sys
import json
import copy
from db_helper import db_helper as db


class Team:
    def __init__(self, name: str, aliases: list):
        self.name = name
        self.aliases = aliases
        self.stats_dict = {
            "Total": {
                "P": 0,
                "General":
                    {
                        "Pts": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PPG": 0
                    },
                "R1":
                    {
                        "Pts": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PPG": 0
                    },
                "R2":
                    {
                        "Pts": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PPG": 0
                    }
            },
            "Home": {
                "P": 0,
                "Total":
                    {
                        "Pts": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PPG": 0
                    },
                "R1":
                    {
                        "Pts": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PPG": 0
                    },
                "R2":
                    {
                        "Pts": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PPG": 0
                    }
            },
            "Away": {
                "P": 0,
                "Total":
                    {
                        "Pts": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PPG": 0
                    },
                "R1":
                    {
                        "Pts": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PPG": 0
                    },
                "R2":
                    {
                        "Pts": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PPG": 0
                    }
            }
        }

    def get_current_stats(self):
        return self.stats_dict

    def get_home_stats(self):
        return self.stats_dict["Home"]

    def get_away_stats(self):
        return self.stats_dict["Away"]

    def get_r1_stats(self):
        return self.stats_dict["Total"]["R1"]

    def get_r2_stats(self):
        return self.stats_dict["Total"]["R2"]

    def add_match_results(self, result: list):
        """
        :param result: [home_team, away_team, runda, fh_ht_score, fh_at_score, sh_ht_score, sh_at_score]
        :return: None
        """
        if self.name not in result[:2]:
            return

        self.stats_dict["Total"]["P"] += 1
        if self.name in result[0]:  # Home
            # R1
            self.stats_dict["Home"]["P"] += 1
            self.stats_dict["Total"]["General"]["GF"] += result[3]
            self.stats_dict["Total"]["General"]["GA"] += result[4]
            self.stats_dict["Total"]["R1"]["GF"] += result[3]
            self.stats_dict["Total"]["R1"]["GA"] += result[4]
            self.stats_dict["Home"]["R1"]["GF"] += result[3]
            self.stats_dict["Home"]["R1"]["GA"] += result[4]
            self.stats_dict["Home"]["Total"]["GF"] += result[3]
            self.stats_dict["Home"]["Total"]["GA"] += result[4]

            # R2
            self.stats_dict["Total"]["General"]["GF"] += result[5]
            self.stats_dict["Total"]["General"]["GA"] += result[6]
            self.stats_dict["Total"]["R2"]["GF"] += result[5]
            self.stats_dict["Total"]["R2"]["GA"] += result[6]
            self.stats_dict["Home"]["R2"]["GF"] += result[5]
            self.stats_dict["Home"]["R2"]["GA"] += result[6]
            self.stats_dict["Home"]["Total"]["GF"] += result[5]
            self.stats_dict["Home"]["Total"]["GA"] += result[6]

            # W D L R1
            if result[3] > result[4]:
                self.stats_dict["Total"]["R1"]["W"] += 1
                self.stats_dict["Home"]["R1"]["W"] += 1
            elif result[3] == result[4]:
                self.stats_dict["Total"]["R1"]["D"] += 1
                self.stats_dict["Home"]["R1"]["D"] += 1
            else:
                self.stats_dict["Total"]["R1"]["L"] += 1
                self.stats_dict["Home"]["R1"]["L"] += 1

            # W D L R2
            if result[5] > result[6]:
                self.stats_dict["Total"]["R2"]["W"] += 1
                self.stats_dict["Home"]["R2"]["W"] += 1
            elif result[5] == result[6]:
                self.stats_dict["Total"]["R2"]["D"] += 1
                self.stats_dict["Home"]["R2"]["D"] += 1
            else:
                self.stats_dict["Total"]["R2"]["L"] += 1
                self.stats_dict["Home"]["R2"]["L"] += 1

            # W D L Total
            if (result[3] + result[5]) > (result[4] + result[6]):
                self.stats_dict["Total"]["General"]["W"] += 1
                self.stats_dict["Home"]["Total"]["W"] += 1
            elif (result[3] + result[5]) == (result[4] + result[6]):
                self.stats_dict["Total"]["General"]["D"] += 1
                self.stats_dict["Home"]["Total"]["D"] += 1
            else:
                self.stats_dict["Total"]["General"]["L"] += 1
                self.stats_dict["Home"]["Total"]["L"] += 1

        else:  # Away
            # R1
            self.stats_dict["Away"]["P"] += 1
            self.stats_dict["Total"]["General"]["GF"] += result[4]
            self.stats_dict["Total"]["General"]["GA"] += result[3]
            self.stats_dict["Total"]["R1"]["GF"] += result[4]
            self.stats_dict["Total"]["R1"]["GA"] += result[3]
            self.stats_dict["Away"]["R1"]["GF"] += result[4]
            self.stats_dict["Away"]["R1"]["GA"] += result[3]
            self.stats_dict["Away"]["Total"]["GF"] += result[4]
            self.stats_dict["Away"]["Total"]["GA"] += result[3]

            # R2
            self.stats_dict["Total"]["General"]["GF"] += result[6]
            self.stats_dict["Total"]["General"]["GA"] += result[5]
            self.stats_dict["Total"]["R2"]["GF"] += result[6]
            self.stats_dict["Total"]["R2"]["GA"] += result[5]
            self.stats_dict["Away"]["R2"]["GF"] += result[6]
            self.stats_dict["Away"]["R2"]["GA"] += result[5]
            self.stats_dict["Away"]["Total"]["GF"] += result[6]
            self.stats_dict["Away"]["Total"]["GA"] += result[5]

            # W D L R1
            if result[4] > result[3]:
                self.stats_dict["Total"]["R1"]["W"] += 1
                self.stats_dict["Away"]["R1"]["W"] += 1
            elif result[4] == result[3]:
                self.stats_dict["Total"]["R1"]["D"] += 1
                self.stats_dict["Away"]["R1"]["D"] += 1
            else:
                self.stats_dict["Total"]["R1"]["L"] += 1
                self.stats_dict["Away"]["R1"]["L"] += 1

            # W D L R2
            if result[6] > result[5]:
                self.stats_dict["Total"]["R2"]["W"] += 1
                self.stats_dict["Away"]["R2"]["W"] += 1
            elif result[6] == result[5]:
                self.stats_dict["Total"]["R2"]["D"] += 1
                self.stats_dict["Away"]["R2"]["D"] += 1
            else:
                self.stats_dict["Total"]["R2"]["L"] += 1
                self.stats_dict["Away"]["R2"]["L"] += 1

            # W D L Total
            if (result[4] + result[6]) > (result[3] + result[5]):
                self.stats_dict["Total"]["General"]["W"] += 1
                self.stats_dict["Away"]["Total"]["W"] += 1
            elif (result[4] + result[6]) == (result[3] + result[5]):
                self.stats_dict["Total"]["General"]["D"] += 1
                self.stats_dict["Away"]["Total"]["D"] += 1
            else:
                self.stats_dict["Total"]["General"]["L"] += 1
                self.stats_dict["Away"]["Total"]["L"] += 1

        # Actualizare date
        self.stats_dict["Total"]["General"]["Pts"] = 3 * self.stats_dict["Total"]["General"]["W"] + \
                                                     self.stats_dict["Total"]["General"]["D"]
        self.stats_dict["Total"]["R1"]["Pts"] = 3 * self.stats_dict["Total"]["R1"]["W"] + \
                                                self.stats_dict["Total"]["R1"]["D"]
        self.stats_dict["Total"]["R2"]["Pts"] = 3 * self.stats_dict["Total"]["R2"]["W"] + \
                                                self.stats_dict["Total"]["R2"]["D"]
        self.stats_dict["Total"]["General"]["GD"] = self.stats_dict["Total"]["General"]["GF"] - \
                                                    self.stats_dict["Total"]["General"]["GA"]
        self.stats_dict["Total"]["R1"]["GD"] = self.stats_dict["Total"]["R1"]["GF"] - self.stats_dict["Total"]["R1"]["GA"]
        self.stats_dict["Total"]["R2"]["GD"] = self.stats_dict["Total"]["R2"]["GF"] - self.stats_dict["Total"]["R2"]["GA"]
        self.stats_dict["Total"]["General"]["PPG"] = self.stats_dict["Total"]["General"]["Pts"] / \
                                                     self.stats_dict["Total"]["P"]
        self.stats_dict["Total"]["R1"]["PPG"] = self.stats_dict["Total"]["R1"]["Pts"] / self.stats_dict["Total"]["P"]
        self.stats_dict["Total"]["R2"]["PPG"] = self.stats_dict["Total"]["R2"]["Pts"] / self.stats_dict["Total"]["P"]

        self.stats_dict["Home"]["Total"]["Pts"] = 3 * self.stats_dict["Home"]["Total"]["W"] + \
                                                  self.stats_dict["Home"]["Total"]["D"]
        self.stats_dict["Home"]["R1"]["Pts"] = 3 * self.stats_dict["Home"]["R1"]["W"] + self.stats_dict["Home"]["R1"]["D"]
        self.stats_dict["Home"]["R2"]["Pts"] = 3 * self.stats_dict["Home"]["R2"]["W"] + self.stats_dict["Home"]["R2"]["D"]
        self.stats_dict["Home"]["Total"]["GD"] = self.stats_dict["Home"]["Total"]["GF"] - \
                                                 self.stats_dict["Home"]["Total"]["GA"]
        self.stats_dict["Home"]["R1"]["GD"] = self.stats_dict["Home"]["R1"]["GF"] - self.stats_dict["Home"]["R1"]["GA"]
        self.stats_dict["Home"]["R2"]["GD"] = self.stats_dict["Home"]["R2"]["GF"] - self.stats_dict["Home"]["R2"]["GA"]
        if self.stats_dict["Home"]["P"] > 0:
            self.stats_dict["Home"]["Total"]["PPG"] = self.stats_dict["Home"]["Total"]["Pts"] / self.stats_dict["Home"]["P"]
            self.stats_dict["Home"]["R1"]["PPG"] = self.stats_dict["Home"]["R1"]["Pts"] / self.stats_dict["Home"]["P"]
            self.stats_dict["Home"]["R2"]["PPG"] = self.stats_dict["Home"]["R2"]["Pts"] / self.stats_dict["Home"]["P"]

        self.stats_dict["Away"]["Total"]["Pts"] = 3 * self.stats_dict["Away"]["Total"]["W"] + \
                                                  self.stats_dict["Away"]["Total"]["D"]
        self.stats_dict["Away"]["R1"]["Pts"] = 3 * self.stats_dict["Away"]["R1"]["W"] + self.stats_dict["Away"]["R1"]["D"]
        self.stats_dict["Away"]["R2"]["Pts"] = 3 * self.stats_dict["Away"]["R2"]["W"] + self.stats_dict["Away"]["R2"]["D"]
        self.stats_dict["Away"]["Total"]["GD"] = self.stats_dict["Away"]["Total"]["GF"] - \
                                                 self.stats_dict["Away"]["Total"]["GA"]
        self.stats_dict["Away"]["R1"]["GD"] = self.stats_dict["Away"]["R1"]["GF"] - self.stats_dict["Away"]["R1"]["GA"]
        self.stats_dict["Away"]["R2"]["GD"] = self.stats_dict["Away"]["R2"]["GF"] - self.stats_dict["Away"]["R2"]["GA"]
        if self.stats_dict["Away"]["P"] > 0:
            self.stats_dict["Away"]["Total"]["PPG"] = self.stats_dict["Away"]["Total"]["Pts"] / self.stats_dict["Away"]["P"]
            self.stats_dict["Away"]["R1"]["PPG"] = self.stats_dict["Away"]["R1"]["Pts"] / self.stats_dict["Away"]["P"]
            self.stats_dict["Away"]["R2"]["PPG"] = self.stats_dict["Away"]["R2"]["Pts"] / self.stats_dict["Away"]["P"]


class StatsProvider:
    """
    Clasa asta primeste un fisier cu rezultatele meciurilor unei competitii si ofera statistici pentru echipe la un
    anumit moment in competitie.
    La incput, toate echipele sunt pe pozitia 1 si au 0 puncte.
    Statisticile pe care le ofera sunt:
    Place (loc in clasament in functie de punctele acumulate)
    Played (meciuri jucate pana la acel moment)
    Wins
    Draws
    Lost
    GoalsFor (goluri marcate)
    GoalsAgainst (goluri primite)
    GoalsDifference (diferenta intre golurile marcate si cele primite)
    Points (puncte acumulate: 3 pentru fiecare victorie, 1 pentru remiza, 0 pentru pierdute)
    PointsPerGame (cate punte a luat in medie pe fiecare meci = points/played (float))
    WinsHome
    DrawsHome
    LostHome
    GoalsForHome
    GoalsAgainstHome
    PointsPerGameHome
    PointsPerGameAway
    WinsAway
    DrawsAway
    LostAway
    GoalsForAway
    GoalsAgainstAway
    """
    def __init__(self, competition, auto_update_stats=True):
        self.competition = competition
        if not os.path.isfile('teams_aliases.json'):
            raise Exception("Fisierul team_aliases.json nu exista!")
        with open('teams_aliases.json', 'rt') as f:
            aliases = json.load(f)
            if competition not in aliases.keys():
                raise Exception("Nu am gasit competitia {} in teams_aliases.json".format(competition))
        self.competition_teams = [Team(team, aliases[competition][team]) for team in db.get_competition_teams(competition)]
        self.matches = db.get_competition_all_matches(competition)
        if auto_update_stats:
            for match in self.matches:
                self.process_match(match)
                # for team in self.competition_teams:
                #     team.add_match_results(match)

    def get_team_stats(self, team_name):
        for team in self.competition_teams:
            if team.name == team_name:
                return team.get_current_stats()
        # raise Exception('Nu am gasit nici o echipa cu numele {} in competita {}'.format(team_name, self.competition))
        return None
    def get_team(self, team_name):
        for team in self.competition_teams:
            if team.name == team_name:
                return team
        raise Exception('Nu am gasit nici o echipa cu numele {} in competita {}'.format(team_name, self.competition))

    def process_match(self, match: list):
        for team in self.competition_teams:
            team.add_match_results(match)

    def report_stats(self, team_home, team_away):
        result = {}
        for team in self.competition_teams:
            if team.name == team_home:
                result[team_home] = team.get_current_stats()
            elif team.name == team_away:
                result[team_away] = team.get_current_stats()
        return result

