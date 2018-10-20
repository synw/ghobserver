package conf

import (
	"github.com/spf13/viper"
	"github.com/synw/terr"
)

func GetConf() (string, string, string, []string, *terr.Trace) {
	tr := &terr.Trace{}
	var r []string
	viper.SetConfigName("config")
	viper.AddConfigPath(".")
	err := viper.ReadInConfig()
	if err != nil {
		switch err.(type) {
		case viper.ConfigParseError:
			tr := terr.New(err)
			return "", "", "", r, tr
		default:
			tr := terr.New("Unable to locate config file")
			return "", "", "", r, tr
		}
	}
	user := viper.Get("user").(string)
	pwd := viper.Get("pwd").(string)
	token := viper.Get("token").(string)
	repos := viper.Get("repositories").([]interface{})
	for _, repo := range repos {
		r = append(r, repo.(string))
	}
	return user, pwd, token, r, tr
}
