package db

import (
	"log"

	"github.com/0xAX/notificator"
	"github.com/go-xorm/xorm"
	_ "github.com/mattn/go-sqlite3"
	"github.com/synw/terr"

	"github.com/synw/ghobserver/exe"
)

var engine *xorm.Engine

type Result struct {
	Id         int64
	RepoId     int64
	NumCommits int64
}

type ResultDetails struct {
	Commits  int64
	RepoName string
	Owner    string
}

func Init(dbpath string) {
	var err error
	engine, err = xorm.NewEngine("sqlite3", dbpath)
	if err != nil {
		tr := terr.New("Can not create database engine")
		tr.Fatal(err)
	}
	err = engine.Sync2(new(Repository))
	if err != nil {
		tr := terr.New("Can not sync repositories table")
		tr.Fatal(err)
	}
	err = engine.Sync2(new(GhCommit))
	if err != nil {
		tr := terr.New("Can not sync commits table")
		tr.Fatal(err)
	}
	err = engine.Sync2(new(User))
	if err != nil {
		tr := terr.New("Can not sync users table")
		tr.Fatal(err)
	}
	err = engine.Sync2(new(Result))
	if err != nil {
		tr := terr.New("Can not sync result table")
		tr.Fatal(err)
	}
	err = engine.Sync2(new(Activity))
	if err != nil {
		tr := terr.New("Can not sync activity table")
		tr.Fatal(err)
	}
}

func GetRepo(name string) (Repository, *terr.Trace) {
	var repo Repository
	has, err := engine.Where("name = ?", name).Desc("id").Get(&repo)
	if err != nil {
		tr := terr.New(err)
		return repo, tr
	}
	if has == false {
		tr := terr.New("Can not select repository")
		return repo, tr
	}
	return repo, nil
}

func GetRepos() ([]map[string]string, *terr.Trace) {
	res, err := engine.QueryString("SELECT * FROM repository ORDER BY name ASC")
	if err != nil {
		tr := terr.New(err)
		var r []map[string]string
		return r, tr
	}
	return res, nil
}

func GetOrCreateUser(username string) (*User, *terr.Trace) {
	user := &User{Name: username}
	has, err := engine.Exist(user)
	if err != nil {
		tr := terr.New(err, "Can not check if user "+username+" exists")
		return user, tr
	}
	if has == false {
		_, err = engine.Insert(user)
		if err != nil {
			tr := terr.New(err, "Can not insert user "+username)
			return user, tr
		}
	}
	has, err = engine.Where("name = ?", username).Get(user)
	if err != nil {
		tr := terr.New(err, "Can not select user "+username)
		return user, tr
	}
	if has == false {
		tr := terr.New("Can not select user " + username)
		return user, tr
	}

	return user, nil
}

func SaveFeedUrl(user *User, url string) {
	_, err := engine.ID(user.Id).Cols("feed_url").Update(&User{FeedUrl: url})
	if err != nil {
		tr := terr.New(err)
		tr = tr.Add("Can not update user " + user.Name)
		tr.Fatal(err.Error)
	}
}

func GetDashboardsToUpdate() ([]string, *terr.Trace) {
	results, err := engine.QueryString("SELECT repository.name FROM result JOIN repository ON result.repo_id = repository.id")
	var repos []string
	if err != nil {
		tr := terr.New("Can not select dashboards to update: " + err.Error())
		return repos, tr
	}
	for _, repo := range results {
		repos = append(repos, repo["name"])
	}
	return repos, nil
}

func GetActivity() []Activity {
	var acts []Activity
	err := engine.Desc("id").Limit(30, 0).Find(&acts)
	if err != nil {
		tr := terr.New(err, "Can not select last activity")
		tr.Fatal(err.Error)
	}
	return acts
}

func SaveActivity(activities []Activity, staticPath string) {
	// get last entries in database
	knownActs := GetActivity()
	// check which activities to save
	var acToSave []Activity
	for _, activity := range activities {
		if activityInSlice(activity, knownActs) == false {
			acToSave = append(acToSave, activity)
		}
	}
	// save
	if len(acToSave) == 0 {
		return
	}
	_, err := engine.Insert(&acToSave)
	if err != nil {
		tr := terr.New(err, "Can not save last activity")
		tr.Fatal(err.Error)
	}
	// notify
	iconPath := staticPath + "/img/notification.png"
	notify := notificator.New(notificator.Options{
		DefaultIcon: iconPath,
		AppName:     "Ghobserver",
	})
	title := "New activity on Github\n"
	text := ""
	for _, act := range acToSave {
		text = text + act.Title + "\n"
	}
	text = text + "\n<a href=\"http://localhost:8447\">See activity</a>"
	notify.Push(title, text, iconPath, notificator.UR_CRITICAL)
}

func activityInSlice(a Activity, list []Activity) bool {
	for _, aa := range list {
		if a.EventId == aa.EventId {
			return true
		}
	}
	return false
}

func getUser(username string) *User {
	var users []User
	err := engine.Where("name = ?", username).Find(&users)
	if err != nil {
		tr := terr.New(err, "Can not select user")
		tr.Check()
	}
	if len(users) > 0 {
		return &users[0]
	}
	u := new(User)
	return u
}

func CheckRepos(repos []string, user *User, dbpath string, apikey string) {
	for _, r := range repos {
		exists, tr := insertRepoIfNotExists(r, user.Id)
		if tr != nil {
			tr := tr.Add("Can not check insert repo " + r)
			tr.Fatal(tr.Error)
		}
		if exists == false {
			log.Print("Updating repository info for " + r)
			exe.UpdateRepo(r, user.Name, dbpath, apikey)
		}
	}
}

func insertRepoIfNotExists(reponame string, userid int64) (bool, *terr.Trace) {
	tr := &terr.Trace{}
	repo := &Repository{
		Name:  reponame,
		Owner: userid,
	}
	exists, err := engine.Exist(repo)
	if err != nil {
		tr = terr.New(err, "Can not check if repository "+reponame+" exists")
		return false, tr
	}
	if exists == false {
		_, err := engine.Insert(repo)
		if err != nil {
			tr = terr.New(err, "Can not insert repository "+reponame)
			return false, tr
		}
		log.Print("Repository " + reponame + " added")
	}
	return exists, nil
}
