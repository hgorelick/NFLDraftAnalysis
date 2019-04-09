#!/usr/bin/env python37
from Players.DraftedPlayer import *
from Players.CombinePlayer import *
from Players.PlayerWithStats import *
from Players.PlayerWithAwards import *

from write_pfr_db import *

import _pickle as pickle
import os
from contextlib import closing

import sqlite3
from twilio.rest import Client
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *

# Constants
PLAYERS_PER_PAGE = 300
TOTAL_ROWS = 2700
DRAFTED_PLAYERS = 2471
COMBINE_PLAYERS = 2174

UBLOCK_PATH = os.getcwd() + "\\1.17.0_0"
UBLOCK = Options()
UBLOCK.add_argument('load-extension=' + UBLOCK_PATH)
UBLOCK.add_argument('--ignore-certificate-errors')
UBLOCK.add_argument('--ignore-ssl-errors')

BROWSER_PATH = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'

PFR_URL = "https://www.pro-football-reference.com"

DRAFTED_URL = "https://www.pro-football-reference.com/play-index/draft-finder.cgi?request=1&" \
              "year_min=2004&year_max=2015&draft_slot_min=1&draft_slot_max=500&pick_type=overall&" \
              "pos%5B%5D=qb&pos%5B%5D=rb&pos%5B%5D=wr&pos%5B%5D=te&pos%5B%5D=e&pos%5B%5D=dt&pos%5B%5D=de" \
              "&pos%5B%5D=dl&pos%5B%5D=ilb&pos%5B%5D=olb&pos%5B%5D=lb&pos%5B%5D=cb&pos%5B%5D=s&pos%5B%5D=db&" \
              "conference=any&show=all&order_by=draft_round&order_by_asc=Y&offset="

COMBINE_PREFIX = "https://www.pro-football-reference.com/play-index/nfl-combine-results.cgi?request=1&" \
                 "year_min="

OFFENSE_URL = "&pos%5B%5D=QB&pos%5B%5D=WR&pos%5B%5D=TE&pos%5B%5D=RB"

DEFENSE_URL = "&pos%5B%5D=DE&pos%5B%5D=DT&pos%5B%5D=EDGE&pos%5B%5D=ILB&pos%5B%5D=OLB&pos%5B%5D=SS&pos%5B%5D=FS&" \
              "pos%5B%5D=S&pos%5B%5D=CB"

COMBINE_SUFFIX = "&show=all&order_by=year_id&order_by_asc=Y"


