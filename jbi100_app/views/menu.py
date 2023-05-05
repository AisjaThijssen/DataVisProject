from dash import dcc, html


def generate_description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("QuickMove for Scouts"),
            html.Div(
                id="intro",
                children="This tool can be used to compare soccer players on their performance in the 2022 world cup",
            ),
        ],
    )


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Label("Position to analyse"),
            dcc.Dropdown(
                id="select-position",
                options=[{"label": i, "value": i} for i in ['goalkeeper', 'defender', 'midfielder', 'forward', None]],
                value=None,
            ),
        ], style={"textAlign": "float-left"}
    )


def make_menu_layout():
    return [generate_description_card(), generate_control_card()]
