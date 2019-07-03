# This file handles the graphs generation, mainly for the
# collection informations
# Copyright (c) 2019 Paolo Somenzi <paolo.somenzi@school.rainerum.it>
# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

from bokeh import plotting, embed


def example_graph1(patients):
    cats = ["< 1", "1 < x < 2", "2 < x < 5", "> 5"]
    vals = [0, 0, 0, 0]
    for patient in patients:
        if patient["score"] < 1:
            vals[0] += 1
        elif 1 <= patient["score"] < 2:
            vals[1] += 1
        elif 2 <= patient["score"] < 5:
            vals[2] += 1
        else:
            vals[3] += 1
    plot = plotting.figure(
        title="SCORE classes distribution",
        x_range=cats,
        toolbar_location=None,
        tools="",
        plot_width=400,
        plot_height=400
    )
    plot.vbar(x=cats, top=vals, width=0.9)
    return plot

def example_graph2(patients):
    cats = ["gatti", "cani", "giraffe"]
    vals = [100, 10, 60]
    plot = plotting.figure(
        title="Most liked animal",
        x_range=cats,
        toolbar_location=None,
        tools="",
        plot_width=400,
        plot_height=400
    )
    plot.vbar(x=cats, top=vals, width=0.9)
    return plot


def plot_for_each_variable(patients):
    vars = {
        var: [] for var in patients[0] if var != "_id" and type(patients[0][var]) in (int, float)
    }
    for pat in patients:
        for var in vars:
            vars[var].append(pat[var])
    plots = []
    for var in vars:
        plot = plotting.figure(
            title=var,
            plot_width=400,
            plot_height=400
        )
        plot.circle(list(range(len(vars[var]))), vars[var], size=10, color="navy", alpha=0.5)
        plots.append(plot)
    return plots


def collection_graphs(patients):
    f = [
        example_graph1,
        example_graph2
    ]
    plots = [
        x(patients) for x in f
    ] #+ plot_for_each_variable(patients)
    return plots


def patient_plots(visits):
    plot_cols = ["score", "lab:calculated_ldl"] + [
        x for x in visits[0] if "imt_cc_average" in x
    ]
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
            title=var,
            plot_width=250,
            plot_height=250
        )
        plot.circle(range(1,len(vals[var])+1), vals[var])
        plot.xaxis.ticker = list(range(1,len(vals[var])+1))
        plot.xgrid.visible = False
        plot.ygrid.visible = False
        plots.append(plot)
    return plots
