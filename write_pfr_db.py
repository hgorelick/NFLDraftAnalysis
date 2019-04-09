#!/usr/bin/env python

import _pickle as pickle
from Players.DraftedPlayer import *
from Players.CombinePlayer import *
import sqlite3


def write_drafted_table(players):
    """
    Writes DraftedPlayers to an SQLite3 database
    """
    print("Connecting to SQLite3")
    conn = sqlite3.connect('PFR.db')
    cursor = conn.cursor()
    print("SQLite3 Connected")

    print("Writing DraftedPlayers...")
    cursor.execute('DROP TABLE IF EXISTS DraftedPlayers')
    cursor.execute('''CREATE TABLE IF NOT EXISTS DraftedPlayers (
                      year integer, 
                      round integer, 
                      pick integer, 
                      name text,
                      prof_url text,
                      pos text, 
                      age integer,
                      drafted_by text,
                      college text, 
                      career_length integer, 
                      av integer,
                      games_played integer, 
                      games_started integer,
                      all_pros integer, 
                      pro_bowls integer, 
                      college_stats_link text)''')

    for player in players:
        cursor.execute('''INSERT INTO DraftedPlayers (
                          year,
                          round,
                          pick,
                          name,
                          prof_url,
                          pos,
                          age,
                          drafted_by,
                          college,
                          career_length,
                          av,
                          games_played,
                          games_started,
                          all_pros,
                          pro_bowls,
                          college_stats_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (player.year, player.rnd, player.pick, player.name, player.prof_url, player.pos, player.age,
                        player.drafted_by, player.college, player.career_length, player.av, player.games_played,
                        player.games_started, player.all_pros, player.pro_bowls, player.college_stats_link))
    print("DraftedPlayers complete\n")
    conn.commit()
    conn.close()
    print('Complete!')


def write_combine_table(players):
    """
    Writes CombinePlayers to an SQLite3 database
    """
    print("Connecting to SQLite3")
    conn = sqlite3.connect('PFR.db')
    cursor = conn.cursor()
    print("SQLite3 Connected")
    print("Writing CombinePlayers...")

    cursor.execute('DROP TABLE IF EXISTS CombinePlayers')
    cursor.execute('''CREATE TABLE IF NOT EXISTS CombinePlayers (
                              year integer, 
                              name text,
                              pos text, 
                              college text,
                              college_stats_link text, 
                              height text,
                              weight integer,
                              forty real,
                              vert real,
                              bench integer,
                              broad integer,
                              cone real,
                              shuttle real)''')

    for player in players:
        cursor.execute('''INSERT INTO CombinePlayers (
                                  year,
                                  name,
                                  pos,
                                  college,
                                  college_stats_link,
                                  height,
                                  weight,
                                  forty,
                                  vert,
                                  bench,
                                  broad,
                                  cone,
                                  shuttle) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (player.year, player.name, player.pos, player.college, player.college_stats_link,
                        player.height, player.weight, player.forty, player.vert, player.bench, player.broad,
                        player.cone, player.shuttle))

    print("CombinePlayers complete\n")
    conn.commit()
    conn.close()
    print('Complete!')