class PFRScraper:
    """
    The main webcrawler class that retrieves the DraftedPlayers from pro-football-reference.com
    """
    def __init__(self):
        """
        Initializes a PFRScraper object
        """
        self.DraftedPlayers = []
        self.CombinePlayers = []
        self.PlayersPickValues = []
        self.CollegePlayersStats = []

        self.rush_rec = {"QB", "RB", "WR", "TE"}
        self.defense = {"CB", "DB", "DE", "DL", "DT", "ILB", "LB", "NT", "OLB", "S"}
        self.ol = {"C", "G", "OL", "T"}

    def get_players(self, url):
        """
        Builds a table of players from the given url
        """
        if url == COMBINE_PREFIX:
            url = COMBINE_PREFIX + str(2004) + "&year_max=" + str(2004) + OFFENSE_URL + COMBINE_SUFFIX

        with closing(Chrome(BROWSER_PATH, options=UBLOCK)) as browser:
            browser.create_options()
            browser.get(url)
            browser.maximize_window()
            WebDriverWait(browser, timeout=10).until(
                lambda x: x.find_element_by_class_name("overthrow")
            )

            page = browser.page_source
            pfr = BeautifulSoup(page, "lxml")

            if url == DRAFTED_URL:
                self.get_drafted_players(browser, pfr)

            elif COMBINE_PREFIX in url:
                self.get_combine_players(browser, pfr)

    def get_drafted_players(self, browser, soup):
        """
        Builds a table of players drafted between 2004 - 2015 from pro-football-reference.com
        """
        player_counter = 1
        offset = 300

        for i in range(int(DRAFTED_PLAYERS / PLAYERS_PER_PAGE) + 1):
            url_to_use = ""
            if i > 0:
                url_to_use = DRAFTED_URL.split("offset=")[0] + "offset=" + str(offset)
                offset += 300

                browser.get(url_to_use)
                WebDriverWait(browser, timeout=10).until(
                    lambda x: x.find_element_by_class_name("overthrow")
                )
                page = browser.page_source
                soup = BeautifulSoup(page, "lxml")

            players_list = soup.find("table", id="results").contents[6].find_all("tr", recursive=False)

            header_row = 30
            for item in players_list:
                if int(item.attrs['data-row']) == header_row:
                    header_row += 31
                    continue

                if header_row > 278:
                    header_row = 30

                if str(item.contents[5].text) in self.ol or str(item.contents[5].text) == 'FB':
                    continue

                year = int(item.contents[1].text)
                rnd = int(item.contents[2].text)
                pick = int(item.contents[3].text)
                name = str(item.contents[4].text)
                pos = str(item.contents[5].text)

                player_info = get_nulls(item, draft=True)
                if player_info is None:
                    continue

                age = player_info[0]
                drafted_by = str(item.contents[7].text)
                career_length = player_info[1]
                all_pros = player_info[2]
                pro_bowls = player_info[3]
                av = player_info[4]
                games_played = player_info[5]
                games_started = player_info[6]
                prof_url = player_info[7]

                if u'\u2013' in item.contents[30].text:
                    college = str(item.contents[30].text.replace(u'\u2013', '-'))
                else:
                    college = str(item.contents[30].text)
                if "St." in college[-3:]:
                    college = college.replace("St.", "State")

                try:
                    college_stats_link = str(item.contents[31].contents[0].attrs['href'])[:-5] + "/gamelog/"
                except IndexError:
                    college_stats_link = ""

                print(f"Adding DraftedPlayer {player_counter} of {DRAFTED_PLAYERS}")
                player_counter += 1
                if len(self.DraftedPlayers) == 0:
                    self.DraftedPlayers = [DraftedPlayer(year, rnd, pick, name, prof_url, pos, age, drafted_by,
                                                         career_length, college, av, games_played, games_started,
                                                         all_pros, pro_bowls, college_stats_link)]
                else:
                    self.DraftedPlayers.append(DraftedPlayer(year, rnd, pick, name, prof_url, pos, age, drafted_by,
                                                             career_length, college, av, games_played, games_started,
                                                             all_pros, pro_bowls, college_stats_link))

        try:
            write_drafted_table(self.DraftedPlayers)

        except sqlite3.OperationalError:
            # catch sqlite error and write table data to txt file
            with open("DraftedPlayers.txt", "wb+") as f:
                pickle.dump(self.DraftedPlayers, f)
            f.close()

    def get_combine_players(self, browser, soup):
        """
        Builds a table of players who both participated in the NFL Scouting Combine between 2004 - 2015,
        and then played in the NFL. (there are players who participated in the combine but never played)
        :param browser:
        :param soup:
        """

        # uncomment line below if loading from pickle file
        # self.DraftedPlayers = pickle.load(open("DraftedPlayers.txt", "rb+"))

        player_counter = 1
        max_year = 2015
        combine_year = 2004
        defense = False

        while combine_year <= max_year:
            if combine_year > 2004:
                url = COMBINE_PREFIX + str(combine_year) + "&year_max=" + str(combine_year) + \
                      (DEFENSE_URL if defense else OFFENSE_URL) + COMBINE_SUFFIX
                browser.get(url)
                WebDriverWait(browser, timeout=10).until(
                    lambda x: x.find_element_by_class_name("overthrow")
                )
                page = browser.page_source
                soup = BeautifulSoup(page, "lxml")

            players_list = soup.find("table", id="results").contents[6].find_all("tr", recursive=False)
            header_row = 50

            for item in players_list:
                if int(item.attrs['data-row']) == header_row:
                    header_row += 51
                    continue

                if header_row > 203:
                    header_row = 50

                year = int(item.contents[1].text)
                name = str(item.contents[2].text)
                pos = str(item.contents[3].text)

                if u'\u2013' in item.contents[5].text:
                    college = str(item.contents[5].text.replace(u'\u2013', '-'))
                else:
                    college = str(item.contents[5].text)
                if "St." in college[-3:]:
                    college = college.replace("St.", "State")

                if item.contents[4].text == u'' and not contains(Player(name, pos, college), "DraftedPlayers"):
                    continue

                try:
                    prof_url = str(item.contents[2].contents[0].attrs['href'])
                except IndexError:
                    if contains(Player(name, pos, college), "DraftedPlayers"):
                        prof_url = find(Player(name, pos, college), "DraftedPlayers").prof_url
                    else:
                        prof_url = ""

                try:
                    college_stats_link = str(item.contents[6].contents[0].attrs['href'])
                except IndexError:
                    college_stats_link = ""

                height = str(item.contents[7].text)
                weight = int(item.contents[8].text)
                player_info = get_nulls(item, combine=True)
                forty = player_info[0]
                vert = player_info[1]
                bench = player_info[2]
                broad = player_info[3]
                cone = player_info[4]
                shuttle = player_info[5]

                print(f"Adding CombinePlayer {player_counter} of {COMBINE_PLAYERS}")
                player_counter += 1
                if len(self.CombinePlayers) == 0:
                    self.CombinePlayers = [CombinePlayer(year, name, prof_url, pos, college, college_stats_link, height,
                                                         weight, forty, vert, bench, broad, cone, shuttle)]
                else:
                    self.CombinePlayers.append(CombinePlayer(year, name, prof_url, pos, college, college_stats_link,
                                                             height, weight, forty, vert, bench, broad, cone, shuttle))
            combine_year += 1
            if combine_year == 2016 and not defense:
                combine_year = 2004
                defense = True
                url = COMBINE_PREFIX + str(combine_year) + "&year_max=" + str(combine_year) + \
                    DEFENSE_URL + COMBINE_SUFFIX
                browser.get(url)
                WebDriverWait(browser, timeout=10).until(
                    lambda x: x.find_element_by_class_name("overthrow")
                )
                page = browser.page_source
                soup = BeautifulSoup(page, "lxml")

        try:
            write_combine_table(self.CombinePlayers)

        except sqlite3.OperationalError:
            # catch sqlite error and write table data to txt file
            with open("CombinePlayers.txt", "wb+") as f:
                pickle.dump(self.CombinePlayers, f)
            f.close()

    def get_pick_value(self):
        """
        Similar to get_drafted_players(), but calculates player_pick_val column. See
        the Appendix section of the .docx report for the formula
        """
        print("Connecting to SQLite3")
        conn = sqlite3.connect('PFR.db')
        cursor = conn.cursor()
        print("SQLite3 Connected")

        append = self.PlayersPickValues.append
        award_names = ["MVP", "Def. RoY", "Off. RoY", "Def. PoY", "Off. PoY", "all pros", "pro bowls"]

        with closing(Chrome(BROWSER_PATH, options=UBLOCK)) as browser:
            browser.create_options()
            browser.maximize_window()

            player_counter = 1
            row_count = len(cursor.execute('select * from DraftedPlayers order by name;').fetchall())
            for row in conn.execute('select * from DraftedPlayers order by name;'):
                url = PFR_URL + row[4]
                if url == PFR_URL:
                    continue
                awards = {k: 0 for k in award_names}
                name = row[3]
                pos = row[5]
                college = row[8]
                pro_bowls = row[-2]

                browser.get(url)
                try:
                    WebDriverWait(browser, timeout=5).until(
                        lambda x: x.find_element_by_class_name("overthrow")
                    )
                    page = browser.page_source
                    soup = BeautifulSoup(page, "lxml")

                    bling = soup.find("div", id="info", class_="players").find("ul", id="bling")
                    if bling is not None:
                        bling = bling.find_all("li", class_="bling_special", recursive=False)
                        if bling is not None:
                            for award in bling:
                                if "Def. RoY" in str(award.contents[0].text):
                                    awards["Def. RoY"] = 1
                                elif "Off. RoY" in str(award.contents[0].text):
                                    awards["Off. RoY"] = 1
                                elif "Off. PoY" in str(award.contents[0].text):
                                    awards["Off. PoY"] += 1
                                elif "Def. PoY" in str(award.contents[0].text):
                                    awards["Def. PoY"] += 1
                                elif "MVP" in str(award.contents[0].text):
                                    awards["MVP"] = int(str(award.contents[0].text).split("x ")[0])

                    pro_bowl_table = soup.find("div", id="leaderboard_pro_bowls")
                    if pro_bowl_table is not None:
                        pro_bowl_table = pro_bowl_table.find_all("td", recursive=False)
                        if pro_bowl_table is not None:
                            for year in pro_bowl_table:
                                if int(year.contents[0].text) <= row[0] + 2:
                                    awards["pro bowls"] += 1

                    player = PlayerWithAwards(name, pos, college, awards, pro_bowls)
                    player.pick_value = calc_pick_value(row, player)

                    print(f"Adding {name}'s pick value -> player {player_counter} of {str(row_count)}")
                    player_counter += 1

                    append(player)

                except TimeoutException:
                    continue

        try:
            write_player_pick_values(self.PlayersPickValues)

        except sqlite3.OperationalError:
            # catch sqlite error and write table data to txt file
            with open("PlayersPickValues.txt", "wb+") as f:
                pickle.dump(self.PlayersPickValues, f)
            f.close()

    def get_all_college_stats(self):
        """
        Builds a table containing the collegiate stats of players in DraftedPlayers
        """
        print("Connecting to SQLite3")
        conn = sqlite3.connect('PFR.db')
        cursor = conn.cursor()
        print("SQLite3 Connected")

        bad_records = []
        append_b = bad_records.append

        with closing(Chrome(BROWSER_PATH, options=UBLOCK)) as browser:
            browser.create_options()
            browser.maximize_window()

            player_counter = 1
            append = self.CollegePlayersStats.append

            row_count = len(cursor.execute('select * from HasCollegeStats order by name;').fetchall())
            for row in conn.execute('select * from HasCollegeStats order by name;'):
                url = row[-1]
                name = row[3]
                pos = row[5]
                college = row[8]
                if "pac-man" in url:
                    url = url.replace("pac-man", "adam")
                browser.get(url)
                try:
                    WebDriverWait(browser, timeout=5).until(
                        lambda x: x.find_element_by_class_name("overthrow")
                    )
                    page = browser.page_source
                    soup = BeautifulSoup(page, "lxml")

                    stats = soup.find("table", id="gamelog")
                    if stats is not None:
                        college_stats = get_stats(stats)
                        if college_stats is None:
                            append_b((name, pos, college))
                            continue
                        print(f"Getting {name}'s collegiate stats -> player {player_counter} of {str(row_count)}")
                        player = PlayerWithStats(name, college, pos, college_stats)
                        append(calc_percentages(player))
                        player_counter += 1

                except TimeoutException:
                    append_b((name, pos, college))
                    continue

        try:
            write_college_stats(self.CollegePlayersStats)

        except sqlite3.OperationalError:
            # catch sqlite error and write table data to txt file
            with open("CollegePlayerStats.txt", "wb+") as f:
                pickle.dump(self.CollegePlayersStats, f)
            f.close()

        # remove players in DraftedPlayers with bad data
        for record in bad_records:
            delete = f"delete from DraftedPlayers where name = \'{record[0]}\' and " \
                f"pos = \'{record[1]}\' and college = \'{record[2]}\';"
            cursor.execute(delete)
            conn.commit()

    def get_table_by_pos(self, pos, soup):
        """
        Helper method that Returns the table containing the given player's statistics,
        which are different for certain position groups
        :param pos:
        :param soup:
        :return:
        """
        stats = None
        if pos == "QB":
            stats = soup.find("div", id="all_passing")

        elif pos in self.rush_rec:
            stats = soup.find("div", id="all_receiving_and_rushing") or \
                    soup.find("div", id="all_rushing_and_receiving")

        elif pos in self.defense:
            stats = soup.find("div", id="all_defense")

        return stats

    def add_year_round_pick_to_values(self, player_pick_values):
        """
        Helper method to use if DraftedPlayers does not contain a player_pick_val column
        :param player_pick_values:
        :return:
        """
        print("Connecting to SQLite3")
        conn = sqlite3.connect('PFR.db')
        cursor = conn.cursor()
        print("SQLite3 Connected")

        append = self.PlayersPickValues.append

        multiple_results = []
        append_m = multiple_results.append

        for player in player_pick_values:
            query = f"select year, round, pick from DraftedPlayers where name = '" + player.name + f"' and " \
                f"pos = \'{player.pos}\' and college = \'{player.college}\';"

            row = list(sum(cursor.execute(
                "select year, round, pick from DraftedPlayers where name = ? and pos = ? and college = ?;",
                (player.name, player.pos, player.college)).fetchall(), ()))

            if len(row) > 3:
                append_m(player)
                continue
            player.year = row[0]
            player.round = row[1]
            player.pick = row[2]
            append(player)

        conn.close()

        try:
            write_player_pick_values(self.PlayersPickValues)

        except sqlite3.OperationalError:
            # catch sqlite error and write table data to txt file
            with open("PlayersPickValues.txt", "wb+") as f:
                pickle.dump(self.PlayersPickValues, f)
            f.close()

        # in the case that a query returns more than one row,
        # save those query results to a text file for later inspection
        with open("MultipleResults.txt", "wb+") as f:
            pickle.dump(multiple_results, f)
        f.close()


