from dash import html, dash, dcc
from dash.dependencies import Input, Output, State

from jbi100_app.data import get_data
from jbi100_app.main import app
from jbi100_app.views.barchart import Barchart
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.radarplot import Radar
from jbi100_app.views.scatterplot import Scatterplot

if __name__ == '__main__':
    data = get_data()

    barchart1 = Barchart("Choose players", 'player', data)

    radarplot = Radar("Compare two chosen players", data)

    gcaplot = Scatterplot("GCA plot", 'gca_per90', 'sca_per90', data)

    # New layout
    app.layout = html.Div(
        id="app-container",
        children=[
            # States

            # Left column
            html.Div(
                id="left-column",
                className="two columns",
                children=make_menu_layout()
            ),

            # plots
            html.Div(
                id='plots-section',
                className="ten columns",
                children=[
                    html.Div(
                        id="top-row",
                        className="row",
                        children=[
                            html.Div(
                                id='top-row-first-plot',
                                className='seven columns',
                                children=[barchart1]
                            ),
                            html.Div(
                                id='top-row-second-plot',
                                className='five columns',
                                children=[gcaplot]
                            )
                        ]),
                    html.Div(
                        id='bottom-row',
                        className="row",
                        children=[
                            radarplot
                        ]
                    )
                ]
            ),

            html.Div([
                dcc.Store(id='previous_position', data=None),
                dcc.Store(id='previous_bar', data=None),
                dcc.Store(id='previous_click', data=None)
            ], style={'display': 'none'})
        ],
    )


    # Define interactions
    @app.callback(
        [Output(barchart1.html_id, "figure"),
         Output(gcaplot.html_id, "figure"),
         Output(radarplot.html_id, "figure"),
         Output('previous_position', 'value'),
         Output('previous_bar', 'clickData'),
         Output('previous_click', 'clickData')],
        [Input("select-position", "value"),
         Input(barchart1.html_id, 'clickData'),
         Input(gcaplot.html_id, 'clickData')],
        [State('previous_position', 'value'),
         State('previous_bar', 'clickData'),
         State('previous_click', 'clickData')]
    )
    def update_gca(selected_position, selected_bar, gca_click_player, prev_position,
                   prev_bar, prev_click_player):
        if selected_position != prev_position:
            new_plot_bar = barchart1.update(selected_position, None)
            new_plot_gca = gcaplot.update(selected_position, None)
            new_plot_radar = radarplot.update(None)
        elif selected_bar != prev_bar:
            new_plot_bar = barchart1.update(selected_position, selected_bar['points'][0]['label'])
            new_plot_gca = gcaplot.update(selected_position, selected_bar['points'][0]['label'])
            new_plot_radar = radarplot.update(selected_bar['points'][0]['label'])
        elif gca_click_player != prev_click_player:
            new_plot_bar = barchart1.update(selected_position, gca_click_player['points'][0]['hovertext'])
            new_plot_gca = gcaplot.update(selected_position, gca_click_player['points'][0]['hovertext'])
            new_plot_radar = radarplot.update(gca_click_player['points'][0]['hovertext'])
        else:
            new_plot_bar = barchart1.update(selected_position, None)
            new_plot_gca = gcaplot.update(selected_position, None)
            new_plot_radar = radarplot.update(None)

        prev_position = selected_position
        prev_bar = selected_bar
        prev_click_player = gca_click_player

        return new_plot_bar, new_plot_gca, new_plot_radar, prev_position, prev_bar, prev_click_player

app.run_server(debug=False, dev_tools_ui=True)
