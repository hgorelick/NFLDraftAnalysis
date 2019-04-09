import sqlite3
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import Normalize
from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

# switch the following imports if needed
# import visuals_jupyter as vs
import visuals as vs


def plot_feature_weight(players, x_train, y_train, num_columns):
    """
    Displays the most import features used in the predictor model
    :param players:
    :param x_train:
    :param y_train:
    :param num_columns:
    :return:
    """
    model = RandomForestClassifier(max_depth=None, random_state=None)
    model = model.fit(x_train, y_train)
    vs.feature_plot(model.feature_importances_, pd.DataFrame(x_train, columns=players.columns[7:num_columns]),
                    pd.DataFrame(y_train), num_columns - 7)


def fit_players(players, num_columns, plot_features=False):
    """
    Fits the given players to a DecisionTreeClassifier model
    :param players:
    :param num_columns:
    :param plot_features:
    :return:
    """
    if 'cmp_percent' in players.columns:
        title = "QBs"

    elif 'tackles_solo' in players.columns:
        title = "Defenders"

    elif 'rush_att' in players.columns:
        title = "Rushers & Receivers (includes QBs)"

    else:
        title = "Returners"

    x_ys = get_test_train_xy(players, num_columns)
    x_train = x_ys[0]
    y_train = x_ys[2]

    x_test = x_ys[1]
    y_test = x_ys[3]

    dec_tree = DecisionTreeClassifier(max_depth=None, random_state=None)

    if plot_features:
        plot_feature_weight(players, x_train, y_train, num_columns)

    return dec_tree.fit(x_test, y_test)


###############################
# Model and training getters  #
###############################
def get_qbs_model(db_path, plot_features=False):
    conn = sqlite3.connect(db_path)
    qbs = pd.read_sql_query("select * from Player_PickVal_Draft_CStats_QBs;", conn)
    return fit_players(qbs, 16, plot_features)


def get_rush_rec_model(db_path, plot_features=False):
    conn = sqlite3.connect(db_path)
    rush_rec = pd.read_sql_query("select * from Player_PickVal_Draft_CStats_RUSH_REC;", conn)
    return fit_players(rush_rec, 15, plot_features)


def get_def_model(db_path, plot_features=False):
    conn = sqlite3.connect(db_path)
    defense = pd.read_sql_query("select * from Player_PickVal_Draft_CStats_DEFENSE;", conn)
    return fit_players(defense, 18, plot_features)


def get_test_train_xy(players, num_columns):
    players_array = players.values
    x = players_array[:, 7:num_columns]
    y = players_array[:, 0]
    y = y.astype('int')
    validation_size = 0.20
    seed = 7
    x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, test_size=validation_size,
                                                                        random_state=seed)

    return x_train, x_test, y_train, y_test
###############################


#######################
# Plotting Functions  #
#######################
def plot_rounds_one_two(db_path, save=False):
    conn = sqlite3.connect(db_path)

    avg_query = "select real_pick, ((sum(difference) * 1.0) / (count(real_pick))) as average " \
                "from PickPredictionAccuracies group by real_pick;"
    avg = pd.read_sql_query(avg_query, conn)

    pos_accuracies_query = "select pos, count(pos) as count from CorrectPredictions group by pos order by count desc;"
    pos_accuracies = pd.read_sql_query(pos_accuracies_query, conn)

    plot_bar_x(avg, 200, "Real Pick", "Average Difference", "Real Pick vs. Average Difference in Predicted Pick", save)
    plot_bar_x(pos_accuracies, 20, "Position", "Correct Predictions", "Number of Correct Predictions by Position", save)


def plot_bar_x(data, vmax, x_label, y_label, title, save=False):
    x_pos = [int(i) for i, _ in enumerate(data.iloc[:, 0])]

    cmap = cm.get_cmap('jet')
    norm = Normalize(vmin=0, vmax=vmax)

    plt.figure(figsize=(20, 12))
    plt.bar(x_pos, data.iloc[:, 1], color=cmap(norm(list(data.iloc[:, 1]))))
    plt.grid(True, linestyle='--', which='major', axis='y', color='grey', alpha=.25)
    plt.xlabel(x_label, fontsize=16)
    plt.ylabel(y_label, fontsize=16)
    plt.title(title, fontsize=24)

    plt.xticks(x_pos, data.iloc[:, 0])
    if save:
        plt.savefig(title + '.png', bbox_inches='tight')
    else:
        plt.show()
#######################