def calc_percentages(player):
    """
    Helper method for recalculating percentage and/or yards-per stats
    :param player:
    :return:
    """
    if player.stats is None:
        player.stats.update({'cmp_percent': 0.0, 'yp_cmp': 0.0, 'yp_rush': 0.0, 'yp_rec': 0.0})
        if player.stats['pass_cmp'] > 0:
            if player.stats['pass_cmp'] > 67:
                player.stats['cmp_percent'] = float(player.stats['pass_cmp'] / player.stats['pass_att'])
                player.stats['yp_cmp'] = float(player.stats['pass_yds'] / player.stats['pass_cmp'])
            elif player.pos != "QB":
                player.stats['pass_cmp'] = 0
                player.stats['pass_att'] = 0
                player.stats['pass_yds'] = 0
                player.stats['pass_td'] = 0
                player.stats['pass_int'] = 0
        if player.stats['rush_att'] > 0:
            if player.stats['rush_yds'] <= 0:
                player.stats['rush_att'] = player.stats['rush_yds'] = player.stats['rush_td']
            if player.stats['rush_att'] > 0:
                player.stats['yp_rush'] = float(player.stats['rush_yds'] / player.stats['rush_att'])
        if player.stats['rec'] > 0:
            if player.stats['rec'] > 9:
                player.stats['yp_rec'] = float(player.stats['rec_yds'] / player.stats['rec'])
            else:
                player.stats['rec'] = 0
                player.stats['rec_yds'] = 0
                player.stats['rec_td'] = 0

    return player


