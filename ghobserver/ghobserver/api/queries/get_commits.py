def get_commits(reponame, owner, num_per_page, cursor=None, since=None): 
    args = ""
    if cursor is not None:
        args = " after:" + '"' + cursor + '"'
    elif since is not None:
        args = " since:" + '"' + since + '"'
    q = """
    {
      repository(name: \"""" + reponame + """\", owner: \"""" + owner + """\") {
        updatedAt
        owner {
          login
        }
        ref(qualifiedName: "master") {
          target {
            ... on Commit {
              id
              history(first: """ + str(num_per_page) + args + """) {
                pageInfo {
                  startCursor
                  endCursor
                  hasNextPage
                }
                edges {
                  node {
                    id
                    oid
                    message
                    committedDate
                    url
                    committer {
                      user {
                          login
                      }
                    }
                    changedFiles
                    additions
                    deletions
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    return q
