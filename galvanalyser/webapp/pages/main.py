import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from galvanalyser.webapp.pages import all_layouts
import dash_table

from galvanalyser.database.experiment.dataset_row import DatasetRow
from galvanalyser.database.experiment.range_label_row import RangeLabelRow
import galvanalyser.database.experiment.timeseries_data_column as TimeseriesDataColumn
from galvanalyser.database.experiment.timeseries_data_row import (
    TimeseriesDataRow,
    TEST_TIME_COLUMN_ID,
)
import psycopg2
from galvanalyser.webapp.datahandling import data_server
from galvanalyser_dash_components import GalvanalyserLegend
from galvanalyser.webapp.colours import (
    D3 as colours_D3,
    Light24 as colours_Light24,
)

# Reference for selection interaction https://dash.plot.ly/interactive-graphing
# Plotly python reference https://plot.ly/python/reference/
# Plotly js reference https://plot.ly/javascript/reference/
# and https://dash.plot.ly/dash-core-components
# also https://raw.githubusercontent.com/plotly/plotly.py/master/packages/python/plotly/plotly/graph_objs/__init__.py
# and https://github.com/plotly/dash-core-components/blob/dev/dash_core_components/Graph.py
# and https://github.com/plotly/dash-html-components/blob/master/dash_html_components/Div.py
def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")


dataset_selector = html.Div(
    [
        html.Button(
            id="main_get_dataset", type="button", children="Get Datasets"
        )
    ]
)
dataset_list = html.Div(
    [
        html.P("Dataset list"),
        dcc.RadioItems(id="main_dataset"),
        html.Form(
            children=[
                dash_table.DataTable(
                    id="dataset_table",
                    row_selectable="single",
                    columns=[
                        {"name": i, "id": i}
                        for i in ["id", "name", "date", "type"]
                    ],
                    # data=[{"hello":"aa","world":"bb","id":1}]
                )
            ]
        ),
    ]
)
data_ranges = html.Div(
    [
        html.P("Data ranges"),
        html.P(id="main_selected_dataset"),
        html.Form(
            children=[
                dash_table.DataTable(
                    id="metadata_table",
                    row_selectable="multi",
                    columns=[
                        {"name": i, "id": i}
                        for i in [
                            "label_name",
                            "column",
                            "samples_from",
                            "samples_to",
                            "info",
                            "user_created",
                        ]
                    ],
                    # data=[{"hello":"aa","world":"bb","id":1}]
                )
            ]
        ),
        html.Button(
            id="btn_add_data_range_to_plot",
            type="button",
            children="Plot Data Range",
        ),
    ]
)
range_editor = html.Div(
    children=[
        html.Button(
            id="btn_show_hide_range_editor",
            type="button",
            children="Show Range Editor",
        ),
        html.Div(
            id="range_editor", hidden=True, children=[html.P("Range Editor")]
        ),
    ]
)
plotting_controls = html.Div(
    [
        range_editor,
        html.Button(
            id="btn_set_reference_value_to_view",
            type="button",
            children="Set Reference Value to View",
        ),
    ]
)
tab_graph_content = html.Div(
    id="tab_graph_content",
    children=[
        dcc.Graph(
            id="main-graph",
            figure={"layout": {"clickmode": "event+select"}},
            config={
                "displaylogo": False,
                "responsive": True,
                "fillFrame": False,
                #'modeBarButtonsToAdd': [{'name':x }for x in ['select2d','lasso2d']]
            },
        ),
        html.Div(id="graph_update_dummy", hidden=True),
    ],
)

tab_dataset_content = html.Div(
    id="tab_dataset_content",
    children=[dataset_selector, dataset_list, data_ranges],
    hidden=True,
)

tab_legend_content = html.Div(
    id="tab_legend_content",
    children=[
        plotting_controls,
        GalvanalyserLegend(
            id="my-first-legend",
            graphId="main-graph",
            # entries=[{"foo":x} for x in ["foo", "bar", "spam", "eggs", "harry", "bear"]],
            label="my-label",
        ),
    ],
)

