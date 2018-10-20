import altair as alt


def heatmap(ds):
    ds.width(250)
    ds.height(110)
    ds.chart("Date:T", "Commits:Q")
    ds.aenc("color", "Commits:Q")
    c1 = ds.heatmap_()
    ds.raencs()
    ds.aenc("size", alt.Size('Commits:Q', legend=None))
    ds.zero_nan("Commits")
    ds.color("lime")
    c2 = ds.point_()
    c = c1 + c2
    return c.configure_axisX(titleFontSize=0)
