import numpy as np
import altair as alt


def additions_deletions(ds):
    ds.chart("Date:T", "Changed files:Q")
    ds.width(630)
    ds.height(175)
    # line + text changed files
    ds.color("grey")
    ds.style("opacity", 0.5)
    line = ds.line_()
    ds.rstyle("opacity")
    ds.zero_nan("Changed files")
    ds.color("green")
    ds.aenc("text", "Changed files:Q")
    text = ds.text_()
    cx = line + text
    # addtitions deletions
    ds.rcolor()
    ds.chart("Date:T", "Additions:Q")
    c0 = ds.area_()
    ds.color("red")
    ds.chart("Date:T", "Deletions:Q")
    ds.df.Deletions = np.negative(ds.df.Deletions)
    c1 = ds.area_()
    c = c0 + c1
    chart = alt.layer(c, cx).resolve_scale(y='independent').configure_axis(
        grid=False).configure_axisX(titleFontSize=0)
    return chart
