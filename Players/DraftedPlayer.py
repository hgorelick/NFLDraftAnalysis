from Players.Player import Player


class DraftedPlayer(Player):
    """
    An object representing a single NFL player drafted between 2004 - 2015
    All data is pulled from Pro-Football-Reference at:
    https://www.pro-football-reference.com/play-index/draft-finder.cgi
    """

    def __init__(self, year, rnd, pick, name, prof_url, pos, age, drafted_by, career_length, college, av,
                 games_played, games_started, all_pros, pro_bowls, college_stats_link):
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
        self.rnd = rnd
        self.pick = pick
        self.age = age
        self.drafted_by = drafted_by
        self.career_length = career_length
        self.av = av
        self.games_played = games_played
        self.games_started = games_started
        self.all_pros = all_pros
        self.pro_bowls = pro_bowls
        self.college_stats_link = college_stats_link

    def __repr__(self):
        return f'name: {str(self.name)}\n' \
               f'year: {str(self.year)}\n' \
               f'drafted (rnd, pick): {str(self.rnd)}, {str(self.pick)}\n' \
               f'pos: {str(self.pos)}\n' \
               f'college: {str(self.college)}\n' \
               f'gp / gs: {str(self.games_played)} / {str(self.games_started)}\n' \
               f'ap1 / pb: {str(self.all_pros)}\n'

    def __eq__(self, other):
        """
        Overloaded equality operator
        :param other:
        :return:
        """
        return self.name == other.name and self.year == other.year and self.rnd == other.rnd and \
            self.pick == other.pick and self.pos == other.pos and self.college == other.college and \
            self.games_played == other.games_played and self.games_started == other.games_started and \
            self.all_pros == other.all_pros and self.pro_bowls == other.pro_bowls