tab_export_content = html.Div(
    id="tab_export_content",
    children=[
        html.Div(
            children=[
                "Export format",
                dcc.RadioItems(
                    id="export-format-options",
                    options=[
                        {"label": "PNG", "value": "png"},
                        {"label": "SVG", "value": "svg"},
                        {"label": "JPG", "value": "jpg"},
                        {"label": "WEBP", "value": "webp"},
                    ],
                    value="png",
                ),
            ]
        ),
        html.Div(
            children=[
                "Width",
                dcc.Input(
                    id="export-width-input", type="number", value="1920"
                ),
            ]
        ),
        html.Div(
            children=[
                "Height",
                dcc.Input(
                    id="export-height-input", type="number", value="1080"
                ),
            ]
        ),
        html.Div(
            children=[
                "Scale",
                dcc.Input(id="export-scale-input", type="number", value="1.0"),
            ]
        ),
        html.Div(
            children=[
                "File name",
                dcc.Input(
                    id="export-filename-input",
                    placeholder="(without extension)",
                    type="text",
                    value="",
                ),
            ]
        ),
        html.Button(
            id="btn_export_image", type="button", children="Save Image"
        ),
        html.Div(id="export_plot_dummy", hidden=True),
    ],
    hidden=True,
)

main_tabs_container = html.Div(
    id="main_tabs_container",
    children=[
        dcc.Tabs(
            id="main_tabs",
            value="tab_graph",
            children=[
                dcc.Tab(label="Plotting", value="tab_graph"),
                dcc.Tab(label="Select Dataset", value="tab_dataset"),
            ],
        ),
        html.Div(
            id="main_tabs_content",
            children=[tab_graph_content, tab_dataset_content],
        ),
    ],
)

side_tabs_container = html.Div(
    id="side_tabs_container",
    children=[
        dcc.Tabs(
            id="side_tabs",
            value="tab_legend",
            children=[
                dcc.Tab(label="Legend", value="tab_legend"),
                dcc.Tab(label="Export", value="tab_export"),
            ],
        ),
        html.Div(
            id="side_tabs_content",
            children=[tab_legend_content, tab_export_content],
        ),
    ],
)


layout = html.Div(
    id="main_page_container",
    children=[main_tabs_container, side_tabs_container],
)

all_layouts.extend(
    [
        layout,
        tab_graph_content,
        tab_dataset_content,
        tab_legend_content,
        tab_export_content,
    ]
)


