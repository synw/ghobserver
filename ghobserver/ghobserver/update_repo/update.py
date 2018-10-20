from ..api import run_query
from ..api.queries import update_repository


def get_repo_data(reponame, username, apikey):
    q = update_repository(reponame, username)
    data = run_query(q, apikey)
    res = {}
    res["owner"] = data["data"]["repository"]["owner"]["login"]
    res["updatedAt"] = data["data"]["repository"]["updatedAt"]
    res["createdAt"] = data["data"]["repository"]["createdAt"]
    res["description"] = data["data"]["repository"]["description"]
    res["isFork"] = data["data"]["repository"]["isFork"]
    res["forkCount"] = data["data"]["repository"]["forkCount"]
    res["diskUsage"] = data["data"]["repository"]["diskUsage"]
    try:
        res["license"] = data["data"]["repository"]["licenseInfo"]["name"]
    except TypeError:
        res["license"] = ""
    res["commitsCount"] = data["data"]["repository"]["object"]["history"]["totalCount"]
    res["url"] = data["data"]["repository"]["url"]
    res["primaryLanguage"] = data["data"]["repository"]["primaryLanguage"]["name"]
    res["pushedAt"] = data["data"]["repository"]["pushedAt"]
    try:
        res["readmeSize"] = data["data"]["repository"]["readme"]["byteSize"]
    except TypeError:
        res["readmeSize"] = 0
    res["releases"] = data["data"]["repository"]["releases"]["totalCount"]
    res["stars"] = data["data"]["repository"]["stargazers"]["totalCount"]
    res["watchers"] = data["data"]["repository"]["watchers"]["totalCount"]
    res["issues"] = data["data"]["repository"]["issues"]["totalCount"]
    res["pullRequests"] = data["data"]["repository"]["pullRequests"]["totalCount"]
    res["mentionableUsers"] = data["data"]["repository"]["mentionableUsers"]["totalCount"]
    res["collaborators"] = data["data"]["repository"]["collaborators"]["totalCount"]
    return res