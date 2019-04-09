from Players.Player import *


class PlayerWithAwards(Player):
    """
       An object representing a single NFL player drafted between 2004 - 2015. Contains
       information about the awards this player has won in his career.
       All data is pulled from https://www.pro-football-reference.com/
    """

    def __init__(self, name, pos, college, awards, total_pro_bowls):
        """
        Initializes a PlayerWithStats object
        """
        super().__init__(name, pos, college)
        self.awards_score = self.calc_awards_score(awards, total_pro_bowls)
        self.pick_value = 0.0

    @staticmethod
    def calc_awards_score(awards, total_pro_bowls):
        """
        Returns this player's awards score according to the formula outlined on nfl.com:
        This player's awards score equals the sum of:
            - # of MVPs * 7
            - # of Player of the Year * 6
            - # of 1st Team All Pros * 5
            - Rookie of the Year * 4
            - Pro Bowls within first two years * 3
            - All other pro bowls
        :param awards:
        :param total_pro_bowls:
        :return:
        """
        other_pro_bowls = total_pro_bowls - awards["pro bowls"]
        return (awards["MVP"] * 7) + (awards["Off. PoY"] * 6) + (awards["Def. PoY"] * 6) + (awards["all pros"] * 5) + \
               (awards["Off. RoY"] * 4) + (awards["Def. RoY"] * 4) + (awards["pro bowls"] * 3) + other_pro_bowls
