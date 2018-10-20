def timeline(ds):
    ds.chart("Date:T", "Commits:Q")
    ds.width(630)
    ds.height(150)
    ds.color("green")
    ds.raencs()
    c = ds.line_num_()
    ds.timestamps("Date")
    ds.drop_nan("Commits")
    ds.lreg("Timestamps", "Commits")
    ds.chart("Date:T", "Regression:Q")
    ds.color("grey")
    c1 = ds.line_(style=dict(opacity=0.4))
    c2 = c + c1
    c2 = c2.configure_axisX(titleFontSize=0)
    return c2