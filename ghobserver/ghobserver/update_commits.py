import sys
import arrow
from ghobserver import db, api
from ghobserver.update_repo import get_repo_data

FETCH_SLICE = 100
REPOS = {}
VERBOSE = True


def msg(*msg):
    global VERBOSE
    if VERBOSE is True:
        print(*msg)


def init_repo(repoid, reponame, owner, apikey):
    global FETCH_SLICE
    has_next_page = True
    end_cursor = None
    total = 0
    while has_next_page is True:
        # msg("Fetching " + str(FETCH_SLICE) + "records")
        if end_cursor is not None:
            last_update, records, has_next_page, end_cursor = api.get_commits(
                reponame, owner, apikey, FETCH_SLICE, end_cursor)
        else:
            last_update, records, has_next_page, end_cursor = api.get_commits(
                reponame, owner, apikey, FETCH_SLICE)
        i = len(records)
        msg("Fetched", i, "records, saving")
        db.save_commits(repoid, records)
        total = total + i
    msg("Saved", total, "commits for repository", reponame)
    return total, last_update


def get_start_date(date):
    arw = arrow.get(date)
    arw = arw.shift(seconds=+1)
    res = arw.format('YYYY-MM-DDTHH:mm:ss') + "Z"
    return res


def update_repo_commits(repoid, reponame, owner, date, message, apikey):
    global FETCH_SLICE
    msg("Updating repo", reponame + " from " + message + " " + str(date))
    has_next_page = True
    end_cursor = None
    total = 0
    while has_next_page is True:
        # msg("Fetching " + str(FETCH_SLICE) + "records")
        if end_cursor is not None:
            last_update, records, has_next_page, end_cursor = api.get_commits(
                reponame, owner, apikey, FETCH_SLICE, end_cursor)
        else:
            last_update, records, has_next_page, end_cursor = api.get_commits(
                reponame, owner, apikey, FETCH_SLICE, since=get_start_date(date))
        i = len(records)
        if i > 0:
            msg("Fetched", i, "records, saving")
            db.save_commits(repoid, records)
            total = total + i
    if total > 0:
        msg("Saved", total, "commits for repository", reponame)
    return total, last_update


def get_reponame(repoid):
    global REPOS
    for rep in REPOS:
        if rep["id"] == repoid:
            return rep["name"]


def run(dbpath, apikey):
    global REPOS
    db.init(dbpath)
    db.clean_results()
    REPOS = db.get_repos()
    last_commits = db.get_repos_update_info()
    res = {}
    for last_commit in last_commits:
        repoid = last_commit["repoid"]
        reponame = last_commit["reponame"]
        owner = last_commit["owner"]
        if last_commit["last_commit_date"] is None:
            msg("Initializing commits for repository " + reponame)
            res[repoid], last_update = init_repo(repoid, reponame, owner, apikey)
        else:
            res[repoid], last_update = update_repo_commits(repoid, reponame, owner,
                        last_commit["last_commit_date"],
                        last_commit["message"],
                        apikey
                        )
        # update repo info if needed
        if last_update != last_commit["last_update"]:
            msg("Updating repository info for " + reponame)
            data = get_repo_data(reponame, last_commit["owner"], apikey)
            db.save_repo_info(reponame, data)
    db.save_results(res)
    print("ok")
    

try:
    _ = sys.argv[3]
    v = False
except IndexError:
    v = True
VERBOSE = v
run(sys.argv[1], sys.argv[2])