def write_player_pick_values(players):
    """
    Writes CombinePlayers to an SQLite3 database
    """
    print("Connecting to SQLite3")
    conn = sqlite3.connect('PFR.db')
    cursor = conn.cursor()
    print("SQLite3 Connected")
    print("Writing NotOnDrafted...")

    cursor.execute('DROP TABLE IF EXISTS PlayersPickValues')
    cursor.execute('''CREATE TABLE IF NOT EXISTS PlayersPickValues (
                      name text,
                      pos text,
                      college text,
                      year integer,
                      round integer,
                      pick integer,
                      award_score real,
                      pick_value real)''')

    for player in players:
        cursor.execute('''INSERT INTO PlayersPickValues (
                          name,
                          pos,
                          college,
                          year,
                          round,
                          pick,
                          award_score,
                          pick_value) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (player.name, player.pos, player.college, player.year, player.round,
                        player.pick, player.awards_score, player.pick_value))
    print("PlayersPickValues complete\n")
    conn.commit()
    conn.close()
    print('Complete!')


def write_college_stats(players):
    """
    :param players:
    :return:
    """
    print("Connecting to SQLite3")
    conn = sqlite3.connect('PFR.db')
    cursor = conn.cursor()
    print("SQLite3 Connected")
    print("Writing CollegeStats...")

    cursor.execute('DROP TABLE IF EXISTS CollegeStats')
    cursor.execute('''CREATE TABLE IF NOT EXISTS CollegeStats (
                                  name text, 
                                  college text,
                                  pos text,
                                  games integer,
                                  pass_cmp integer,
                                  pass_att integer,
                                  pass_yds integer,
                                  cmp_percent real,
                                  yp_cmp real,
                                  pass_td integer,
                                  pass_int integer,
                                  rush_att integer,
                                  rush_yds integer,
                                  yp_rush real,
                                  rush_td integer,
                                  rec integer,
                                  rec_yds integer,
                                  yp_rec real,
                                  rec_td integer,
                                  tackles_solo integer,
                                  tackles_assists integer,
                                  tackles_loss real,
                                  sacks real,
                                  def_int integer,
                                  def_int_yds integer,
                                  def_int_td integer,
                                  pass_defended integer,
                                  fumbles_rec integer,
                                  fumbles_rec_yds integer,
                                  fumbles_rec_td integer,
                                  fumbles_forced integer,
                                  kick_ret integer,
                                  kick_ret_yds integer,
                                  kick_ret_td integer,
                                  punt_ret integer,
                                  punt_ret_yds integer,
                                  punt_ret_td integer)''')
    bad_records = []
    append_b = bad_records.append
    for player in players:
        try:
            cursor.execute('''INSERT INTO CollegeStats (
                                      name, 
                                      college,
                                      pos,
                                      games,
                                      pass_cmp,
                                      pass_att,
                                      pass_yds,
                                      cmp_percent,
                                      yp_cmp,
                                      pass_td,
                                      pass_int,
                                      rush_att,
                                      rush_yds,
                                      yp_rush,
                                      rush_td,
                                      rec,
                                      rec_yds,
                                      yp_rec,
                                      rec_td,
                                      tackles_solo,
                                      tackles_assists,
                                      tackles_loss,
                                      sacks,
                                      def_int,
                                      def_int_yds,
                                      def_int_td,
                                      pass_defended,
                                      fumbles_rec,
                                      fumbles_rec_yds,
                                      fumbles_rec_td,
                                      fumbles_forced,
                                      kick_ret,
                                      kick_ret_yds,
                                      kick_ret_td,
                                      punt_ret,
                                      punt_ret_yds,
                                      punt_ret_td) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                                           ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (player.name, player.college, player.pos, player.stats['games'], player.stats['pass_cmp'],
                            player.stats['pass_att'], player.stats['pass_yds'], player.stats['cmp_percent'],
                            player.stats['yp_cmp'], player.stats['pass_td'], player.stats['pass_int'],
                            player.stats['rush_att'], player.stats['rush_yds'], player.stats['yp_rush'],
                            player.stats['rush_td'], player.stats['rec'], player.stats['rec_yds'],
                            player.stats['yp_rec'], player.stats['rec_td'], player.stats['tackles_solo'],
                            player.stats['tackles_assists'], player.stats['tackles_loss'], player.stats['sacks'],
                            player.stats['def_int'], player.stats['def_int_yds'], player.stats['def_int_td'],
                            player.stats['pass_defended'], player.stats['fumbles_rec'], player.stats['fumbles_rec_yds'],
                            player.stats['fumbles_rec_td'], player.stats['fumbles_forced'], player.stats['kick_ret'],
                            player.stats['kick_ret_yds'], player.stats['kick_ret_td'], player.stats['punt_ret'],
                            player.stats['punt_ret_yds'], player.stats['punt_ret_td']))
        except TypeError:
            append_b((player.name, player.pos, player.college))
            continue

    print("CollegeStats complete\n")
    conn.commit()
    conn.close()

    conn = sqlite3.connect('PFR.db')
    cursor = conn.cursor()
    for record in bad_records:
        delete = f"delete from DraftedPlayers where name = \'{record[0]}\' and " \
            f"pos = \'{record[1]}\' and college = \'{record[2]}\';"
        cursor.execute(delete)
        conn.commit()
    print('Complete!')


if __name__ == "__main__":
    print("Writing data to PFR.db...")
    # DraftedPlayers = pickle.load(open('./DraftedPlayers.txt', 'rb+'))
    # CombinePlayers = pickle.load(open('./CombinePlayers.txt', 'rb+'))
    # NotOnDraftedTeam = pickle.load(open('./NotOnDraftedTeam.txt', 'rb+'))
    # write_drafted_table(DraftedPlayers)
    # write_combine_table(CombinePlayers)
