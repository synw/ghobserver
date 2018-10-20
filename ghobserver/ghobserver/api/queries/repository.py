def update_repository(slug, owner):
    q = """
    query {
      repository(owner:\"""" + owner + """\", name:\"""" + slug + """\") {
        createdAt
        url
        name
        description
        owner {
          login
          url
          avatarUrl
        }
        primaryLanguage {
          name
        }
        licenseInfo {
          name
        }
        releases {
          totalCount
        }
        collaborators(first:100) {
          totalCount
        }
        watchers(first:100) {
          totalCount
        }
        stargazers {
          totalCount
        }
        pushedAt
        updatedAt
        forkCount
        isFork
        diskUsage
        mentionableUsers (first:100) {
          totalCount
        }
        object(expression:"master") {
          ... on Commit {
            history {
              totalCount
            }
          }
        },
        issues {
            totalCount
        }
        pullRequests {
            totalCount
        }
        readme: object(expression: "master:README.md") {... on Blob {byteSize}}
      }
    }
    """
    return q
