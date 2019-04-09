from Players.Player import Player


class CombinePlayer(Player):
    """
    An object representing a single NFL player who participated in the
    NFL Scouting Combine between 2004 - 2015.
    All data is pulled from Pro-Football-Reference at:
    https://www.pro-football-reference.com/play-index/nfl-combine-results.cgi
    """

    def __init__(self, year, name, prof_url, pos, college, college_stats_link, height, weight, forty,
                 vert, bench, broad, cone, shuttle):
        """
        Initializes a DraftedPlayer object

        Parameters:
        - 'year'           - the year this player was drafted
        - 'rnd'            - the round this player was drafted
        - 'pick'           - the pick (in that round, not overall) this player was drafted
        - 'name'           - this player's name
        - 'pos'            - this player's position
        - 'college'        - where this player went to college
        - 'games_played'   - the number of games in which this player has appeared
        - 'games_started'  - the number of games in which this player has started
        - 'all_pros'       - the number of times this player has been named "1st Team All Pro"
        - 'pro_bowls'      - the number of times this player has made the Pro Bowl
        """
        super().__init__(name, pos, college)
        self.year = year
        self.prof_url = prof_url
        self.college_stats_link = college_stats_link
        self.height = height
        self.weight = weight
        self.forty = forty
        self.vert = vert
        self.bench = bench
        self.broad = broad
        self.cone = cone
        self.shuttle = shuttle

    def __repr__(self):
        return f'name: {self.name}\n' \
               f'year: {str(self.year)}\n' \
               f'pos: {self.pos}\n' \
               f'college: {self.college}\n' \
               f'height: {self.height}\n' \
               f'weight: {str(self.weight)}\n' \
               f'forty: {str(self.forty)}\n' \
               f'vert: {str(self.vert)}\n' \
               f'bench: {str(self.bench)}\n' \
               f'broad: {str(self.broad)}\n' \
               f'cone: {str(self.cone)}\n' \
               f'shuttle: {str(self.shuttle)}\n'

    def __eq__(self, other):
        """
        Overloaded equality operator
        :param other:
        :return:
        """
        return self.name == other.name and self.year == other.year and self.pos == other.pos and \
            self.college == other.college and self.height == other.height and self.weight == other.weight and \
            self.forty == other.forty and self.vert == other.vert and self.bench == other.bench and \
            self.broad == other.broad and self.cone == other.cone and self.shuttle == other.shuttle
