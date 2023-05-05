import string

import plotly.graph_objects as go
from dash import dcc, html

from ..config import goalkeeper_stats, defender_stats, midfielder_stats, forward_stats


class Barchart(html.Div):
    def __init__(self, name, feature_y, df):
        positions_to_features = {
            'goalkeeper': goalkeeper_stats,
            'defender': defender_stats,
            'midfielder': midfielder_stats,
            'forward': forward_stats
        }

        positions_to_encoded_positions = {
            'goalkeeper': ['GK'],
            'defender': ['DF', 'FB', 'LB', 'RB', 'CB'],
            'midfielder': ['MF', 'DM', 'CM', 'LM', 'RM', 'WM', 'AM'],
            'forward': ['FW', 'LW', 'RW']
        }

        dfs = {}

        for key, value in positions_to_features.items():
            position = df[['player', 'position'] + value]
            position = position[position['position'].isin(positions_to_encoded_positions[key])]
            position[value] = position[value].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
            position['sum'] = position[value].sum(axis=1)
            if key == 'goalkeeper':
                position['sum'] -= 2 * position['gk_goals_against_per90']
            position = position.sort_values(by='sum', ascending=False)
            dfs[key] = position

        self.html_id = name.lower().replace(" ", "-")
        self.gk_df = dfs['goalkeeper']
        self.def_df = dfs['defender']
        self.mid_df = dfs['midfielder']
        self.for_df = dfs['forward']
        self.feature_y = feature_y
        self.selected_players = []

        # Equivalent to `html.Div([...])`
        super().__init__(
            className="graph_card",
            children=[
                html.H6(name),
                dcc.Graph(id=self.html_id)
            ],
        )

    def update(self, selected_position, added_player):
        if selected_position is None:
            return go.Figure(
                layout=go.Layout(
                    yaxis={'title': 'Player'},
                    width=700,
                    height=550
                )
            )

        positions_to_df = {
            'goalkeeper': self.gk_df,
            'defender': self.def_df,
            'midfielder': self.mid_df,
            'forward': self.for_df
        }

        positions_to_features = {
            'goalkeeper': goalkeeper_stats,
            'defender': defender_stats,
            'midfielder': midfielder_stats,
            'forward': forward_stats
        }

        df = positions_to_df[selected_position].reset_index(drop=True)
        features = positions_to_features[selected_position]

        x_values = df[features]
        y_values = df[self.feature_y]
        self.fig = go.Figure(data=[
            go.Bar(x=x_values[feature][:10],
                   y=y_values[:10],
                   orientation='h',
                   name=string.capwords(feature.replace('gk_', '').replace('_', ' ')))
            for feature in features
        ])

        self.fig.update_layout(width=700, height=550, barmode='stack', clickmode='event+select', yaxis_title="Players")
        self.fig.update_xaxes(showticklabels=False)

        if added_player is None:
            selected_index = df.index[:10]
            self.selected_players = []
        else:
            if len(self.selected_players) < 2:
                self.selected_players.append(added_player)
            else:
                self.selected_players = [self.selected_players[-1], added_player]
            selected_index = df[df['player'].isin(self.selected_players)].index

        for i in range(5):
            self.fig.data[i].selectedpoints = selected_index

        return self.fig
