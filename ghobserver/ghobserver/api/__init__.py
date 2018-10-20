import requests
from . import queries


def run_query(query, apikey, debug=False):
    if debug is True:
        print(query)
    headers = {"Authorization": "token " + apikey}
    request = requests.post('https://api.github.com/graphql',
                            json={'query': query}, headers=headers)
    if request.status_code == 200:
        data = request.json()
        if debug is True:
            print(data)
        return data
    else:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                str(request.status_code), query))


def get_commits(reponame, owner, apikey, num_per_page, cursor=None, since=None):
    query = queries.get_commits(reponame, owner, num_per_page, cursor, since)
    # print(query)
    data = run_query(query, apikey)
    # print(data)
    has_next_page = data["data"]["repository"]["ref"]["target"]["history"] \
        ["pageInfo"]["hasNextPage"]
    end_cursor = None
    if has_next_page is True:
        end_cursor = data["data"]["repository"]["ref"]["target"]["history"] \
            ["pageInfo"]["endCursor"]
    nodes = data["data"]["repository"]["ref"]["target"]["history"]["edges"]
    records = []
    for node in nodes:
        try:
            username = node["node"]["committer"]["user"]["login"]
        except:
            username = ""
        record = {"author": username,
                  "date": node["node"]["committedDate"],
                  "message": node["node"]["message"],
                  "url": node["node"]["url"],
                  "hash": node["node"]["oid"],
                  "repository": reponame,
                  "changed_files": node["node"]["changedFiles"],
                  "additions": node["node"]["additions"],
                  "deletions": node["node"]["deletions"]}
        records.append(record)
    last_update = data["data"]["repository"]["updatedAt"]
    return last_update, records, has_next_page, end_cursor
