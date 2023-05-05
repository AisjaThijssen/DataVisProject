import plotly.graph_objects as go
from dash import dcc, html


class Scatterplot(html.Div):
    def __init__(self, name, feature_x, feature_y, df):
        self.html_id = name.lower().replace(" ", "-")
        self.feature_x = feature_x
        self.feature_y = feature_y
        self.selected_players = []

        positions_to_encoded_positions = {
            'goalkeeper': ['GK'],
            'defender': ['DF', 'FB', 'LB', 'RB', 'CB'],
            'midfielder': ['MF', 'DM', 'CM', 'LM', 'RM', 'WM', 'AM'],
            'forward': ['FW', 'LW', 'RW']
        }

        dfs = {}
        for key, value in positions_to_encoded_positions.items():
            position = df
            position = position[position['position'].isin(positions_to_encoded_positions[key])]
            dfs[key] = position

        self.gk_df = dfs['goalkeeper']
        self.def_df = dfs['defender']
        self.mid_df = dfs['midfielder']
        self.for_df = dfs['forward']

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
                    yaxis={'title': 'SCA per 90 minutes played'},
                    xaxis={'title': 'GCA per 90 minutes played'},
                    width=500,
                    height=550
                )
            )

        self.fig = go.Figure()

        positions_to_df = {
            'goalkeeper': self.gk_df,
            'defender': self.def_df,
            'midfielder': self.mid_df,
            'forward': self.for_df
        }

        df = positions_to_df[selected_position].reset_index(drop=True)

        x_values = df[self.feature_x]
        y_values = df[self.feature_y]
        self.fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='markers',
            hovertext=df['player'],
        ))
        self.fig.update_traces(mode='markers', marker_size=10)
        self.fig.update_layout(
            yaxis_zeroline=False,
            xaxis_zeroline=False,
        )
        self.fig.update_xaxes(fixedrange=True)
        self.fig.update_yaxes(fixedrange=True)

        if added_player is None:
            selected_index = df.index
            self.selected_players = []
        else:
            if len(self.selected_players) < 2:
                self.selected_players.append(added_player)
            else:
                self.selected_players = [self.selected_players[-1], added_player]
            selected_index = df[df['player'].isin(self.selected_players)].index

        self.fig.data[0].update(
            selectedpoints=selected_index,

            # color of selected points
            selected=dict(marker=dict(color='red')),

            # color of unselected pts
            unselected=dict(marker=dict(color='rgb(200,200,200)', opacity=0.9))
        )

        # update axis titles
        self.fig.update_layout(
            yaxis_title='SCA per 90 minutes played',
            xaxis_title='GCA per 90 minutes played'
        )

        self.fig.update_layout(clickmode='event+select')

        return self.fig
