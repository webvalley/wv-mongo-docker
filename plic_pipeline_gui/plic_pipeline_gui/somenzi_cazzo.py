# This file handles the graphs generation, mainly for the
# collection informations
# Copyright (c) 2019 Paolo Somenzi <paolo.somenzi@school.rainerum.it>
# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>
# Copyright (c) 2019 Stefano Fioravanzo <stefano.fioravanzo@gmail.com>

import pandas as pd
import numpy as np
from bokeh import plotting, embed
from bokeh.models import Range1d, ColumnDataSource, FactorRange, \
                            Grid, LinearAxis, Plot
from bokeh.models.glyphs import VBar
from bokeh.models import ColumnDataSource, Whisker
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral10
import os


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
        #score_classes_plot,
        boxplot_trajectories_rf,
        feature_randomforest_10classes,
        feature_randomforest_15classes
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
    p.yaxis.axis_label = "MCC"
    p.yaxis.axis_label_text_font_size = "25pt"
    p.xaxis.axis_label = "Trajectories"
    p.xaxis.axis_label_text_font_size = "25pt"

    return p


def feature_randomforest_10classes(*args):
    ROOT = "./plot_datasets"
    df_list = [pd.read_csv(os.path.join(ROOT, f'rf_score_traj_rankedVariables_{i}.txt'), sep='\t') for i in range(2,5)]
    df_list[0]['score_2'].to_frame()
    tmp = df_list[0].merge(df_list[1], left_index=True, right_index=True)
    for i in range(len(df_list)):
        tmp = tmp.merge(df_list[i],left_index=True, right_index=True)
    mean = tmp.mean(axis = 1)
    cols = df_list[0]
    idx = np.argsort(mean.values)[::-1]
    mean_df = pd.DataFrame({'feat':mean.index,'score':mean})
    mean_df['feat'][idx].values.tolist()
    source=ColumnDataSource(dict(feat=mean.index, score=mean.values))
    features = mean_df['feat'].values[idx[:7]].tolist()
    x = mean_df['score'].values[idx[:7]].tolist()
    dot = plotting.figure(title="", tools="", toolbar_location=None) #, y_range=features) #, x_range=range(0,300))
    dot.segment(0, features, x, features, line_width=4, line_color="green")
    dot.circle(x, features, size=15, fill_color="orange", line_color="green", line_width=3)

    return dot


def feature_randomforest_15classes(*args):
    ROOT = "./plot_datasets"
    df_list = [pd.read_csv(os.path.join(ROOT, f'rf_score_traj_rankedVariables_{i}.txt'), sep='\t') for i in range(2,16)]
    df_list[0]['score_2'].to_frame()
    tmp = df_list[0].merge(df_list[1], left_index=True, right_index=True)
    for i in range(2, 14):
        tmp = tmp.merge(df_list[i],left_index=True, right_index=True)
    mean = tmp.mean(axis = 1)
    cols = df_list[0]
    idx = np.argsort(mean.values)[::-1]
    mean_df = pd.DataFrame({'feat':mean.index,'score':mean})
    source = ColumnDataSource(dict(feat=mean.index, score=mean.values))
    features = ['General']
    data = {'diseases' : mean_df['feat'].values[idx[:7]].tolist(),
            'General'   : mean.values[idx[:7]].tolist()}
    print(data['diseases'], type(data['diseases']))
    p = plotting.figure(
        #x_range=[0,7],
        plot_width=800,
        plot_height=750,
        title="Deaths by cause, Male-Stack",
        toolbar_location=None,
        tools="hover",
        tooltips="$name @diseases: @$name"
    )

    p.vbar_stack(features, x='diseases', width=0.3, source=data,color='orange',
            alpha=0.5)
    return p
