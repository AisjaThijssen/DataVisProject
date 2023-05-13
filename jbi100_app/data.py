import pandas as pd
import plotly.express as px


def get_data():
    # Read all data
    general_stats = pd.read_csv("jbi100_app/data/player_stats.csv")[['player', 'position', 'goals_per90', 'assists_per90', 'games']]
    keeper_stats = pd.read_csv("jbi100_app/data/player_keepers.csv")[['player', 'gk_goals_against_per90', 'gk_save_pct', 'gk_clean_sheets_pct', 'gk_pens_save_pct']]
    adv_keeper_stats = pd.read_csv("jbi100_app/data/player_keepersadv.csv")[['player', 'gk_avg_distance_def_actions']]
    shots_stats = pd.read_csv("jbi100_app/data/player_shooting.csv")[['player', 'shots_on_target_pct']]
    pass_stats = pd.read_csv("jbi100_app/data/player_passing.csv")[['player', 'passes_pct']]
    gca_stats = pd.read_csv("jbi100_app/data/player_gca.csv")[['player', 'gca_per90', 'sca_per90']]
    defence_stats = pd.read_csv("jbi100_app/data/player_defense.csv")[['player', 'tackles_won', 'tackles', 'dribble_tackles_pct', 'blocks', 'interceptions', 'clearances', 'minutes_90s']]
    possession_stats = pd.read_csv("jbi100_app/data/player_possession.csv")[['player', 'dribbles_completed_pct', 'passes_received']]

    # Merge the different datasets into one big one based on player name
    datasets = [general_stats, keeper_stats, adv_keeper_stats, shots_stats, pass_stats, gca_stats, defence_stats, possession_stats]
    datasets = [dataset.set_index('player') for dataset in datasets]
    full_dataset = datasets[0].join(datasets[1:])

    # calculate the statistics not already in the dataset
    for stat in ['blocks', 'interceptions', 'clearances', 'passes_received']:
        full_dataset[f'{stat}_per90'] = full_dataset[stat]/full_dataset['minutes_90s']

    full_dataset['tackles_won_pct'] = full_dataset['tackles_won']/full_dataset['tackles']

    # only include players that played at least two games
    return full_dataset[full_dataset['games']>2].reset_index()
