def density(ds):
    ds.timestamps("Date")
    ds.chart("Timestamps", "Commits")
    ds.width(5)
    ds.height(3)
    c = ds.density_()
    return c