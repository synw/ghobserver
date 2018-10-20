import sqlite3
import pandas as pd
from goerr import Err

err = Err()
DB = None


def init(dbpath):
    global DB
    DB = sqlite3.connect(dbpath)
    
    
def save_results(data):
    global DB
    try:

        def results_generator():
            for repoid in data:
                if data[repoid] > 0:
                    rec = (repoid, data[repoid])
                    yield rec
        
        c = DB.cursor()
        q = "INSERT INTO result(repo_id, num_commits) VALUES (?,?)"
        c.executemany(q, results_generator())
        DB.commit()
    except Exception as e:
        err.new(e)
        

def get_results():
    global DB
    try:
        c = DB.cursor()
        q = "select result.num_commits, repository.name from result "
        q += "join repository on result.repo_id = repository.id"
        c.execute(q)
        res = []
        for rec in c.fetchall():
            res.append(dict(name=rec[1], commits=rec[0]))
        return res
    except Exception as e:
        err.new(e)
        
        
def clean_results():
    global DB
    try:
        c = DB.cursor()
        q = "DELETE from result"
        c.execute(q)
        DB.commit()
    except Exception as e:
        err.new(e)
    
    
def save_repo_info(reponame, data):
    global DB
    c = DB.cursor()
    c.execute("SELECT id FROM repository WHERE name='" + reponame + "'")
    repoid = c.fetchall()[0][0]
    try:
        record = (data["createdAt"], data["updatedAt"], data["description"],
          str(data["diskUsage"]), data["isFork"], str(data["forkCount"]), data["license"],
          str(data["commitsCount"]), data["primaryLanguage"], data["pushedAt"],
          str(data["readmeSize"]), str(data["releases"]), str(data["stars"]), str(data["watchers"]),
          str(data["issues"]), str(data["pullRequests"]), str(data["mentionableUsers"]),
          str(data["collaborators"])                                                   
        )
        q = "UPDATE repository SET " + \
            "created_at = ?, updated_at = ?, description = ?, disk_usage = ?, is_fork = ?, forks_count = ?, " + \
            "license_info = ?, commits_count = ?, primary_language = ?, pushed_at = ?, " + \
            "readme_size = ?, releases_count = ?, stars_count = ?, watchers_count = ?, " + \
            "issues_count = ?, pull_requests_count = ?, mentionable_users_count = ?, " + \
            "collaborators_count = ? WHERE id = " + str(repoid)
        c.execute(q, record)
        DB.commit()
    except Exception as e:
        err.new(e)   

    
def save_commits(repoid, commits):
    global DB
    try:

        def commits_generator():
            for commit in commits:
                com = (commit["message"], commit["author"],
                        str(commit["date"]), commit["hash"], commit["url"], repoid,
                        commit["changed_files"], commit["additions"],
                        commit["deletions"])
                yield com
        
        c = DB.cursor()
        q = "INSERT INTO gh_commit(message, author, date, hash, url, " + \
            "repository, changed_files, additions, deletions) VALUES (?,?,?,?,?,?,?,?,?)"
        c.executemany(q, commits_generator())
        DB.commit()
    except Exception as e:
        err.new(e)


def get_commits(repoid):
    global DB
    q = 'SELECT * FROM gh_commit WHERE repository=' + str(repoid)
    df = pd.read_sql_query(q, DB)
    return df


def get_user(id):
    global DB
    c = DB.cursor()
    q = 'SELECT name FROM user WHERE id=' + str(id)
    c.execute(q)
    for rep in c.fetchall():
        return rep[0]

      
def get_repos():
    c = DB.cursor()
    c.execute('SELECT id, name FROM repository ORDER BY name ASC')
    repos = []
    for rep in c.fetchall():
        repo = dict()
        repo["id"] = rep[0]
        repo["name"] = rep[1]
        repos.append(repo)
    return repos


def get_repos_update_info():
    try:
        c = DB.cursor()
        c.execute('SELECT repository.id, repository.name, user.name AS owner, repository.updated_at'
                  ' FROM repository JOIN user ON repository.owner = user.id')
        repos = c.fetchall()
        update_info = []
        for repo in repos:
            repoid = repo[0]
            name = repo[1]
            owner = repo[2]
            last_update = repo[3]
            # print("Checking repository", name)
            q = "SELECT date, message FROM gh_commit WHERE repository=" + \
            str(repoid) + " ORDER BY date(date) DESC LIMIT 1"
            # print(q)
            c.execute(q)
            last_commit = c.fetchone()
            date = None
            msg = None
            if last_commit is not None:
                date = last_commit[0] 
                msg = last_commit[1] 
                lc = {"reponame": name, "last_commit_date": date, 'last_update': last_update,
                    "message": msg, "repoid": repoid, "owner":owner }
            else:
                lc = {"reponame": name, "last_commit_date": None, 'last_update': last_update,
                    "message": None, "repoid": repoid, "owner":owner}
            update_info.append(lc)
        return update_info
    except Exception as e:
        err.new(e)
    return update_info
