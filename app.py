import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_table.FormatTemplate as FormatTemplate
import plotly.express as px
import pandas as pd
import os
import uuid
from pyplan import Pyplan
from utils import default_colors, default_layout

dash.Dash()
app = dash.Dash(__name__, meta_tags=[
                {"name": "viewport", "content": "width=device-width", "title": "Dash/Pyplan Integration"}])

server = app.server
pyplan_sessions = dict()


def serve_layout():
    session_id = str(uuid.uuid4())

    return html.Div([

        html.Div(session_id, id='session-id', style={'display': 'none'}),
        dcc.Interval(
            id='status-check',
            interval=2000,
            n_intervals=0
        ),
        dcc.Interval(
            id='result-check',
            interval=4000,
            n_intervals=0
        ),
        dcc.Store(id="node_status"),
        html.Div(
            [
                html.Div(
                    html.A(
                        html.Img(
                        src=app.get_asset_url("pyplan-logo.png"),
                        id="pyplan-image",
                        style={
                            "height": "60px",
                            "width": "auto",
                        }), href='https://www.pyplan.org', target='_blank')
                    
                    , className="threet columns"),
                html.H2(
                    "Pyplan/Dash Integration",
                    className="text-center six columns"),
                html.Div(
                    html.A(
                        html.Img(
                        src=app.get_asset_url("dash-logo.png"),
                        id="plotly-image",
                        style={
                            "height": "60px",
                            "width": "auto",
                        }), href='https://plotly.com/dash/', target='_blank')
                    , className="threet columns text-right"),
            ]),
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Integrated Business Planning"),
                        html.H5("Overview:"),
                        html.P("This app is a Commercial, Operations and Financial Planning demo showcasing the integration of Pyplan with Dash. Select any scenario and check the results on the projected P&L Statement."),
                        html.P("Pyplan allows you to explore the underlaying model logic by single clicking a node in the diagram and selecting the <Code> tab to inspect the Python code running underneath."),
                        html.P("You can also analyse its outputs as table and graph by double clicking a node to display its result.")
                          
                    ], className="twelve columns"),
            ], className="row title"),
        html.Div(
            [
                html.Progress(id='progress', value='0', max=30,
                              style={"width": "100%"}),
                
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("wait_for_session.png"),
                            style={
                                "width": "100%",
                                "height": "auto",
                            })
                    ], id='pyplan-container', style={'height':'800px'})

            ], className="row"),

        html.H6('Profit and Loss Statement:'),

        html.Div(
            [
                dcc.Loading(
                    id="loading_charts",
                    type="default",
                    children=html.Div(
                        [
                            dash_table.DataTable(
                                id='pl_table',
                                fixed_rows={
                                    "headers": True, "data": 0},
                                fixed_columns={
                                    "headers": True, "data": 1},
                                style_table={
                                    'width': '100%',
                                },
                                style_as_list_view=True,
                                column_selectable=False,
                                style_cell={'padding': '5px', 'fontSize': '11px',
                                            'fontFamily': 'Open Sans", HelveticaNeue, "Helvetica Neue", Helvetica, Arial, sans-serif'},
                                style_header={
                                    'backgroundColor': '#f2f2f2',
                                    'fontWeight': 'bold'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {
                                            'filter_query': '{Report index} eq "Revenue" or {Report index} eq "Operation Margin" or {Report index} eq "EBITDA" or {Report index} eq "Net Income" or {Report index} eq "EBIT" or {Report index} eq "Profit b/tax"',
                                        },
                                        'backgroundColor': '#f6f6f6',
                                        'fontWeight': 'bold',
                                    },
                                    {
                                        'if': {'column_id': 'Report index'},
                                        'backgroundColor': '#f2f2f2',
                                        'textAlign': 'left'
                                    },
                                ],
                                data=[],
                            ),
                            dcc.Graph(
                                id="pl_chart",
                                figure={
                                    'data': [],
                                    'layout': {
                                        'height': 390
                                    }
                                }
                            )
                        ])
                )

            ], className="row box"),
    ], className="container")


app.layout = serve_layout


@app.callback(
    [Output("pyplan-container","children"),
     Output("status-check", "disabled"),
     Output("progress", "value"),
     Output("progress", "hidden"),
     ],
    [Input(component_id='status-check', component_property='n_intervals'),
     State('session-id', 'children')]
)
def update_pyplan_status(n_intervals, session_id):
    if n_intervals > 0:
        if not session_id in pyplan_sessions:
            pyplan_sessions[session_id] = Pyplan("https://api.pyplan.org")
            pyplan_sessions[session_id].login(
                "dash_user", "Afd.!4dFssw", 23)
            pyplan_sessions[session_id].open_model(
                "dash_integration/Public/getting started with planning dash demo.ppl")

        pyplan = pyplan_sessions[session_id]
        if pyplan.is_ready():
            return html.Iframe(id="pyplan-ui", src=f"https://my.pyplan.org/#loginas/{pyplan.token}/{pyplan.session_key}", style={"height":"800px"}), True, '30', True

    return dash.no_update, False, f'{n_intervals+1}', False



@app.callback(
    [Output('node_status', 'data')],
    [Input('result-check', 'n_intervals'),
     State('session-id', 'children')]
)
def check_pyplan_status(n_intervals, session_id):
    if session_id in pyplan_sessions and pyplan_sessions[session_id].is_ready():
        nodes_to_refresh = pyplan_sessions[session_id].getStatus(['p_l_report_for_dash'])
        return [True if 'p_l_report_for_dash' in nodes_to_refresh else dash.no_update]
    return [dash.no_update]



@app.callback(
    [Output('pl_table', 'columns'), Output(
        "pl_table", "data"), Output("pl_chart", "figure")],
    [Input('node_status', 'data'),
     State('session-id', 'children'),
     ]
)
def selects_callback(node_status, session_id):

    if session_id in pyplan_sessions and pyplan_sessions[session_id].is_ready():
        pyplan = pyplan_sessions[session_id]

        # get values from Pyplan
        df_json = pyplan.getResult('p_l_report_for_dash')
        df = pd.read_json(df_json, orient='table')
        sorted_values = df.index.get_level_values("Report index").unique().tolist()
        df = pd.pivot_table( df, values="value", index=["Report index"], columns=["time"], aggfunc="sum")
        #fix index order after pivot
        df = df.reindex(index=sorted_values).reset_index()

        # create columns for table
        columns = []
        for nn, col in enumerate(df.columns):
            column_definition = None
            if nn==0:
                column_definition = {
                    "name": 'P&L Accounts',
                    "id": 'Report index',
                    "type": "text"
                }
            else:
                column_definition = {
                    "name": col,
                    "id": col,
                    "type": "numeric",
                    "format": FormatTemplate.money(0)
                }
            columns.append(column_definition)

        data = df.to_dict("records")

        value_columns = [cc for nn, cc in enumerate(df.columns) if nn > 0]
        df_chart = df.melt(id_vars=["Report index"],
                           value_vars=value_columns, var_name='time')

        # create chart
        fig = px.line(df_chart, x="time", y="value",
                        color='Report index', color_discrete_sequence=default_colors)

        default_layout(fig)
        fig.update_layout(height=390, xaxis_type="category",
                          title_text=f"P&L Report")

        return columns, data, fig
    return dash.no_update, dash.no_update, dash.no_update


# Main
if __name__ == "__main__":
    app.run_server(debug=True)
