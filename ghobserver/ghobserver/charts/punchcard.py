import altair as alt


def punchcard(ds):
    ds.engine = "altair"
    ds.rcolor()
    ds.width(550)
    ds.chart("Date:T", "Repository:N")
    ds.aenc("size", "Commits")
    c = ds.square_()
    return c.configure_axisX(titleFontSize=0)


def punchcard_repo(ds):
    ds.engine = "altair"
    ds.rcolor()
    ds.width(630)
    ds.height(15)
    ds.chart("Date:T", "Repository:N")
    ds.aenc("size", alt.Size('Commits', legend=None))
    c = ds.square_().configure_axis(
        titleColor="transparent", grid=False, tickSize=0,
        domain=False, labelFontSize=0).configure_view(strokeWidth=0)
    ds.raencs()
    return c
