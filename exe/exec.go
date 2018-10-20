package exe

import (
	"fmt"
	"os/exec"
	"strings"

	"github.com/synw/terr"
)

func Exec(cmdName string, cmdArgs ...string) (string, *terr.Trace) {
	// Execute a python script
	cmd := exec.Command("python3", cmdArgs...)
	out, err := cmd.CombinedOutput()
	if err != nil {
		errmsg := "Error executing command " + cmdName
		tr := terr.New(err, errmsg)
		return "", tr
	}
	msg := fmt.Sprintf("%s\n", out)
	msg = strings.Replace(string(out), "\n", "", -1)
	return msg, nil
}
