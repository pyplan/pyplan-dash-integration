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
from utils import default_colors, default_layout, createDashSelectorOptions

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
        dcc.Store(id="discount_selector_status"),
        dcc.Store(id="stock_policy_selector_status"),
        dcc.Store(id="cost_sel_scenario_status"),
        dcc.Store(id="node_status"),
        
        html.Div(
            [
                html.Div(html.Img(
                    src=app.get_asset_url("dash-logo.png"),
                    id="plotly-image",
                    style={
                        "height": "60px",
                        "width": "auto",
                    }), className="three columns"),
                html.H2(
                    "Dash/Pyplan Integration",
                    className="text-center six columns"),
                html.Div(html.Img(
                    src=app.get_asset_url("pyplan-logo.png"),
                    id="pyplan-image",
                    style={
                        "height": "60px",
                        "width": "auto",
                    }), className="three columns text-right"),
            ]),
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Financial Planning"),
                        html.P("Profit and loss statement collect the impact of the previous simulated scenarios across the company and project it results for the following three years. The Net present value of Net Income is the single number that reflects cross impacts."),
                    ], className="twelve columns"),
            ], className="row title"),
        html.Div(
            [
                html.Progress(id='progress', value=0, max=30,
                              style={"width": "100%"}),
                html.Iframe(
                    id="pyplan-ui", src=app.get_asset_url("pyplan-logo.png"), style={"height": "800px"})
            ], className="row"),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    "Discount", className="selector_label first"),
                                dcc.RadioItems(
                                    id="discount_selector",
                                    options=[],
                                    labelStyle={'display': 'inline-block',
                                                'marginRight': '10px'}
                                ),
                            ], className="four columns box"),

                        html.Div(
                            [
                                html.P("Stock Policy",
                                       className="selector_label first"),
                                dcc.RadioItems(
                                    id="stock_policy_selector",
                                    options=[],
                                    labelStyle={'display': 'inline-block',
                                                'marginRight': '10px'}
                                ),
                            ], className="four columns box"),

                        html.Div(
                            [
                                html.P(
                                    "Cost", className="selector_label first"),
                                dcc.RadioItems(
                                    id="cost_sel_scenario",
                                    options=[],
                                    labelStyle={'display': 'inline-block',
                                                'marginRight': '10px'}
                                ),
                            ], className="four columns box")

                    ])


            ], className="row"),
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
    [Output("pyplan-ui", "src"),
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
            pyplan_sessions[session_id] = Pyplan("http://localhost:8000")
            pyplan_sessions[session_id].login(
                "dash_user", "Pyplan.dash.2020", 1)
            pyplan_sessions[session_id].open_model(
                "novix/Public/Test/getting started with planning dash demo.ppl")

        pyplan = pyplan_sessions[session_id]
        if pyplan.is_ready():
            return f"http://localhost:9000/#loginas/{pyplan.token}/{pyplan.session_key}", True, 30, True

    return app.get_asset_url("pyplan-logo.png"), False, n_intervals+1, False




@app.callback(
    [
        Output('discount_selector_status', 'data'),
        Output('stock_policy_selector_status', 'data'),
        Output('cost_sel_scenario_status', 'data'),
        Output('node_status', 'data'),
    ],
    [Input('result-check', 'n_intervals'),
     State('session-id', 'children')]
)
def check_pyplan_status(n_intervals, session_id):
    discount_selector_status = dash.no_update
    stock_policy_selector_status = dash.no_update
    cost_sel_scenario_status = dash.no_update
    node_status = dash.no_update

    if session_id in pyplan_sessions and pyplan_sessions[session_id].is_ready():

        nodes_to_refresh = pyplan_sessions[session_id].getStatus(
            ['discount_selector', 'stock_policy_selector', 'cost_sel_scenario', 'p_l_report'])
        if 'discount_selector' in nodes_to_refresh:
            discount_selector_status = True
        if 'stock_policy_selector' in nodes_to_refresh:
            stock_policy_selector_status = True
        if 'cost_sel_scenario' in nodes_to_refresh:
            cost_sel_scenario_status = True
        if 'p_l_report' in nodes_to_refresh:
            node_status = True

    return discount_selector_status, stock_policy_selector_status, cost_sel_scenario_status, node_status


@app.callback(
    [Output('discount_selector', 'options'),
     Output("discount_selector", "value")],
    [Input('discount_selector_status', 'data'),
     State('session-id', 'children')]
)
def update_discount_selector(status_data, session_id):
    if session_id in pyplan_sessions and pyplan_sessions[session_id].is_ready():
        option_list = pyplan_sessions[session_id].getResult(
            'discount_scenarios')
        option_selected = pyplan_sessions[session_id].getResult(
            'discount_selector')
        return createDashSelectorOptions(option_list), option_list.index(option_selected)
    return dash.no_update, dash.no_update


@app.callback(
    [Output('stock_policy_selector', 'options'),
     Output("stock_policy_selector", "value")],
    [Input('stock_policy_selector_status', 'data'),
     State('session-id', 'children')]
)
def update_discount_selector(status_data, session_id):
    if session_id in pyplan_sessions and pyplan_sessions[session_id].is_ready():
        option_list = pyplan_sessions[session_id].getResult(
            'stock_scenarios')
        option_selected = pyplan_sessions[session_id].getResult(
            'stock_policy_selector')
        return createDashSelectorOptions(option_list), option_list.index(option_selected)
    return dash.no_update, dash.no_update



@app.callback(
    [Output('cost_sel_scenario', 'options'),
     Output("cost_sel_scenario", "value")],
    [Input('cost_sel_scenario_status', 'data'),
     State('session-id', 'children')]
)
def update_discount_selector(status_data, session_id):
    if session_id in pyplan_sessions and pyplan_sessions[session_id].is_ready():
        option_list = pyplan_sessions[session_id].getResult(
            'cost_scenarios')
        option_selected = pyplan_sessions[session_id].getResult(
            'cost_sel_scenario')
        return createDashSelectorOptions(option_list), option_list.index(option_selected)
    return dash.no_update, dash.no_update    



@app.callback(
    [Output(None)],
    [Input('discount_selector', 'value'),
     State('session-id', 'children')]
    #  Input(component_id='discount_selector', component_property='value'),
    #  Input(component_id='stock_policy_selector', component_property='value'),
    #  Input(component_id='cost_sel_scenario', component_property='value')
    #  ]
)
def selects_callback(selector_value, session_id):
    if session_id in pyplan_sessions and pyplan_sessions[session_id].is_ready():
        pyplan_sessions[session_id].setSelectorValue("discount_selector", selector_value)
        # pyplan.setSelectorValue("discount_selector", discount_value)
        # pyplan.setSelectorValue("stock_policy_selector", stock_value)
        # pyplan.setSelectorValue("cost_sel_scenario", cost_value)



















@app.callback(
    [Output('pl_table', 'columns'), Output(
        "pl_table", "data"), Output("pl_chart", "figure")],
    [Input('node_status', 'data'),
     State('session-id', 'children'),
     ]
    #  Input(component_id='discount_selector', component_property='value'),
    #  Input(component_id='stock_policy_selector', component_property='value'),
    #  Input(component_id='cost_sel_scenario', component_property='value')
    #  ]
)
def selects_callback(node_status, session_id):

    if session_id in pyplan_sessions and pyplan_sessions[session_id].is_ready():

        # get values from Pyplan
        pyplan = pyplan_sessions[session_id]
        df_json = pyplan.getResult('p_l_report')
        df = pd.read_json(df_json, orient='table')
        sorted_values = df.index.get_level_values("Report index").unique().tolist()
        df = pd.pivot_table( df, values="value", index=["Report index"], columns=["time"], aggfunc="sum")
        #fix index order after pivot
        df = df.reindex(index=sorted_values).reset_index()

        # create columns for table
        columns = []
        for nn, col in enumerate(df.columns):
            column_definition = {
                "name": col,
                "id": col,
                "type": "text"
            }
            if nn > 0:
                column_definition["type"] = "numeric"
                column_definition["format"] = FormatTemplate.money(0)

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