def get_nulls(item, draft=False, combine=False):
    """
    Helper method for processing null fields when web scraping
    :param draft:
    :param combine:
    :param item:
    """
    if draft:
        try:
            prof_url = str(item.contents[4].contents[0].attrs['href'])
        except (KeyError, AttributeError):
            try:
                prof_url = str(item.contents[4].contents[0].contents[0].attrs['href'])
            except AttributeError:
                prof_url = ""
        try:
            age = int(item.contents[6].text)
        except ValueError:
            age = 22
        try:
            career_length = int(item.contents[9].text) - int(item.contents[8].text)
        except ValueError:
            career_length = 0
        try:
            all_pros = int(item.contents[10].text)
        except ValueError:
            all_pros = 0
        try:
            pro_bowls = int(item.contents[11].text)
        except ValueError:
            pro_bowls = 0
        try:
            av = int(item.contents[13].text)
        except ValueError:
            av = 0
        try:
            games_played = int(item.contents[14].text)
        except ValueError:
            games_played = 0
        try:
            games_started = int(item.contents[15].text)
        except ValueError:
            games_started = 0

        return age, career_length, all_pros, pro_bowls, av, games_played, games_started, prof_url

    elif combine:
        try:
            forty = float(item.contents[9].text)
        except ValueError:
            forty = 0
        try:
            vert = float(item.contents[10].text)
        except ValueError:
            vert = 0
        try:
            bench = int(item.contents[11].text)
        except ValueError:
            bench = 0
        try:
            broad = int(item.contents[12].text)
        except ValueError:
            broad = 0
        try:
            cone = float(item.contents[13].text)
        except ValueError:
            cone = 0
        try:
            shuttle = float(item.contents[14].text)
        except ValueError:
            shuttle = 0

        return forty, vert, bench, broad, cone, shuttle


