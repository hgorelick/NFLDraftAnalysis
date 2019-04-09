import sqlite3
from Players import *
from pfr_scraper import *
from PFRDataAnalysis.Processor import *

# constants
rush_rec = ("QB", "RB", "WR", "TE")
defense = ("CB", "DB", "DE", "DL", "DT", "ILB", "LB", "NT", "OLB", "S")

table_names = {"QB": "Player_PickVal_Draft_CStats_QBs", rush_rec: "Player_PickVal_Draft_CStats_RUSH_REC",
               defense: "Player_PickVal_Draft_CStats_DEFENSE"}

qb_stats = ['pass_cmp', 'pass_att', 'pass_yds', 'cmp_percent', 'yp_cmp', 'pass_td',
            'pass_int', 'rush_att', 'rush_yds']

rush_rec_stats = ['rush_att', 'rush_yds', 'yp_rush', 'rush_td', 'rec', 'rec_yds', 'yp_rec', 'rec_td']

defense_stats = ['tackles_solo', 'tackles_assists', 'tackles_loss', 'sacks', 'def_int', 'def_int_yds',
                 'def_int_td', 'pass_defended', 'fumbles_rec', 'fumbles_rec_yds', 'fumbles_forced']


def predict_player_pick(db_path, player, plot_features):
    """
    Uses the given player's collegiate stats to predict his draft position
    :param db_path:
    :param player:
    :param plot_features:
    :return:
    """
    model = None
    stats_list = []
    table = ""
    if player.pos == "QB":
        model = get_qbs_model(db_path, plot_features)
        stats_list = qb_stats
        table = table_names["QB"]

    elif player.pos in rush_rec:
        model = get_rush_rec_model(db_path, plot_features)
        stats_list = rush_rec_stats
        table = table_names[rush_rec]

    elif player.pos in defense:
        model = get_def_model(db_path, plot_features)
        stats_list = defense_stats
        table = table_names[defense]

    player_to_predict_info = find(player, db_path, table, stats_list)
    player_to_predict = player_to_predict_info[0]
    pick = player_to_predict_info[1]

    if player_to_predict is None:
        return None

    return int(model.predict([list(player_to_predict.stats.values())], pick)), pick


def create_prediction_accuracies_round_one_two(db_path):
    """
    Creates the prediction accuracy tables
    :param db_path:
    :return:
    """
    models = {get_qbs_model(db_path, False): (table_names["QB"], qb_stats),
              get_rush_rec_model(db_path, False): (table_names[rush_rec], rush_rec_stats),
              get_def_model(db_path, False): (table_names[defense], defense_stats)}

    predictions = {}
    update = predictions.update

    conn = sqlite3.connect(db_path)
    for model in models.keys():
        table = models[model][0]
        stats_list = models[model][1]
        query = f"select * from {table} where round = 1 or round = 2"

        df = pd.read_sql_query(query, conn)
        for row in df.itertuples():
            player = Player(row.name, row.pos, row.college)
            player_to_predict_info = find(player, db_path, table, stats_list)
            player_to_predict = player_to_predict_info[0]
            pick = player_to_predict_info[1]

            if player_to_predict is None:
                continue

            prediction = int(model.predict([list(player_to_predict.stats.values())], pick)), pick

            if player.name not in predictions.keys():
                predictions[player.name] = (prediction[1], prediction[0], abs(prediction[1] - prediction[0]))

    df = pd.DataFrame(predictions, index=['real_pick', 'predicted_pick', 'difference']).T
    df.to_sql("PickPredictionAccuracies", conn, index=False, if_exists=True)

    correct_predictions_query = \
        "create view CorrectPredictions as" \
        "select DraftedPlayers.year, DraftedPlayers.round, DraftedPlayers.pick, predicted_pick, " \
        "PickPredictionAccuracies.name, DraftedPlayers.pos, drafted_by, DraftedPlayers.college, pick_value from " \
        "PickPredictionAccuracies left join DraftedPlayers on PickPredictionAccuracies.name = DraftedPlayers.name " \
        "left join PlayersPickValues on PlayersPickValues.name = PickPredictionAccuracies.name " \
        "where difference = (select min(difference) from PickPredictionAccuracies group by real_pick) " \
        "order by DraftedPlayers.pick;"
    conn.execute(correct_predictions_query)
    conn.commit()


if __name__ == "__main__":
    plot_rounds_one_two(r'C:\NFLDraftAnalysis\PFR.db', True)
    # player = Player("Adrian Peterson", "RB", "Oklahoma")
    # prediction = predict_player_pick(r'C:\NFLDraftAnalysis\PFR.db', player, True)
    # print(f"{player.name}:\n"
    #       f"Actual Pick:  {prediction[1]}\n"
    #       f"Predicted Pick: {prediction[0]}")
