import string

import plotly.graph_objects as go
from dash import dcc, html

from ..config import defender_stats, midfielder_stats, forward_stats, goalkeeper_stats


class Radar(html.Div):
    def __init__(self, name, df):
        to_normalize = list(set(defender_stats + midfielder_stats + forward_stats + goalkeeper_stats))
        df[to_normalize] = df[to_normalize].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

        percentage_features = [feature for feature in to_normalize if 'pct' in feature]
        df[percentage_features] = df[percentage_features].fillna(0)

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
        theta = list(set(defender_stats + midfielder_stats + forward_stats))
        theta_layout = [string.capwords(feature.replace('gk_', '').replace('_', ' ')) for feature in theta]

        if (added_player is None) and len(self.selected_players) == 0:
            self.fig = go.Figure()
            self.fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
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
        elif (added_player is None):
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
            if len(self.selected_players) < 2:
                self.selected_players.append(added_player)
            else:
                self.selected_players = [self.selected_players[-1], added_player]

        self.fig = go.Figure()

        rho1 = [float(self.df.loc[self.df['player'] == self.selected_players[0], attribute]) for attribute in theta]
        self.fig.add_trace(go.Scatterpolar(
            r=rho1 + [rho1[-1]],
            theta=theta_layout + [theta_layout[-1]],
            name=self.selected_players[0],
            fill='toself',
            line=dict(color='blue' if (self.colortracker == 1) else 'red')
        ))
        if len(self.selected_players) > 1:
            rho2 = [float(self.df.loc[self.df['player'] == self.selected_players[1], attribute]) for attribute in theta]
            self.fig.add_trace(go.Scatterpolar(
                r=rho2 + [rho2[-1]],
                theta=theta_layout + [theta_layout[-1]],
                name=self.selected_players[1],
                fill='toself',
                line=dict(color='red' if (self.colortracker == 1) else 'blue')
            ))

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