def calc_pick_value(row, player):
    """
    Helper method that returns this player's pick value as outlined in the Appendix of the report
    :param row:
    :param player:
    :return:
    """
    round = row[1]
    pick = row[2]
    career_length = row[9]
    av = row[10]
    awards_score = player.awards_score

    av_per_year = float(av / career_length) if career_length > 0 else 0

    return av_per_year * float(1 + float(round / 10) + float(pick / 32)) * awards_score


def contains(player, db_name):
    """
    Returns true if the given player was drafted
    :param player
    :param db_name
    :return:
    """
    if db_name != "DraftedPlayers" and db_name != "CombinePlayers" and \
            db_name != "Player_PickVal_Draft_CStats" and \
            db_name != "Player_PickVal_Draft_CStats_QBs" and \
            db_name != "Player_PickVal_Draft_CStats_RUSH_REC" and \
            db_name != "Player_PickVal_Draft_CStats_DEFENSE":
        return False

    conn = sqlite3.connect('PFR.db')
    for row in conn.execute('select * from ' + db_name + ' order by name;'):
        if player.name == row[1] and player.pos == row[2] and \
                player.college == row[3]:
            return True
    return False


def find(player, db_path, table_name, stats_list):
    """
    Returns a PlayerWithStats from the given table_name
    :param player:
    :param db_path:
    :param table_name:
    :param stats_list:
    :return:
    """
    if table_name != "DraftedPlayers" and table_name != "CombinePlayers" and \
            table_name != "Player_PickVal_Draft_CStats" and \
            table_name != "Player_PickVal_Draft_CStats_QBs" and \
            table_name != "Player_PickVal_Draft_CStats_RUSH_REC" and \
            table_name != "Player_PickVal_Draft_CStats_DEFENSE":
        return False

    conn = sqlite3.connect(db_path)
    for row in conn.execute('select * from ' + table_name + ' order by name;'):
        if player.name == row[1] and player.pos == row[2] and \
                player.college == row[3]:
            stats = {}
            for i, stat in enumerate(stats_list):
                stats[stats_list[i]] = row[i + 7]
                i += 1
            return PlayerWithStats(player.name, player.college, player.pos, stats), row[0]
    return None


