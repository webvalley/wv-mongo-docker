# This file handles the graphs generation, mainly for the
# collection informations
# Copyright (c) 2019 Paolo Somenzi <paolo.somenzi@school.rainerum.it>
# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>
# Copyright (c) 2019 Stefano Fioravanzo <stefano.fioravanzo@gmail.com>

import pandas as pd
from bokeh import plotting, embed
from bokeh.models import Range1d
from bokeh.models import ColumnDataSource, Whisker


_LABELS = {
    "score": "SCORE",
    "lab:calculated_ldl": "LDL",
    "ult_tsa:imt_cc_average_left": "IMT avg left",
    "ult_tsa:imt_cc_average_right": "IMT avg right",
}

units = {
    "score": "%",
    "lab:calculated_ldl": "mg/dL",
    "ult_tsa:imt_cc_average_left": "mm",
    "ult_tsa:imt_cc_average_right": "mm",
}


def score_classes_plot(patients):
    palette = ["#715F99", "#3867FF", "#FFCD78", "#CC7318"]
    cats = ["< 1", "1 < x < 2", "2 < x < 5", "> 5"]
    df = pd.DataFrame(patients)[["score"]]
    df["colors"] = None
    df.loc[df["score"]<1,["colors"]] = palette[0]
    df.loc[(df["score"]<2) & (df["score"]>=1),["colors"]] = palette[1]
    df.loc[(df["score"]<5) & (df["score"]>=2),["colors"]] = palette[1]
    df.loc[5<df["score"],["colors"]] = palette[3]
    plot = plotting.figure(
        title="SCORE classes distribution",
        x_range=cats,
        toolbar_location=None,
        tools="",
        plot_width=400,
        plot_height=400
    )
    plot.vbar(x=cats, top=df["score"], width=0.9)
    return plot


def collection_graphs(patients):
    f = [
        score_classes_plot,
        boxplot_trajectories_rf,
    ]
    plots = [
        x(patients) for x in f
    ] #+ plot_for_each_variable(patients)
    return plots


def patient_plots(visits, plot_cols, axes_limits):
    plots = []
    vals = {x: [] for x in plot_cols}
    for v in visits:
        for col in plot_cols:
            if col in v:
                vals[col].append(v[col])
            else:
                vals[col].append(None)
    for var in vals:
        plot = plotting.figure(
            title=var in _LABELS and _LABELS[var] or var,
            plot_width=250,
            plot_height=250
        )
        plot.line(range(1,len(vals[var])+1), vals[var], line_dash=[3, 5])
        plot.circle(range(1,len(vals[var])+1), vals[var])
        plot.xaxis.ticker = list(range(1,len(vals[var])+1))
        plot.xgrid.visible = False
        plot.ygrid.visible = False
        plot.xaxis.axis_label = "# visit"
        plot.yaxis.axis_label = var in units and units[var] or None
        plot.toolbar.logo = None
        plot.toolbar_location = None
        plot.y_range = Range1d(*axes_limits[var])
        plots.append(plot)
    return plots


def boxplot_trajectories_rf(*args):
    dataframe = pd.read_csv(
        "plot_datasets/rf_score_traj_results.tsv", 0, "\t"
    )
    source = ColumnDataSource(dataframe)

    tr_low = dataframe['mcc_tr_lower'].replace(',', '.').astype(float)
    tr_mean = dataframe['mcc_tr_mean'].replace(',', '.').astype(float)
    tr_high = dataframe['mcc_tr_upper'].replace(',', '.').astype(float)
    ts_low = dataframe['mcc_ts_lower'].replace(',', '.').astype(float)
    ts_mean = dataframe['mcc_ts_mean'].replace(',', '.').astype(float)
    ts_high = dataframe['mcc_ts_upper'].replace(',', '.').astype(float)

    list_traj = [item for item in range(2,17)]

    p = plotting.figure(tools="", background_fill_color="#efefef", toolbar_location=None)
    p.circle(list_traj, tr_mean, color='navy')
    p.add_layout(
        Whisker(source=source, base='traj_id', upper="mcc_tr_upper", lower="mcc_tr_lower", level="overlay")
    )
    p.circle(list_traj, ts_mean, color='red')
    p.add_layout(
        Whisker(source=source, base='traj_id', upper="mcc_ts_upper", lower="mcc_ts_lower", level="overlay")
    )
    p.yaxis.axis_label="MCC"
    p.yaxis.axis_label_text_font_size = "25pt"
    p.xaxis.axis_label="Trajectories"
    p.xaxis.axis_label_text_font_size = "25pt"

    return p
