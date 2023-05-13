import string

import plotly.graph_objects as go
from dash import dcc, html

from ..config import defender_stats, midfielder_stats, forward_stats, goalkeeper_stats


class Radar(html.Div):
    def __init__(self, name, df):
        # min-max normalize all numeric features to make the plot more readable
        to_normalize = list(set(defender_stats + midfielder_stats + forward_stats + goalkeeper_stats))
        df[to_normalize] = df[to_normalize].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

        # for the percentage features fill missing values with 0
        percentage_features = [feature for feature in to_normalize if 'pct' in feature]
        df[percentage_features] = df[percentage_features].fillna(0)

        # save all information needed for the update
        self.html_id = name.lower().replace(" ", "-")
        self.df = df
        self.selected_players = []
        self.colortracker = 1

        # Equivalent to `html.Div([...])`
        super().__init__(
            className="graph_card",
            children=[
                html.H6(name),
                dcc.Graph(id=self.html_id)
            ],
        )

    def update(self, added_player):
        # define the different axes of the radarplot as a combination of all others except for the goal keeper ones
        # as they are missing values for non goal-keepers
        theta = list(set(defender_stats + midfielder_stats + forward_stats))
        theta_layout = [string.capwords(feature.replace('gk_', '').replace('_', ' ')) for feature in theta]

        # generate an empty radarplot of no added_player is provided and there are no selected players, also reset the
        # selected player list, this is done when the position changes and when the app is first created
        if added_player is None:
            self.selected_players = []
            self.fig = go.Figure()
            self.fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                    ),
                    angularaxis=dict(
                        visible=True,
                        tickfont=dict(size=10),
                        rotation=90,
                        direction="clockwise"
                    )
                )
            )
            self.fig.add_trace(go.Scatterpolar(r=[0], theta=[''], fill='toself'))
            return self.fig

        else:
            # make sure there are at most 2 selected players
            if len(self.selected_players) < 2:
                self.selected_players.append(added_player)
            else:
                self.selected_players = [self.selected_players[-1], added_player]

        self.fig = go.Figure()

        # The colortracker makes sure that when a new player is added (as it is always second in the list) that the
        # color of the other player in the plot (that moves from second player to first player) keeps the same color
        # and legend position to avoid confusion

        # always add the first selected player to the radarplot
        rho1 = [float(self.df.loc[self.df['player'] == self.selected_players[0], attribute]) for attribute in theta]
        self.fig.add_trace(go.Scatterpolar(
            r=rho1 + [rho1[-1]],
            theta=theta_layout + [theta_layout[-1]],
            name=self.selected_players[0],
            fill='toself',
            line=dict(color='blue' if (self.colortracker == 1) else 'red')
        ))
        if len(self.selected_players) > 1:
            # if there is a second selected player
            rho2 = [float(self.df.loc[self.df['player'] == self.selected_players[1], attribute]) for attribute in theta]
            self.fig.add_trace(go.Scatterpolar(
                r=rho2 + [rho2[-1]],
                theta=theta_layout + [theta_layout[-1]],
                name=self.selected_players[1],
                fill='toself',
                line=dict(color='red' if (self.colortracker == 1) else 'blue')
            ))

            # update the colortracker
            if self.colortracker == 1:
                self.colortracker = 0
            else:
                self.fig.update_layout(legend_traceorder="reversed")
                self.colortracker = 1

        self.fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True
                ),
            ),
            showlegend=True
        )

        return self.fig
