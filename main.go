package main

import (
	"flag"
	"fmt"
	"log"
	"path/filepath"
	"strings"
	"time"

	"github.com/synw/ghobserver/activity"
	"github.com/synw/ghobserver/conf"
	"github.com/synw/ghobserver/db"
	"github.com/synw/ghobserver/exe"
	"github.com/synw/ghobserver/server"
	"github.com/synw/terr"
)

var initDb = flag.Bool("db", false, "Initialize the database and exit")
var httpServerOnly = flag.Bool("s", false, "Run the http server only")
var dev = flag.Bool("d", false, "Run in developement mode")
var noUpdate = flag.Bool("nu", false, "Do not update data from api")

func main() {
	flag.Parse()
	pypath, tr := exe.GetPath()
	if tr != nil {
		tr.Fatal()
	}
	staticPath := pypath + "/static"
	templatesPath := pypath + "/templates"
	localpath, _ := filepath.Abs("./")
	dbpath := localpath + "/ghobserver.db"
	db.Init(dbpath)
	username, pwd, apikey, repositories, externalRepositories, tr := conf.GetConf()
	if tr != nil {
		tr.Fatal()
	}
	// internal repos
	user := db.GetOrCreateUser(username)
	db.CheckRepos(repositories, user, dbpath, apikey)
	if *initDb == true {
		log.Print("Done")
		return
	}
	var exrep = make(map[string][]string)
	// get external repos
	for _, addr := range externalRepositories {
		li := strings.Split(addr, "/")
		u := li[0]
		rep := li[1]
		_, has := exrep[u]
		if has {
			exrep[u] = append(exrep[u], rep)
		} else {
			exrep[u] = []string{rep}
		}
	}
	// process external repos
	for u, reps := range exrep {
		exuser := db.GetOrCreateUser(u)
		db.CheckRepos(reps, exuser, dbpath, apikey)
	}
	// update loop
	if *httpServerOnly == false {
		go update(pypath, dbpath, apikey, *noUpdate, user, pwd, staticPath)
	}
	// http
	server.StartHttp(templatesPath, staticPath, *dev)
}

func update(pypath string, dbpath string, apikey string, noUpdate bool, user *db.User, pwd string, staticPath string) {
	for {
		if noUpdate == false {
			// update activity
			activity.Update(user, pwd, staticPath)
			// update repos
			log.Print("Updating commits data ...")
			msg, tr := exe.UpdateCommits(pypath, dbpath, apikey)
			if tr != nil {
				tr.Check()
			}
			if msg != "ok" {
				fmt.Println(msg)
			}
		}
		// run data pipeline
		updateList, tr := db.GetDashboardsToUpdate()
		if tr != nil {
			tr.Add("Can not get dashboards to udpate")
			tr.Fatal()
		}
		if len(updateList) == 0 {
			log.Print("Nothing changed")
		} else {
			// update dashboards
			var strli string
			for _, reponame := range updateList {
				strli = strli + " " + reponame
			}
			log.Print("Updating dashboard for" + strli)
			msg, tr := exe.RunPipeline(pypath, dbpath)
			if tr != nil {
				tr.Check()
			}
			if msg != "ok" {
				tr := terr.New("Error running the data pipeline:\n" + msg)
				tr.Fatal()
			}
			log.Print("Dashboard updated")
		}
		//}
		time.Sleep(10 * time.Minute)
	}
}
