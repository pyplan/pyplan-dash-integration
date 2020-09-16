import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_table.FormatTemplate as FormatTemplate
import plotly.express as px
import pathlib
import os
from pyplan import Pyplan


# get relative data folder

dash.Dash()
app = dash.Dash(__name__, meta_tags=[
                {"name": "viewport", "content": "width=device-width", "title": "Dash/Pyplan Integration"}])

server = app.server
# pyplan api class
pyplan = None


app.clientside_callback
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
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
            html.Button('Connect to Pyplan', id="connect_to_pyplan", n_clicks=0),

            dcc.Loading(
                id="loading_pyplan",
                type="default",
                children=html.Div(
                    [
                        html.Iframe(src=app.get_asset_url("pyplan-logo.png"))
                    ])

        ], className="row view-source-code"),
    html.Div(
        [
            # html.Div(
            #     [
            #         html.Div(
            #             [

            #                 html.P("Time", className="selector_label first"),
            #                 dcc.RangeSlider(
            #                     id="time_selector",
            #                     min=0,
            #                     max=len(pyplan.getResult(
            #                         "time_selector").options)-1,
            #                     value=pyplan.getResult(
            #                         "time_selector").selected,
            #                     marks=createRangeSliderMarks(
            #                         pyplan, "time_selector"),  # Helper for create marks
            #                     className="dcc_control",
            #                 ),
            #             ], className="box"),

            #         html.Div(
            #             [
            #                 html.H5("Scenario options"),
            #                 html.P("Discount", className="selector_label"),
            #                 dcc.RadioItems(
            #                     id="discount_selector",
            #                     options=createDashSelectorOptions(
            #                         pyplan, "discount_selector"),  # Helper for create options
            #                     value=pyplan.getResult(
            #                         "discount_selector").selected,
            #                     labelStyle={'display': 'inline-block',
            #                                 'marginRight': '10px'}
            #                 ),
            #                 html.P("Stock Policy", className="selector_label"),
            #                 dcc.RadioItems(
            #                     id="stock_policy_selector",
            #                     options=createDashSelectorOptions(
            #                         pyplan, "stock_policy_selector"),  # Helper for create options
            #                     value=pyplan.getResult(
            #                         "stock_policy_selector").selected,
            #                     labelStyle={'display': 'inline-block',
            #                                 'marginRight': '10px'}
            #                 ),
            #                 html.P("Cost", className="selector_label"),
            #                 dcc.RadioItems(
            #                     id="cost_sel_scenario",
            #                     options=createDashSelectorOptions(
            #                         pyplan, "cost_sel_scenario"),  # Helper for create options
            #                     value=pyplan.getResult(
            #                         "cost_sel_scenario").selected,
            #                     labelStyle={'display': 'inline-block',
            #                                 'marginRight': '10px'}
            #                 ),
            #             ], className="box"),

            #         html.Div(
            #             [
            #                 dcc.Upload(id="upload_model", children=html.Button(
            #                     'Upload Pyplan model file')),
            #                 html.Div(id='output_upload')

            #             ], className="box"),

            #     ], className="four columns"),

            # html.Div(
                # [
                #     html.Div(
                #         [
                #             dcc.Loading(
                #                 id="loading_operation_margin_report",
                #                 type="default",
                #                 children=html.Div(
                #                     [
                #                         dash_table.DataTable(
                #                             id='pl_table',
                #                             fixed_rows={
                #                                 "headers": True, "data": 0},
                #                             fixed_columns={
                #                                 "headers": True, "data": 1},
                #                             style_table={
                #                                 'width': '100%',
                #                             },
                #                             style_as_list_view=True,
                #                             column_selectable=False,
                #                             style_cell={'padding': '5px', 'fontSize': '11px',
                #                                         'fontFamily': 'Open Sans", HelveticaNeue, "Helvetica Neue", Helvetica, Arial, sans-serif'},
                #                             style_header={
                #                                 'backgroundColor': '#f2f2f2',
                #                                 'fontWeight': 'bold'
                #                             },
                #                             style_data_conditional=[
                #                                 {
                #                                     'if': {
                #                                         'filter_query': '{Report index} eq "Revenue" or {Report index} eq "Operation Margin" or {Report index} eq "EBITDA" or {Report index} eq "Net Income" or {Report index} eq "EBIT" or {Report index} eq "Profit b/tax"',
                #                                     },
                #                                     'backgroundColor': '#f6f6f6',
                #                                     'fontWeight': 'bold',
                #                                 },
                #                                 {
                #                                     'if': {'column_id': 'Report index'},
                #                                     'backgroundColor': '#f2f2f2',
                #                                     'textAlign': 'left'
                #                                 },
                #                             ],
                #                             data=[],
                #                         ),
                #                         dcc.Graph(
                #                             id="pl_chart",
                #                             figure={
                #                                 'data': [],
                #                                 'layout': {
                #                                     'height': 390
                #                                 }
                #                             }
                #                         )
                #                     ])
                #             )
                #         ], className="box"),
                # ], className="eight columns"),
        ], className="row"),
    html.Div(
        [
            html.Button('View source code', id="view_source_code", n_clicks=0),
        ], className="row view-source-code"),
    dcc.Markdown(id="source_code", className="markdown"),
    dcc.Markdown(id="ttt", className="markdown")

], className="container")

