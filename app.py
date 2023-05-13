from dash import html, dash, dcc
from dash.dependencies import Input, Output, State

from jbi100_app.data import get_data
from jbi100_app.main import app
from jbi100_app.views.barchart import Barchart
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.radarplot import Radar
from jbi100_app.views.scatterplot import Scatterplot

if __name__ == '__main__':
    # load the data
    data = get_data()

    # Initialize the plots using their created classes
    barchart1 = Barchart("Choose players", 'player', data)
    radarplot = Radar("Compare two chosen players", data)
    gcaplot = Scatterplot("GCA plot", 'gca_per90', 'sca_per90', data)

    # New layout
    app.layout = html.Div(
        id="app-container",
        children=[
            # Make the setup of the app
            # Left column
            html.Div(
                id="left-column",
                className="two columns",
                children=make_menu_layout()
            ),

            # Right column with all plots
            html.Div(
                id='plots-section',
                className="ten columns",
                children=[
                    # Top wor with barplot and scatterplot
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
                    # Bottom row with radarplot
                    html.Div(
                        id='bottom-row',
                        className="row",
                        children=[
                            radarplot
                        ]
                    )
                ]
            ),
            # States needed for the interaction to run more smoothly
            html.Div([
                dcc.Store(id='previous_position', data=None),
                dcc.Store(id='previous_bar', data=None),
                dcc.Store(id='previous_click', data=None)
            ], style={'display': 'none'})
        ],
    )


    # Define interaction
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
    def update_plot(selected_position, selected_bar, gca_click_player, prev_position,
                   prev_bar, prev_click_player):
        """This callback updates all plots simultaniously based on a change in the selected players or a
        change in the filtered position. The change in selected players can come from the barplot or the gca plot"""
        # depending on what input changes the plots are updated
        if selected_position != prev_position:
            # if the selected position changes reset all plots and filter the players on the selected position
            new_plot_bar = barchart1.update(selected_position, None)
            new_plot_gca = gcaplot.update(selected_position, None)
            new_plot_radar = radarplot.update(None)
        elif selected_bar != prev_bar:
            # if you click on a player in the barplot update all plots to include that player
            new_plot_bar = barchart1.update(selected_position, selected_bar['points'][0]['label'])
            new_plot_gca = gcaplot.update(selected_position, selected_bar['points'][0]['label'])
            new_plot_radar = radarplot.update(selected_bar['points'][0]['label'])
        elif gca_click_player != prev_click_player:
            # if you click on a player in the gcaplot update all plots to include that player
            new_plot_bar = barchart1.update(selected_position, gca_click_player['points'][0]['hovertext'])
            new_plot_gca = gcaplot.update(selected_position, gca_click_player['points'][0]['hovertext'])
            new_plot_radar = radarplot.update(gca_click_player['points'][0]['hovertext'])
        else:
            # this is for the first initialization of the dashboard and will generate empty plots and no position filter
            new_plot_bar = barchart1.update(selected_position, None)
            new_plot_gca = gcaplot.update(selected_position, None)
            new_plot_radar = radarplot.update(None)

        # make sure we update the sates
        prev_position = selected_position
        prev_bar = selected_bar
        prev_click_player = gca_click_player

        # return all outputs
        return new_plot_bar, new_plot_gca, new_plot_radar, prev_position, prev_bar, prev_click_player

app.run_server(debug=False, dev_tools_ui=True)
