package db

type User struct {
	Id      int64
	Name    string `xorm:"varchar(120) not null unique index"`
	FeedUrl string
}

type Repository struct {
	Id                    int64
	Name                  string `xorm:"not null index"`
	Owner                 int64  `xorm:"not null"`
	CreatedAt             string
	UpdatedAt             string
	Description           string
	DiskUsage             int64
	IsFork                bool
	ForksCount            int64
	LicenseInfo           string
	CommitsCount          int64
	PrimaryLanguage       string
	PushedAt              string
	ReadmeSize            int64
	ReleasesCount         int64
	StarsCount            int64
	WatchersCount         int64
	IssuesCount           int64
	PullRequestsCount     int64
	MentionableUsersCount int64
	CollaboratorsCount    int64
}

type GhCommit struct {
	Id           int64
	Message      string
	Author       int64  `xorm:"not null"`
	Date         string `xorm:"not null"`
	Hash         string `xorm:"not null unique"`
	Url          string
	Repository   int64 `xorm:"not null"`
	ChangedFiles int64
	Additions    int64
	Deletions    int64
}

type Activity struct {
	Id        int64
	Title     string
	Content   string
	EventId   string `xorm:"not null unique"`
	EventType string
	Published string
	Updated   string
	Author    int64
	Link      string
}