def main(text_me=False):
    if text_me:
        account_sid = "AC64c6114c6b6f5c379eea708031324626"
        auth_token = "4fc0775e65ee98bc6374ee669dd47fda"
        client = Client(account_sid, auth_token)
        client.messages.create(
            to="+17046852122",
            from_="+18645139496",
            body="Beginning script! I'll text you when I'm finished :)"
        )

        try:
            scraper = PFRScraper()
            # scraper.get_players(DRAFTED_URL)
            # scraper.get_players(COMBINE_PREFIX)
            # scraper.get_college_stats()
            # scraper.get_pick_value()
            # scraper.add_college_percentages(pickle.load(open("CollegePlayerStats.txt", "rb+")))
            first = client.messages.create(
                to="+17046852122",
                from_="+18645139496",
                body="Finished!"
            )

        except (TimeoutException, sqlite3.OperationalError,  RuntimeError, AttributeError, KeyError, TypeError) as e:
            second = client.messages.create(
                to="+17046852122",
                from_="+18645139496",
                body=f"Balls, there was an error...\n{e}"
            )

    else:
        scraper = PFRScraper()
        # scraper.get_players(DRAFTED_URL)
        # scraper.get_players(COMBINE_PREFIX)
        # scraper.get_not_on_drafted_team()
        # scraper.get_college_stats()


if __name__ == "__main__":
    # Execute only if run as a script
    # college_stats = pickle.load(open("CollegePlayerStats.txt", "rb+"))
    # write_college_stats(college_stats)
    scraper = PFRScraper()
    scraper.get_players(DRAFTED_URL)
    # scraper.add_college_percentages(pickle.load(open("CollegePlayerStats.txt", "rb+")))
    # main(text_me=True)
