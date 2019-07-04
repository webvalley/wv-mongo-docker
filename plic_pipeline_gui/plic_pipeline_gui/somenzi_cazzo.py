# This file handles the graphs generation, mainly for the
# collection informations
# Copyright (c) 2019 Paolo Somenzi <paolo.somenzi@school.rainerum.it>
# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>
# Copyright (c) 2019 Stefano Fioravanzo <stefano.fioravanzo@gmail.com>

import pandas as pd
from bokeh import plotting, embed
from bokeh.models import Range1d


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