def register_callbacks(app, config):
    @app.callback(
        [
            Output("tab_graph_content", "hidden"),
            Output("tab_dataset_content", "hidden"),
        ],
        [Input("main_tabs", "value")],
    )
    def render_main_tabs_content(tab):
        if tab == "tab_graph":
            return False, True
        elif tab == "tab_dataset":
            return True, False

    @app.callback(
        [
            Output("tab_legend_content", "hidden"),
            Output("tab_export_content", "hidden"),
        ],
        [Input("side_tabs", "value")],
    )
    def render_main_tabs_content(tab):
        if tab == "tab_legend":
            return False, True
        elif tab == "tab_export":
            return True, False

    @app.callback(
        Output("dataset_table", "data"),
        [Input("main_get_dataset", "n_clicks")],
    )
    def get_dataset(n_clicks):
        log("in get_dataset")
        options = []
        if n_clicks:
            conn = None
            try:
                conn = config["get_db_connection_for_current_user"]()
                dataset = DatasetRow.select_all_dataset(conn)
                options = [
                    {
                        "id": exp.id,
                        "name": exp.name,
                        "date": exp.date,
                        "type": exp.dataset_type,
                    }
                    for exp in dataset
                ]
            finally:
                if conn:
                    conn.close()
        return options

    @app.callback(
        [
            Output("main_selected_dataset", "children"),
            Output("metadata_table", "data"),
            Output("metadata_table", "selected_rows"),
        ],
        [Input("dataset_table", "selected_row_ids")],
    )
    def dataset_selected(selected_row_ids):
        info_line = f"Selected: {selected_row_ids}"
        table_rows = []
        conn = None
        try:
            conn = config["get_db_connection_for_current_user"]()
            # populate columns properly, don't include "test_time"
            # available_columns = ["volts", "amps"]
            if selected_row_ids:
                selected_row_id = selected_row_ids[0]
                available_columns = TimeseriesDataColumn.select_experiment_columns(
                    selected_row_id, conn
                )
                try:
                    metadatas = RangeLabelRow.select_from_dataset_id(
                        selected_row_id, conn
                    )
                    table_rows = [
                        {
                            "id": f"{selected_row_id}:{m.id}:{col}:{m.label_name}",
                            "dataset_id": selected_row_id,
                            "label_name": m.label_name,
                            "column": col[1],
                            "column_id": col[0],
                            "samples_from": m.lower_bound,
                            "samples_to": m.upper_bound - 1,
                            "start_time": TimeseriesDataRow.select_from_dataset_id_column_id_and_sample_no(
                                selected_row_id,
                                TEST_TIME_COLUMN_ID,
                                m.lower_bound,
                                conn,
                            ).value,
                            "end_time": TimeseriesDataRow.select_from_dataset_id_column_id_and_sample_no(
                                selected_row_id,
                                TEST_TIME_COLUMN_ID,
                                m.upper_bound - 1,
                                conn,
                            ).value,
                            "info": m.info,
                            "user_created": m.user_created,
                            "offset": 0.0,
                            "colour": "#000000",
                        }
                        for m in metadatas
                        for col in available_columns
                    ]
                except psycopg2.errors.InsufficientPrivilege:
                    info_line = f"Permission denied when retrieving metadata for dataset id {selected_row_ids}"
        finally:
            if conn:
                conn.close()
        return info_line, table_rows, []

    @app.callback(
        [Output("my-first-legend", "requested_ranges")],
        [
            Input("btn_add_data_range_to_plot", "n_clicks"),
            Input("my-first-legend", "n_updated"),
        ],
        [
            State("metadata_table", "selected_rows"),
            State("metadata_table", "data"),
            State("my-first-legend", "requested_ranges"),
            State("main-graph", "relayoutData"),
        ],
    )
    def add_data_range_to_plot(
        add_n_clicks,
        legend_n_updated,
        metadata_selected_rows,
        metadata_table_rows,
        plotted_table_rows,
        graph_relayout_data,
    ):
        requested_ranges = (
            plotted_table_rows if plotted_table_rows is not None else []
        )
        current_range_ids = set(range["id"] for range in requested_ranges)
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if (
                button_id == "btn_add_data_range_to_plot"
                and add_n_clicks
                and metadata_selected_rows
            ):
                for row_idx in metadata_selected_rows:
                    if (
                        metadata_table_rows[row_idx]["id"]
                        not in current_range_ids
                    ):
                        requested_ranges.append(metadata_table_rows[row_idx])
        dataset_ids = sorted(
            list(set(row["dataset_id"] for row in requested_ranges))
        )
        dataset_columns = {id: set() for id in dataset_ids}
        for row in requested_ranges:
            dataset_columns[row["dataset_id"]].add(row["column_id"])
        total_plots = 0
        plot_colour_indices = {}
        for dataset_id in dataset_ids:
            dataset_columns[dataset_id] = sorted(
                list(dataset_columns[dataset_id])
            )
            for column_id in dataset_columns[dataset_id]:
                plot_colour_indices[(dataset_id, column_id)] = total_plots
                total_plots = total_plots + 1
        if total_plots < 10:
            colours = colours_D3
        else:
            colours = colours_Light24
        for row in requested_ranges:
            row["colour"] = colours[
                plot_colour_indices[(row["dataset_id"], row["column_id"])]
            ]
        return (requested_ranges,)

    @app.callback(
        [Output("my-first-legend", "reference_value")],
        [Input("btn_set_reference_value_to_view", "n_clicks")],
        [
            State("main-graph", "relayoutData"),
            State("my-first-legend", "reference_value"),
        ],
    )
    def set_reference_value_to_view(
        set_ref_n_clicks, graph_relayout_data, current_reference_value
    ):
        reference_value = current_reference_value
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if (
                button_id == "btn_set_reference_value_to_view"
                and set_ref_n_clicks
                and graph_relayout_data
            ):
                log(repr(graph_relayout_data))
                reference_value = graph_relayout_data.get(
                    "xaxis.range[0]", 0.0
                )
        return (reference_value,)

    app.clientside_callback(
        ClientsideFunction(
            namespace="plot_export", function_name="export_plot"
        ),
        [Output("export_plot_dummy", "children")],
        [Input("btn_export_image", "n_clicks")],
        [
            State("main-graph", "id"),
            State("export-format-options", "value"),
            State("export-width-input", "value"),
            State("export-height-input", "value"),
            State("export-scale-input", "value"),
            State("export-filename-input", "value"),
        ],
    )

    @app.callback(
        [
            Output("btn_show_hide_range_editor", "children"),
            Output("range_editor", "hidden"),
        ],
        [Input("btn_show_hide_range_editor", "n_clicks")],
        [State("range_editor", "hidden")],
    )
    def toggle_range_editor(n_clicks, editor_hidden):
        hide_editor = True
        if n_clicks:
            hide_editor = not editor_hidden
        button_label = (
            "Show Range Editor" if hide_editor else "Hide Range Editor"
        )
        return (button_label, hide_editor)

    data_server.register_handlers(app, config)
