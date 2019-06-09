package exe

import (
	"github.com/synw/terr"
)

func RunPipeline(path string, dbpath string) (string, *terr.Trace) {
	// run the data pipeline
	cmd := "run pipeline"
	out, tr := Exec(cmd, path+"/pipeline.py", dbpath, "nodebug")
	if tr != nil {
		tr = tr.Add("Can not run data pipeline")
	}
	return out, tr
}

func GetPath() (string, *terr.Trace) {
	// get the base python path
	cmd := "get path"
	out, tr := Exec(cmd, "-m", "ghobserver.get_path")
	if tr != nil {
		tr = tr.Pass()
	}
	return out, tr
}

func UpdateRepo(reponame string, username string, dbpath string, apikey string) (string, *terr.Trace) {
	cmd := "update repo"
	args := []string{"-m", "ghobserver.update_repo", reponame, username, dbpath, apikey}
	out, tr := Exec(cmd, args...)
	if tr != nil {
		tr.Pass()
	}
	return out, tr
}

func UpdateCommits(path string, dbpath string, apikey string) (string, *terr.Trace) {
	// update all repositories commit history
	cmd := "update commits"
	args := []string{path + "/update_commits.py", dbpath, apikey, "no_debug"}
	out, tr := Exec(cmd, args...)
	if tr != nil {
		tr.Pass()
	}
	return out, tr
}
