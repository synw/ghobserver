package main

import (
	"flag"
	"fmt"
	"log"
	"path/filepath"
	"time"

	"github.com/synw/terr"

	"github.com/synw/ghobserver/activity"
	"github.com/synw/ghobserver/conf"
	"github.com/synw/ghobserver/db"
	"github.com/synw/ghobserver/exe"
	"github.com/synw/ghobserver/server"
)

var initDb = flag.Bool("db", false, "Initialize the database and exit")
var httpServer = flag.Bool("s", false, "Run the http server only")
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
	username, pwd, apikey, repositories, tr := conf.GetConf()
	if tr != nil {
		tr.Fatal()
	}
	user := db.GetOrCreateUser(username)
	db.CheckRepos(repositories, user, dbpath, apikey)
	if *initDb == true {
		log.Print("Done")
		return
	}
	if *httpServer == false {
		go update(pypath, dbpath, apikey, *noUpdate, user, pwd, staticPath)
	}
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
		hasRes, tr := db.HasResults()
		if tr != nil {
			tr.Fatal()
		}
		if hasRes == false {
			log.Print("Nothing changed")
		} else {
			// run data pipeline
			var strli string
			updatelist := db.GetDashboardsToUpdate()
			for _, reponame := range updatelist {
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
		time.Sleep(10 * time.Minute)
	}
}
