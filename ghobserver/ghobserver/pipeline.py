# @PydevCodeAnalysisIgnore
import sys
import os
import arrow
import pandas as pd
from goerr import Err
from dataswim import DataSwim as Ds, DataSwim
import ghobserver
from ghobserver import db, charts
from ghobserver.notify import notify

err = Err()


def now():
    now = arrow.utcnow()
    date = now.format('YYYY-MM-DDTHH:mm:ss') + "Z"
    return date


def write_file(filepath, content):
    filex = open(filepath, "w")
    filex.write(content)
    filex.close()


def no_data(ds, reposlug, timeframe):
    filename = reposlug.replace("-", "_") + "_" + timeframe + ".html"
    filepath = ds.report_path + "/" + filename
    content = '<div style="font-family:arial;text-align:center;font-size:220%;color:lightgrey;margin-top:4em">'
    content += 'No data' 
    content += '</div>'
    ds.ok("Writing", filepath)
    write_file(filepath, content)
    # sidebar
    filename = reposlug.replace("-", "_") + "_" + timeframe + "_sidebar.html"
    content = ""
    filepath = ds.static_path + "/" + filename
    ds.ok("Writing", filepath)
    write_file(filepath, content)


def pipe_repo(ds, reposlug, timeframe, all_ds=None):
    ds.engine = "altair"
    # timeline
    if timeframe == "100Y":
        timeframe = "all"
    if reposlug is not None:
        slug = reposlug.replace("-", "_") + "_" + timeframe
    else:
        slug = "all_" + timeframe
    c = charts.timeline(ds)
    ds.stack(slug + "_chart_tl", c)
    if reposlug is not None:
        pc = charts.punchcard_repo(ds)
        ds.stack(slug + "_chart_pc", pc)
    else:
        pc = charts.punchcard(all_ds)
        ds.stack(slug + "_pc", pc)
    # addtitions deletions
    c = charts.additions_deletions(ds)
    ds.stack(slug + "_ad", c)
    # density
    # c = charts.density(ds)
    # ds.stack(slug + "_dens", c)
    # save to disk
    footer = "<style>div[id$='_chart_pc'] {margin:-1em 0 -1em 10px;}\n"
    footer = footer + "div[id$='_chart_tl'] {margin-top:-0.9em}</style>"
    ds.to_file(slug, footer=footer)
    # heatmap
    c = charts.heatmap(ds)
    ds.stack(slug + "_hm", c)
    # save to disk
    ds.to_file(slug + "_sidebar")
    return ds, slug


def get_results():
    res = db.get_results()
    repos = []
    for rec in res:
        repos.append(rec["name"])
    return res, repos


def pop_notification(results):
    msg = ""
    total = 0
    for rec in results:
        url = "http://localhost:8447/repository/" + rec["name"]
        msg += '<a href="' + url + '">' + rec["name"] + '</a> : ' + str(rec["commits"]) + ' new commits\n'
        total += rec["commits"]
    notify("New data from Github\n", msg)


def run(dbpath, debug=True):
    ds = Ds()
    if debug is True:
        ds.status("Debug mode is enabled")
    db.init(dbpath)
    results, modified_repos = get_results()
    if debug is False:
        ds.quiet = True
    db.init(dbpath)
    modulepath = os.path.dirname(os.path.realpath(
                                ghobserver.__file__))
    templates_path = modulepath + "/templates/charts"
    static_path = modulepath + "/static"
    repos = db.get_repos()
    ds.connect("sqlite:///" + dbpath)
    ds.load("gh_commit")
    ds.relation("repository", "repository", "name", "Repository")
    ds.rename("date", "Date")
    ds.rename("additions", "Additions")
    ds.rename("deletions", "Deletions")
    ds.rename("changed_files", "Changed files")
    ds.keep("Repository", "Date", "Additions", "Deletions", "Changed files")
    ds.date("Date")
    ds.dateindex("Date")
    ds.report_path = static_path + "/charts"
    ds.static_path = ds.report_path
    ds.backup()
    ts = [["3Y", "1M"], ["1Y", "1W"], ["3M", "1D"], ["3W", "1D"], ["1W", "1D"], ["100Y", "1M"]]
    # repos = [repos[0]]
    for tf in ts:
        timeframe = tf[0]
        timerange = tf[1]
        ds.restore()
        # all repos
        slug = "all"
        # ds.append(["", now(), 0, 0, 0])
        ds.df.Date = pd.to_datetime(ds.df.Date)
        ds.dateindex("Date")
        ds.nowrange("Date", timeframe)
        if len(ds.df.index) < 2:
            no_data(ds, slug, timeframe)
            ds.status("No data for all repositories", timeframe)
        else:
            # add repositories names to the rsumed dataset
            res = []
            dss = ds.split_("Repository")
            for k in dss:
                d = dss[k]
                repo = d.df["Repository"].values[0]
                d.rsum(timerange, "Commits")
                d.add("Repository", repo)
                res.append(d)
            ds2 = DataSwim().concat_(*res)
            ds.rsum(timerange, "Commits")
            ds.df.iloc[[-1], [3]] = 0
            pipe_repo(ds, None, timeframe, ds2)
        # by repos
        for repo in repos:
            reposlug = repo["name"]
            if debug is False:
                if reposlug not in modified_repos:
                    continue
            ds.restore()
            ds.append([reposlug, now(), 0, 0, 0])
            ds.df.Date = pd.to_datetime(ds.df.Date)
            ds.dateindex("Date")
            ds.exact("Repository", reposlug)
            ds.nowrange("Date", timeframe)
            if len(ds.df.index) < 2:
                no_data(ds, reposlug, timeframe)
                ds.status("No data for", reposlug, timeframe)
                continue
            ds.rsum(timerange, "Commits")
            ds.df.iloc[[-1], [3]] = 0
            ds, slug = pipe_repo(ds, repo["name"], timeframe)
    pop_notification(results)
    db.clean_results()
    print("ok")


if len(sys.argv) == 2:
    run(sys.argv[1])
else:
    run(sys.argv[1], False)
