package activity

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"strings"

	"github.com/mmcdole/gofeed"
	"github.com/synw/terr"

	"github.com/synw/ghobserver/db"
)

type feedUrl struct {
	Url string `json:"current_user_url"`
}

func getFeedUrl(username string, pwd string) string {
	client := &http.Client{}
	req, err := http.NewRequest("GET", "https://api.github.com/feeds", nil)
	req.SetBasicAuth(username, pwd)
	req.Header.Set("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	bytes, err := ioutil.ReadAll(resp.Body)
	var url feedUrl
	json.Unmarshal([]byte(bytes), &url)
	return url.Url
}

func checkFeedUrl(user *db.User, pwd string) *db.User {
	if user.FeedUrl == "" {
		url := getFeedUrl(user.Name, pwd)
		db.SaveFeedUrl(user, url)
		user.FeedUrl = url
	}
	return user
}

func Update(user *db.User, pwd string, staticPath string) {
	log.Print("Updating activity")
	user = checkFeedUrl(user, pwd)
	fp := gofeed.NewParser()
	feed, err := fp.ParseURL(user.FeedUrl)
	if err != nil {
		tr := terr.New(err)
		tr.Add("Can not parse activity feed")
		tr.Fatal()
	}
	var activities []db.Activity
	items := reverse(feed.Items)
	var users []*db.User
	for _, item := range items {
		eventType, eventId := getEventIdType(item.GUID)
		if userInSlice(user, users) == false {
			user := db.GetOrCreateUser(item.Author.Name)
			users = append(users, user)
		}
		activity := db.Activity{
			Title:     item.Title,
			Content:   item.Content,
			EventId:   eventId,
			EventType: eventType,
			Published: item.Published,
			Updated:   item.Updated,
			Author:    user.Id,
			Link:      item.Link,
		}
		activities = append(activities, activity)
	}
	db.SaveActivity(activities, staticPath)
}

func userInSlice(user *db.User, list []*db.User) bool {
	for _, u := range list {
		if u == user {
			return true
		}
	}
	return false
}

func getEventIdType(str string) (string, string) {
	sp := strings.Split(str, ",")
	str2 := strings.Split(sp[1], ":")[1]
	sp3 := strings.Split(str2, "/")
	eventType := sp3[0]
	eventId := sp3[1]
	return eventType, eventId
}

func reverse(it []*gofeed.Item) []*gofeed.Item {
	last := len(it) - 1
	for i := 0; i < len(it)/2; i++ {
		it[i], it[last-i] = it[last-i], it[i]
	}
	return it
}
