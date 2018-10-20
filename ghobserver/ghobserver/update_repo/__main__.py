import sys
from .. import db
from .update import get_repo_data

if __name__ == "__main__":
    reponame = sys.argv[1]
    username = sys.argv[2]
    dbpath = sys.argv[3]
    apikey = sys.argv[4]
    data = get_repo_data(reponame, username, apikey)
    db.init(dbpath)
    db.save_repo_info(reponame, data)
    
