from Players.Player import *


class PlayerWithStats(Player):
    """
    An object representing a single NFL player drafted between 2004 - 2015
    All data is pulled from one or many of the following:
        -  https://www.sports-reference.com/cfb
        -  https://www.pro-football-reference.com/
    """

    def __init__(self, name, college, pos, stats):
        """
        Initializes a PlayerWithStats object
        """
        super().__init__(name, pos, college)
        self.stats = stats


fields = ['games', 'pass_cmp', 'pass_att', 'pass_yds', 'cmp_percent', 'yp_cmp', 'pass_td', 'pass_int', 'rush_att',
          'rush_yds', 'yp_rush', 'rush_td', 'rec', 'rec_yds', 'yp_rec', 'rec_td', 'tackles_solo', 'tackles_assists',
          'tackles_loss', 'sacks', 'def_int', 'def_int_yds', 'def_int_td', 'pass_defended', 'fumbles_rec',
          'fumbles_rec_yds', 'fumbles_rec_td', 'fumbles_forced', 'kick_ret', 'kick_ret_yds', 'kick_ret_td', 'punt_ret',
          'punt_ret_yds', 'punt_ret_td']


def get_stats(stats):
    """
    Generates this player's stats from the given table
    :param stats:
    :return:
    """
    college_stats = {}

    footer = stats.find("tfoot")
    if footer is None:
        return None

    data = footer.contents[0].find_all("td", recursive=False)
    if data is None:
        return None

    for cell in data:
        if cell.attrs['data-stat'] == 'date_game':
            college_stats['games'] = int(str(cell.text).split()[0])
        if cell.attrs['data-stat'] in fields:
            if '.' in str(cell.text):
                college_stats[cell.attrs['data-stat']] = float(cell.text)
            elif cell.text != '':
                college_stats[cell.attrs['data-stat']] = int(cell.text)
            else:
                college_stats[cell.attrs['data-stat']] = 0

    for field in fields:
        if field not in college_stats.keys():
            college_stats[field] = 0

    return college_stats
