package server

import (
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gorilla/mux"
	wa "github.com/radovskyb/watcher"
	//"github.com/synw/terr"

	"github.com/synw/ghobserver/db"
)

var w = wa.New()
var tmpl *template.Template
var repos []Repo

type Repo struct {
	Slug string `json:slug`
	Name string `json:name`
	Url  string `json:url`
}

type PageData struct {
	Repos    []Repo
	Activity []db.Activity
}

func StartHttp(templatesPath string, staticPath string, dev bool) {
	repos = getRepos()
	ParseTemplates(templatesPath)
	c := make(chan bool)
	if dev == true {
		fmt.Println("Dev mode enabled")
		go watchTemplates(templatesPath, c)
		go func() {
			for {
				select {
				case <-c:
					ParseTemplates(templatesPath)
				}
			}
		}()
	}
	r := mux.NewRouter()
	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir(staticPath))))
	srv := &http.Server{
		Handler:      r,
		Addr:         "localhost:8447",
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}
	r.HandleFunc("/", serveIndex)
	r.HandleFunc("/repositories", serveIndex)
	r.HandleFunc("/repository/{slug}", serveIndex)
	r.HandleFunc("/api/repository/{slug}", serveRepo)
	log.Fatal(srv.ListenAndServe())
}

func serveIndex(w http.ResponseWriter, r *http.Request) {
	data := PageData{
		Repos:    repos,
		Activity: db.GetActivity(),
	}
	err := tmpl.ExecuteTemplate(w, "index.html", data)
	if err != nil {
		panic(err)
	}
}

func serveRepo(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	slug := vars["slug"]
	w.WriteHeader(http.StatusOK)
	w.Header().Set("Content-Type", "application/json")
	repo, tr := db.GetRepo(slug)
	if tr != nil {
		tr.Check()
	}
	json.NewEncoder(w).Encode(repo)
}

func getRepos() []Repo {
	repos, tr := db.GetRepos()
	r := []Repo{}
	if tr != nil {
		tr.Fatal()
		return r
	}
	for _, repo := range repos {
		slug := repo["name"]
		// get title
		name := strings.Title(strings.Replace(slug, "-", " ", -1))
		// store data
		rep := Repo{Slug: slug, Name: name, Url: slug}
		r = append(r, rep)
	}
	return r
}

func watchTemplates(templatesPath string, c chan bool) {
	err := w.AddRecursive(templatesPath)
	if err != nil {
		panic("Can not find templates path " + templatesPath)
	}
	w.FilterOps(wa.Write, wa.Create, wa.Move, wa.Remove, wa.Rename)
	// lauch listener
	go func() {
		for {
			select {
			case _ = <-w.Event:
				msg := "Reparsing templates"
				c <- true
				fmt.Println(msg)
			case err := <-w.Error:
				msg := "Watcher error " + err.Error()
				fmt.Println(msg)
			case <-w.Closed:
				msg := "Watcher closed"
				fmt.Println(msg)
				return
			}
		}
	}()
	fmt.Println("Watching " + templatesPath)
	// start listening
	err = w.Start(time.Millisecond * 200)
	if err != nil {
		panic("Error starting the watcher")
	}

}

func ParseTemplates(templatesPath string) {
	templ := template.New("")
	err := filepath.Walk(templatesPath, func(path string, info os.FileInfo, err error) error {
		if strings.Contains(path, ".html") {
			_, err = templ.ParseFiles(path)
			if err != nil {
				log.Println(err)
			}
		}
		return err
	})
	if err != nil {
		panic(err)
	}
	tmpl = templ
}