@app.callback(
    Output("ttt", "children"),
    [Input(component_id='connect_to_pyplan', component_property='n_clicks')]
)
def connect_to_pyplan(n_clicks):
    global pyplan
    if n_clicks >= 1 and pyplan is None:
        pyplan = Pyplan("http://localhost:8000")
        pyplan.login("super","Novix123!")   



# @app.callback(
#     [Output('pl_table', 'columns'), Output(
#         "pl_table", "data"), Output("pl_chart", "figure")],
#     [Input(component_id='time_selector', component_property='value'),
#      Input(component_id='discount_selector', component_property='value'),
#      Input(component_id='stock_policy_selector', component_property='value'),
#      Input(component_id='cost_sel_scenario', component_property='value')
#      ]
# )
# def selects_callback(time_value, discount_value, stock_value, cost_value):

#     # set values to Pyplan
#     pyplan.setSelectorValue("time_selector", time_value)
#     pyplan.setSelectorValue("discount_selector", discount_value)
#     pyplan.setSelectorValue("stock_policy_selector", stock_value)
#     pyplan.setSelectorValue("cost_sel_scenario", cost_value)

#     # get values from Pyplan
#     df = pyplan.getResult("dash_p_l_report")

#     # create columns for table
#     columns = []
#     for nn, col in enumerate(df.columns):
#         column_definition = {
#             "name": col,
#             "id": col,
#             "type": "text"
#         }
#         if nn > 0:
#             column_definition["type"] = "numeric"
#             column_definition["format"] = FormatTemplate.money(0)

#         columns.append(column_definition)

#     data = df.to_dict("records")

#     value_columns = [cc for nn, cc in enumerate(df.columns) if nn > 0]
#     df_chart = df.melt(id_vars=["Report index"], value_vars=value_columns)

#     # create chart
#     fig = None
#     if pyplan.getResult("time_group_selector").selected == 0:
#         fig = px.line(df_chart, x="time", y="value",
#                       color='Report index', color_discrete_sequence=default_colors)
#     else:
#         fig = px.bar(df_chart, x="time", y="value", color='Report index',
#                      barmode='group', color_discrete_sequence=default_colors)

#     default_layout(fig)
#     fig.update_layout(height=390, xaxis_type="category",
#                       title_text=f"P&L Report")

#     return columns, data, fig



@app.callback(
    Output("view_source_code", "children"),
    [Input(component_id='view_source_code', component_property='n_clicks')]
)
def view_source_code(n_clicks):
    if n_clicks > 0:
        return read_source_code(__file__)


# Main
if __name__ == "__main__":
    app.run_server(debug=True)
